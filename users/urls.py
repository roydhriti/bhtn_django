
from django.urls import path
from .views import RegisterView, LoginView, UserView, UserListView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('users', UserListView.as_view()),
    path('forgot-password', ForgotPasswordView.as_view()),
    path('reset-password', ResetPasswordView.as_view()),

   
]