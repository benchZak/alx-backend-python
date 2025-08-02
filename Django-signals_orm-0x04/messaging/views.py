from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
def inbox_unread(request):
    """
    View showing all unread messages for the current user.
    Uses the custom manager with optimized queries.
    """
    unread_messages = Message.unread.unread_for_user(request.user)
    unread_count = Message.unread.unread_count_for_user(request.user)
    
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_count
    })
