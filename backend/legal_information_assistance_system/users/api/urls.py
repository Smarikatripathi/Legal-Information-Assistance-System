from django.urls import path

from .views import (
    ChangePasswordView,
    ForgotPasswordView,
    LawyerDetailAPIView,
    LawyerListAPIView,
    LoginView,
    LogoutView,
    ProfileUpdateView,
    ResetPasswordView,
    SignupView,
    TokenRefreshAPIView,
)

auth_urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    path("lawyers/",LawyerListAPIView.as_view(), name="lawyer-list",),
    path("lawyers/<int:pk>/",LawyerDetailAPIView.as_view(), name="lawyer-detail",),

]

app_name = "auth"
urlpatterns = auth_urlpatterns
