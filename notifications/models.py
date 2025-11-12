from django.db import models
from django.conf import settings

class Notification(models.Model):
    """
    Simple notification system for StudyBud. 
    Create records whenever users create rooms or other actions.
    """
    ROOM_CREATED = 'room_created'
    MESSAGE_RECEIVED = 'message_received'
    TOPIC_FOLLOWED = 'topic_followed'

    NOTIFICATION_TYPES = [
        (ROOM_CREATED, 'Room Created'),
        (MESSAGE_RECEIVED, 'Message Received'),
        (TOPIC_FOLLOWED, 'Topic Followed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.created_at:%Y-%m-%d %H:%M:%S}"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
