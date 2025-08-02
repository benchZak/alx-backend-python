from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .managers import UnreadMessagesManager

User = get_user_model()

class Message(models.Model):
    # Standard manager
    objects = models.Manager()
    
    # Custom manager for unread messages
    unread = UnreadMessagesManager()

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('sender')
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('receiver')
    )
    content = models.TextField(verbose_name=_('content'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('sent at'))
    is_read = models.BooleanField(default=False, verbose_name=_('is read'))

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['receiver', 'is_read']),
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Message #{self.id} from {self.sender} to {self.receiver}"

    def mark_as_read(self):
        """Mark the message as read and save."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
