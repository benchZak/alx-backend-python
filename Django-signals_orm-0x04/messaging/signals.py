from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Creates a notification for the receiver when a new message is sent.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Logs the previous content of a message before it's edited.
    """
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Content has changed
                # Create history record
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender
                )
                # Update edited flags
                instance.edited = True
                instance.last_edited = timezone.now()
        except Message.DoesNotExist:
            pass  # New message being created

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up related data when a user is deleted.
    This is a backup in case CASCADE doesn't work as expected.
    """
    # Delete sent messages
    Message.objects.filter(sender=instance).delete()
    
    # Delete received messages
    Message.objects.filter(receiver=instance).delete()
    
    # Delete notifications
    Notification.objects.filter(user=instance).delete()
    
    # Update message history edited_by (set to NULL)
    MessageHistory.objects.filter(edited_by=instance).update(edited_by=None)
