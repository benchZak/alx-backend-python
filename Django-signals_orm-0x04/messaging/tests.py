from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

class UserDeletionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # Create test data
        self.message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message 1"
        )
        self.message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message 2"
        )
        self.notification1 = Notification.objects.create(
            user=self.user1,
            message=self.message2
        )
        self.notification2 = Notification.objects.create(
            user=self.user2,
            message=self.message1
        )
        self.message1.content = "Edited message"
        self.message1.save()
        self.history = MessageHistory.objects.first()

    def test_user_deletion_cascades_to_messages(self):
        # Verify initial data
        self.assertEqual(Message.objects.count(), 2)
        
        # Delete user1
        self.user1.delete()
        
        # Verify messages where user1 was sender or receiver are deleted
        self.assertEqual(Message.objects.count(), 0)
        
    def test_user_deletion_cascades_to_notifications(self):
        # Verify initial data
        self.assertEqual(Notification.objects.count(), 2)
        
        # Delete user1
        self.user1.delete()
        
        # Verify notifications for user1 are deleted
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().user, self.user2)
        
        # Delete user2
        self.user2.delete()
        
        # Verify all notifications are deleted
        self.assertEqual(Notification.objects.count(), 0)
    
    def test_user_deletion_handles_message_history(self):
        # Verify initial data
        self.assertEqual(MessageHistory.objects.count(), 1)
        self.assertEqual(self.history.edited_by, self.user1)
        
        # Delete user1
        self.user1.delete()
        
        # Refresh history from db
        self.history.refresh_from_db()
        
        # Verify edited_by is set to NULL
        self.assertIsNone(self.history.edited_by)
        self.assertEqual(MessageHistory.objects.count(), 1)
