from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, LoginView, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
