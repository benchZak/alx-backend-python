from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message

@login_required
def inbox_unread(request):
    """
    View showing all unread messages for the current user.
    Uses the custom manager with optimized queries.
    """
    unread_messages = Message.unread.unread_for_user(request.user)
    
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_messages.count()
    })

@login_required
def mark_as_read(request, message_id):
    """
    Mark a specific message as read.
    """
    message = Message.unread.filter(
        id=message_id,
        receiver=request.user
    ).first()
    
    if message:
        message.mark_as_read()
        messages.success(request, "Message marked as read.")
    else:
        messages.error(request, "Message not found or already read.")
    
    return redirect('inbox_unread')
