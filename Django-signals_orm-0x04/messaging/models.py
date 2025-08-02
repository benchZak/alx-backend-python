from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Message(models.Model):
    """
    Represents a message in a threaded conversation system.
    """
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
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        verbose_name=_('parent message'),
        help_text=_('The message this is a reply to')
    )
    content = models.TextField(verbose_name=_('content'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('sent at'))
    is_read = models.BooleanField(default=False, verbose_name=_('is read'))
    edited = models.BooleanField(default=False, verbose_name=_('edited'))
    last_edited = models.DateTimeField(null=True, blank=True, verbose_name=_('last edited at'))

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['parent_message']),
            models.Index(fields=['is_read']),
            models.Index(fields=['edited']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(sender=models.F('receiver')),
                name='no_self_messages'
            ),
            models.CheckConstraint(
                check=~models.Q(id=models.F('parent_message')),
                name='no_self_replies'
            )
        ]

    def __str__(self):
        return _('Message #{id} from {sender} to {receiver}').format(
            id=self.id,
            sender=self.sender,
            receiver=self.receiver
        )

    def clean(self):
        """Validate message relationships."""
        if self.sender == self.receiver:
            raise ValidationError(_('Users cannot send messages to themselves.'))
        
        if self.parent_message and self.parent_message.parent_message:
            raise ValidationError(_('Cannot reply to a reply. Please reply to the original message.'))
        
        if self.parent_message and self.parent_message.receiver != self.sender:
            raise ValidationError(_('You can only reply to messages sent to you.'))
        
        super().clean()

    def get_thread(self, depth=10):
        """
        Recursively fetch the entire message thread.
        Uses prefetch_related to optimize database queries.
        """
        def get_replies(message, current_depth):
            if current_depth >= depth:
                return []
            replies = list(message.replies.all())
            for reply in replies:
                reply.replies_list = get_replies(reply, current_depth + 1)
            return replies

        thread = []
        current = self
        while current:
            current.replies_list = get_replies(current, 0)
            thread.append(current)
            current = current.parent_message
        
        return reversed(thread)

    @classmethod
    def get_conversation_threads(cls, user1, user2):
        """
        Get all message threads between two users.
        Optimized with select_related and prefetch_related.
        """
        return cls.objects.filter(
            models.Q(sender=user1, receiver=user2) |
            models.Q(sender=user2, receiver=user1),
            parent_message__isnull=True
        ).select_related(
            'sender', 'receiver'
        ).prefetch_related(
            models.Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver')
                .prefetch_related('replies')
            )
        ).order_by('-timestamp')

    def mark_as_read(self):
        """Mark the message and its thread as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
            # Mark all replies as read
            self.replies.all().update(is_read=True)
