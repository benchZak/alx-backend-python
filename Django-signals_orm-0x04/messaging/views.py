from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views import View
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()

@login_required
@require_http_methods(["GET", "POST"])
def delete_user(request):
    """
    Handle user account deletion with confirmation.
    """
    if request.method == 'POST':
        # Verify password if you want extra security
        # password = request.POST.get('password')
        # if not request.user.check_password(password):
        #     messages.error(request, _('Incorrect password. Account not deleted.'))
        #     return redirect('delete_account')
        
        # Store username for feedback message before deletion
        username = request.user.username
        
        # Delete the user (signals will handle related data cleanup)
        request.user.delete()
        
        # Clear session
        from django.contrib.auth import logout
        logout(request)
        
        messages.success(
            request, 
            _(f'Account {username} and all associated data have been permanently deleted.')
        )
        return redirect('home')  # Redirect to your home page
    
    # GET request - show confirmation page
    return render(request, 'messaging/account/delete_confirm.html', {
        'user': request.user,
        'message_count': request.user.sent_messages.count() + request.user.received_messages.count(),
        'notification_count': request.user.notifications.count(),
    })


class DeleteAccountView(View):
    """
    Class-based version of the account deletion view.
    """
    template_name = 'messaging/account/delete_confirm.html'
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _('You must be logged in to delete your account.'))
            return redirect(reverse('login') + f'?next={reverse("delete_account")}')
        
        return render(request, self.template_name, self.get_context_data())
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _('You must be logged in to delete your account.'))
            return redirect(reverse('login') + f'?next={reverse("delete_account")}')
        
        username = request.user.username
        request.user.delete()
        
        from django.contrib.auth import logout
        logout(request)
        
        messages.success(
            request,
            _(f'Account {username} and all associated data have been permanently deleted.')
        )
        return redirect('home')
    
    def get_context_data(self, **kwargs):
        context = {
            'user': self.request.user,
            'message_count': (self.request.user.sent_messages.count() + 
                            self.request.user.received_messages.count()),
            'notification_count': self.request.user.notifications.count(),
            'data_affected': [
                _('Your profile information'),
                _('All messages you sent or received'),
                _('All your notifications'),
                _('Message edit history you created'),
            ]
        }
        context.update(kwargs)
        return context
