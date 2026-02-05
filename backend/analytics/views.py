import os
from django.shortcuts import render
from django.http import FileResponse
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Dataset
from .serializers import DatasetSerializer, UserSerializer
from .utils import analyze_csv, generate_pdf_report, validate_csv


@api_view(['POST'])
def login_view(request):
    """Basic authentication endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_staff or user.is_superuser,
        'message': 'Login successful'
    })


@api_view(['POST'])
def register_view(request):
    """User registration endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_staff or user.is_superuser,
        'message': 'Registration successful'
    }, status=status.HTTP_201_CREATED)


class DatasetViewSet(viewsets.ModelViewSet):
    serializer_class = DatasetSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return datasets for the current user, or all datasets for admins"""
        base_queryset = Dataset.objects.all().order_by('-uploaded_at')
        if self.request.user.is_staff or self.request.user.is_superuser:
            return base_queryset
        return base_queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associate the created dataset with the current user and keep only last 5"""
        serializer.save(user=self.request.user)
        
        # Keep only the last 5 datasets for this user
        user_datasets = Dataset.objects.filter(user=self.request.user).order_by('-uploaded_at')
        if user_datasets.count() > 5:
            # Delete the oldest datasets (those beyond the 5 most recent)
            datasets_to_delete = user_datasets[5:]
            for dataset in datasets_to_delete:
                # Delete the file if it exists
                if dataset.file:
                    dataset.file.delete()
                dataset.delete()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance

        try:
            analyze_csv(instance.file.path)
        except ValueError as exc:
            if instance.file:
                instance.file.delete()
            instance.delete()
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_destroy(self, instance):
        if instance.file:
            instance.file.delete()
        instance.delete()

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        dataset = self.get_object()
        file_path = dataset.file.path

        if not os.path.exists(file_path):
            return Response({'error': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            analysis = analyze_csv(file_path)
            return Response(analysis)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download dataset analysis as PDF"""
        dataset = self.get_object()
        file_path = dataset.file.path

        if not os.path.exists(file_path):
            return Response({'error': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            analysis = analyze_csv(file_path)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        pdf_buffer = generate_pdf_report(analysis, dataset.id)
        
        response = FileResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="dataset_{dataset.id}_report.pdf"'
        return response

    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        dataset = self.get_object()
        file_path = dataset.file.path

        if not os.path.exists(file_path):
            return Response({'error': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            df = validate_csv(file_path)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        name_column = None
        for candidate in ["Equipment", "Equipment Name", "Name"]:
            if candidate in df.columns:
                name_column = candidate
                break

        equipment_type = request.query_params.get('type')
        name_query = request.query_params.get('name')
        pressure_min = request.query_params.get('pressure_min')
        pressure_max = request.query_params.get('pressure_max')
        temperature_min = request.query_params.get('temperature_min')
        temperature_max = request.query_params.get('temperature_max')

        filtered = df.copy()

        if equipment_type:
            filtered = filtered[filtered["Type"] == equipment_type]

        if name_query:
            if not name_column:
                return Response(
                    {'error': "Missing equipment name column (expected 'Equipment', 'Equipment Name', or 'Name')."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            filtered = filtered[filtered[name_column].astype(str).str.contains(name_query, case=False, na=False)]

        if pressure_min:
            try:
                filtered = filtered[filtered["Pressure"] >= float(pressure_min)]
            except ValueError:
                return Response({'error': "Invalid pressure_min value."}, status=status.HTTP_400_BAD_REQUEST)

        if pressure_max:
            try:
                filtered = filtered[filtered["Pressure"] <= float(pressure_max)]
            except ValueError:
                return Response({'error': "Invalid pressure_max value."}, status=status.HTTP_400_BAD_REQUEST)

        if temperature_min:
            try:
                filtered = filtered[filtered["Temperature"] >= float(temperature_min)]
            except ValueError:
                return Response({'error': "Invalid temperature_min value."}, status=status.HTTP_400_BAD_REQUEST)

        if temperature_max:
            try:
                filtered = filtered[filtered["Temperature"] <= float(temperature_max)]
            except ValueError:
                return Response({'error': "Invalid temperature_max value."}, status=status.HTTP_400_BAD_REQUEST)

        records = []
        for _, row in filtered.iterrows():
            record = {
                "type": row["Type"],
                "flowrate": row["Flowrate"],
                "pressure": row["Pressure"],
                "temperature": row["Temperature"],
            }
            if name_column:
                record["name"] = row[name_column]
            records.append(record)

        response_payload = {
            "records": records,
            "total": len(filtered),
            "available_types": sorted(df["Type"].dropna().astype(str).unique().tolist()),
            "pressure_range": {
                "min": float(df["Pressure"].min()),
                "max": float(df["Pressure"].max()),
            },
            "temperature_range": {
                "min": float(df["Temperature"].min()),
                "max": float(df["Temperature"].max()),
            },
            "name_supported": name_column is not None,
        }

        return Response(response_payload)


class AdminUserViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.all().order_by('username')

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {'error': 'Admins cannot delete their own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_datasets = Dataset.objects.filter(user=user)
        for dataset in user_datasets:
            if dataset.file:
                dataset.file.delete()
            dataset.delete()
        return super().destroy(request, *args, **kwargs)
