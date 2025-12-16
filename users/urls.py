from django.urls import path
from .views import RegisterView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    # optional refresh
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
