import os
from django.shortcuts import render
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Dataset
from .serializers import DatasetSerializer
from .utils import analyze_csv, generate_pdf_report


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
        'message': 'Registration successful'
    }, status=status.HTTP_201_CREATED)


class DatasetViewSet(viewsets.ModelViewSet):
    serializer_class = DatasetSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return datasets only for the current authenticated user"""
        return Dataset.objects.filter(user=self.request.user).order_by('-uploaded_at')
    
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

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        dataset = self.get_object()
        file_path = dataset.file.path

        if not os.path.exists(file_path):
            return Response({'error': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

        analysis = analyze_csv(file_path)
        return Response(analysis)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download dataset analysis as PDF"""
        dataset = self.get_object()
        file_path = dataset.file.path

        if not os.path.exists(file_path):
            return Response({'error': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

        analysis = analyze_csv(file_path)
        pdf_buffer = generate_pdf_report(analysis, dataset.id)
        
        response = FileResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="dataset_{dataset.id}_report.pdf"'
        return response