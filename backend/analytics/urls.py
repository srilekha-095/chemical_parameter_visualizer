from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import DatasetViewSet, login_view, register_view

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')

urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
] + router.urls