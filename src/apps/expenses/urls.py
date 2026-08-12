from django.urls import path
from .views import DownloadBillPDFView

app_name = 'expenses'

urlpatterns = [
    path('bill/<int:pk>/pdf/', DownloadBillPDFView.as_view(), name='download_bill_pdf'),
]