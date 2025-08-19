from django.urls import path
from accounts.views import signup_view, login_view, logout_view, user_info_view

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("userinfo/", user_info_view, name="userinfo"),
]
