from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import boto3
import json
import uuid

s3_client = boto3.client(
    's3',
    region_name=settings.AWS_S3_REGION_NAME,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

@csrf_exempt
def get_presigned_urls(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        file_names = body.get('files', [])

        request_id = str(uuid.uuid4())  # generate unique tracing ID

        urls = []
        for name in file_names:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': name},
                ExpiresIn=900
            )
            urls.append({'fileName': name, 'url': presigned_url})

        return JsonResponse({'requestId': request_id, 'urls': urls})
    
@csrf_exempt
def upload_complete(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request_id = data.get('requestId')
        uploaded_files = data.get('files', [])

        # Optional: Save metadata to DB or logs
        print(f"[UPLOAD COMPLETE] Request ID: {request_id}")
        print(f"Uploaded files: {uploaded_files}")

        return JsonResponse({'status': 'success', 'requestId': request_id})
    return JsonResponse({'error': 'Invalid method'}, status=405)