from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View

User = get_user_model()

@method_decorator(login_required, name='dispatch')
class DeleteAccountView(View):
    def get(self, request):
        # Display confirmation page (optional)
        return render(request, 'messaging/confirm_delete.html')

    @method_decorator(require_POST)
    def post(self, request):
        user = request.user
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('home')  # Redirect to your home page or login page

# Alternative function-based view
@login_required
@require_POST
def delete_account(request):
    request.user.delete()
    messages.success(request, "Your account has been successfully deleted.")
    return redirect('home')
