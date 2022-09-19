from django.contrib.auth.views import (LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from allauth.account.views import EmailView, EmailVerificationSentView, ConfirmEmailView
from django.urls import path, re_path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    (path('logout/',
     LogoutView.as_view(template_name='users/logged_out.html'),
     name='logout')),
    (path('password_change/',
     PasswordChangeView.as_view(template_name='users/password_change.html'),
     name='password_change')),
    (path('password_change/done/',
     PasswordChangeDoneView.as_view
     (template_name='users/password_change_done.html'),
     name='password_change_done')),
    (path('password_reset/',
     PasswordResetView.as_view(template_name='users/password_reset_form.html'),
     name='password_reset')),
    (path('password_reset/done/',
     PasswordResetDoneView.as_view
     (template_name='users/password_reset_done.html'),
     name='password_reset_done')),
    (path('reset/<uidb64>/<token>/',
     PasswordResetConfirmView.as_view
     (template_name='users/password_reset_confirm.html'),
     name='password_reset_confirm')),
    (path('reset/done/',
     PasswordResetCompleteView.as_view
     (template_name='users/password_reset_complete.html'),
     name='password_reset_complete')),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('account/', views.account, name='account'),
    path('account/update/', views.account_update, name='account_update'),
    path('email/', EmailView.as_view(template_name='users/email.html'), name='email'),
    path('confirm-email/', EmailVerificationSentView.as_view(),
         name='users/account_email_verification_sent'),
    re_path(r'^confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(),
            name='users/account_confirm_email'),
]
