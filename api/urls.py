from django.urls import path
from .views import RegisterAPIView, LoginAPIView, ProfileAPIView, ScanAPIView, HistoryAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('profile/', ProfileAPIView.as_view(), name='api_profile'),
    path('scan/', ScanAPIView.as_view(), name='api_scan'),
    path('history/', HistoryAPIView.as_view(), name='api_history'),
]
