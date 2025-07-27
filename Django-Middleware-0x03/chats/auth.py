# messaging_app/chats/auth.py

from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    Placeholder for custom JWT logic.
    Extend this class later to customize token validation or user claims.
    """
    pass
