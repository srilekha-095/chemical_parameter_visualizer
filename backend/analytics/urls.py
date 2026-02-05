from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import DatasetViewSet, AdminUserViewSet, login_view, register_view

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
] + router.urls
