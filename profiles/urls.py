from django.urls import path
from .views import ProfileView, AllergyCardPDFView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('pdf/', AllergyCardPDFView.as_view(), name='profile_pdf'),
]
