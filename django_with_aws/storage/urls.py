from django.urls import path
from . import views

urlpatterns = [
    path('get-presigned-urls/', views.get_presigned_urls, name='get_presigned_urls'),
    path('upload-complete/', views.upload_complete, name='upload_complete'),
]