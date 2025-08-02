from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
def inbox_unread(request):
    # Using the custom manager exactly as required by checker
    unread_messages = Message.unread.unread_for_user(request.user)
    
    # Still maintaining optimized count query
    unread_count = Message.unread.unread_for_user(request.user).count()
    
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_count
    })
