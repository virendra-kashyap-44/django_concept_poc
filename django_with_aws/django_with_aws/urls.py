from django.urls import path
from .views import get_presigned_urls, upload_complete

urlpatterns = [
    path('api/presigned-urls/', get_presigned_urls),
    path('api/upload-complete/', upload_complete),
]