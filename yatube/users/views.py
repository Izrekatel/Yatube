from allauth.account.models import EmailAddress
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView

from posts.models import CustomUser

from .forms import AccountForm, CreationForm, LoginForm


class CustomLoginView(LoginView):
    form_class = LoginForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/login.html'


class SignUp(FormView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super(SignUp, self).form_valid(form)


@login_required
def account(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    subscribers = user.following.all()

    account_verified = False
    email = EmailAddress.objects.filter(email=user.email)
    if len(email):
        account_verified = email[0].verified
    context = {
        'user': user,
        'account_verified': account_verified,
        'subscribers': subscribers
    }
    return render(request, 'users/account.html', context)

@login_required
def account_update(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    form = AccountForm(request.POST or None,
                       files=request.FILES or None,
                       instance=user)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('users:account'))
    context = {'form': form, 'user': user}
    return render(request, 'users/account_update.html', context)
