from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login')
