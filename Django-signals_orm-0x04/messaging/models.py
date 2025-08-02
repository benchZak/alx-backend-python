from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .managers import UnreadMessagesManager

User = get_user_model()

class Message(models.Model):
    objects = models.Manager()
    unread = UnreadMessagesManager()

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['receiver', 'is_read']),
        ]

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"
