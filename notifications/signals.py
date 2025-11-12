from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification

# Try to import Room from base app; if not present, skip the signal
try:
    from base.models import Room
except ImportError:
    Room = None

User = get_user_model()

if Room:
    @receiver(post_save, sender=Room)
    def notify_room_created(sender, instance, created, **kwargs):
        """When a room is created, notify all users except the host."""
        if not created:
            return
        users_to_notify = User.objects.all()[:10]  # demo: limit to first 10
        Notification.objects.bulk_create([
            Notification(
                user=u,
                notification_type=Notification.ROOM_CREATED,
                message=f"New room  \
                          Name: '{instance.name}' created in Topic: {instance.topic.name}",
                link=f"/room/{instance.id}/",
            ) for u in users_to_notify
        ])
