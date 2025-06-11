import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import boto3
import json
import uuid
import time

from .models import PresignedBucket

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

        cookie_header = request.headers.get('Cookie', 'OauthHMAC=NzlkZGIwYjRkZmVmNDlmYWJjYTJhNWIwYzMzN2M2MGExMGU0YTMwNjI1YTRlNTNmMmIwYjFlNmEzZmFjMzg4Ng==; OauthExpires=1749722639; BearerToken=eyJhbGciOiJSUzI1NiIsImtpZCI6Ilg1ZVhrNHh5b2pORnVtMWtsMll0djhkbE5QNC1jNTdkTzZRR1RWQndhTmsiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJlNmMwOWRlZC00NmY0LTQzZWItYmVmZC1mZTcyMDQ1ZDk1MDYiLCJpc3MiOiJodHRwczovL2Rldm5ld2JyaWRnZWZpbnRlY2guYjJjbG9naW4uY29tL2M1YzAzYTM4LTlkZDItNDdkYS04YzA4LTY2ZGQ0ZTk4OWExMy92Mi4wLyIsImV4cCI6MTc0OTcyMjYzOSwibmJmIjoxNzQ5NjM2MjM5LCJvaWQiOiI2YjQwMzZjZi0zOGQ5LTRkNGQtYWVlYS0xNWUzYzU3NjkzOTEiLCJzdWIiOiI2YjQwMzZjZi0zOGQ5LTRkNGQtYWVlYS0xNWUzYzU3NjkzOTEiLCJuYW1lIjoiUGF0cmljayBicmFuZWxpIiwiZ2l2ZW5fbmFtZSI6IlBhdHJpY2siLCJqb2JUaXRsZSI6IlRyYWRlciIsImZhbWlseV9uYW1lIjoiYnJhbmVsaSIsImV4dGVuc2lvbl9tYXJrZXRQYXJ0aWNpcGFudElkIjoiOTY0MzE5ZWEtZTk0YS00YzRhLTk3YWQtNmU4MmNjNTEyZTVlIiwiZXh0ZW5zaW9uX2lzX3JlZ2lzdGVyZWQiOnRydWUsImV4dGVuc2lvbl9pc01QTGl2ZSI6dHJ1ZSwiZXh0ZW5zaW9uX3JlYWxtUm9sZXMiOiJBUFBST1ZFUixBRE1JTklTVFJBVE9SIiwiZXh0ZW5zaW9uX29sZFVzZXJJZCI6IjJjNGJiMWJlLTdkY2YtNGRhYy04N2JmLTI1ZDcxODlhZWVhZSIsImVtYWlscyI6WyJicmFuZWxpQGFsY2VudHJhLmNvbSJdLCJ0ZnAiOiJCMkNfMV9TaWduSW4iLCJhenAiOiJlNmMwOWRlZC00NmY0LTQzZWItYmVmZC1mZTcyMDQ1ZDk1MDYiLCJ2ZXIiOiIxLjAiLCJpYXQiOjE3NDk2MzYyMzl9.ZF6PWwVeLPXPlZx98Rd_YBtd_mzKTZt_u1L11-znaA6bR_xqEuwc51wowLuCavdnlx_K-s6u5xT6V6QT0hvi6VjRWz09fxa6-IfDKAfPUqkFvW9kIXkH7vd1iu_279LSNwFqicgvnbCn8CFtrdjVW3dYL6qP-mUx2xJQG9VHV_Q46B3poH70_DD22l0tsmQ-QQqbisd-wG8qSmFD12BX3pfNIpasgZI8qu2aj9ciK28081YV0M41_-BOAw2nO51uJTE-riMtCsMCzMN-SoM-vgQ-CXUnPHHM3j3Lvrzen7j2gVb_lZFpCTGJscFd_Ly9fjqNogX3HZJemNTyZEIaag')
        if not cookie_header:
            return JsonResponse({'error': 'Missing Cookie header'}, status=401)

        profile_url = 'https://sit.loan-book.com/api/v1/profiles/my'
        headers = {'Cookie': cookie_header}

        user_id = ''
        success = False

        # for attempt in range(3):
        #     try:
        #         # 👇 ye line hamesha error throw kar degi
        #         raise Exception("Intentional error for testing!")
                
        #         profile_response = requests.get(profile_url, headers=headers, timeout=5)
        #         if profile_response.status_code == 200:
        #             profile_data = profile_response.json()
        #             user_id = profile_data.get('data', {}).get('user_id', '')
        #             if user_id:
        #                 success = True
        #                 break
        #         else:
        #             time.sleep(1)  # Small delay between retries
        #     except Exception as e:
        #         print(f"Attempt {attempt+1}: {e}")  # Log for debugging
        #         time.sleep(1)

        # 🔁 Retry logic
        for attempt in range(3):
            try:
                profile_response = requests.get(profile_url, headers=headers, timeout=5)
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"Attempt {attempt+1}: Profile data fetched successfully")  # Log for debuggingp
                    print(f"Profile data: {profile_data}")  # Log for debugging
                    user_id = profile_data.get('data', {}).get('user_id', '')
                    if user_id:
                        success = True
                        break
                else:
                    time.sleep(1)  # Small delay between retries
            except Exception:
                time.sleep(1)

        request_id = str(uuid.uuid4())
        entry = PresignedBucket(
            request_id=request_id,
            status='pending',
            user_id=user_id if success else None,
            files=file_names
        )
        entry.save()

        if not success:
            # ✅ If failed after 3 attempts, update status to failed
            entry.status = 'failed'
            entry.save()
            return JsonResponse({'error': 'Failed to fetch user profile after 3 attempts'}, status=500)

        urls = []
        for name in file_names:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': name},
                ExpiresIn=900
            )
            urls.append({'fileName': name, 'url': presigned_url})

        return JsonResponse({
            'requestId': request_id,
            'urls': urls
        })

    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def upload_complete(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request_id = data.get('requestId')

        try:
            entry = PresignedBucket.objects.get(request_id=request_id)
            entry.status = 'completed'
            entry.save()
            return JsonResponse({'status': 'success', 'requestId': request_id})
        except PresignedBucket.DoesNotExist:
            return JsonResponse({'error': 'Invalid requestId'}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)