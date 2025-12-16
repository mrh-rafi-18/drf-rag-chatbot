from rest_framework import generics
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rag.tasks import send_verification_email 
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] 
    @extend_schema(
        summary="User Signup",
        description="Create a new user account. A verification email may be sent upon registration.",
        responses={201: RegisterSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Save the user
        user = serializer.save()
        
        # Send verification email
        send_verification_email(user)  # call your function
        

class LoginView(TokenObtainPairView):
     permission_classes = [AllowAny]
     @extend_schema(
        summary="User Login",
        description="Obtain access and refresh JWT tokens by providing valid user credentials (username/email and password).",
    )
     def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
     



class RefreshTokenView(TokenRefreshView):
    @extend_schema(
        summary="Refresh JWT Token",
        description="Obtain a new access token using a valid refresh token.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
      

     
