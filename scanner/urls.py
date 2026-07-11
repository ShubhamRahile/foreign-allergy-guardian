from django.urls import path
from .views import DashboardView, ScanView, ScanResultView, OCRScanView, HistoryListView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('scan/', ScanView.as_view(), name='scan'),
    path('scan/result/<str:barcode>/', ScanResultView.as_view(), name='scan_result'),
    path('scan/ocr/', OCRScanView.as_view(), name='ocr_scan'),
    path('history/', HistoryListView.as_view(), name='history'),
]
