from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Add your custom fields here if any
    
    class Meta:
        # Add this to avoid clashes
        db_table = 'chats_user'
    
    # These related_names should be unique
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='chats_user_set',
        related_query_name='chats_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='chats_user_set',
        related_query_name='chats_user',
    )
