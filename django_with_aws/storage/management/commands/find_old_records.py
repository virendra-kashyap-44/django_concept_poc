import pika
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from storage.models import PresignedBucket
from datetime import timedelta

class Command(BaseCommand):
    help = 'Finds records and pushes them to RabbitMQ'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        cutoff_time = now - timedelta(hours=6)
        records = PresignedBucket.objects.filter(
            created_at__gte=cutoff_time,
            created_at__lte=now,
            status__in=['pending', 'failed']
        )

        # RabbitMQ connection setup
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))  # ya aapka RabbitMQ host
        channel = connection.channel()

        # Declare queue
        channel.queue_declare(queue='presignedbucket_queue', durable=True)

        self.stdout.write(self.style.SUCCESS(f'Found {records.count()} records created within last 6 hours!'))

        for record in records:
            message = {
                'request_id': record.request_id,
                'status': record.status,
                'created_at': record.created_at.isoformat(),
                'files': record.files
            }
            channel.basic_publish(
                exchange='',
                routing_key='presignedbucket_queue',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            self.stdout.write(f'Sent to RabbitMQ: {message}')

        connection.close()
        self.stdout.write(self.style.SUCCESS('All records have been sent to RabbitMQ!'))
# This command finds records in the PresignedBucket model created within the last 6 hours  