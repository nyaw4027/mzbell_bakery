# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

from django.views.generic import DetailView
from django.views.decorators.http import require_http_methods
from .models import Profile
from .forms import ProfileEditForm, UserEditForm
 # Make sure UserEditForm exists in forms.py


class ProfileDetailView(DetailView):
    """Class-based view for profile detail - renamed to avoid conflict"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        profile, created = Profile.objects.get_or_create(user=user)
        context['profile'] = profile
        return context


@login_required
def profile_view(request, username):
    """Function-based view for profile display"""
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    
    context = {
        'profile_user': user,
        'profile': profile,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        # Handle image removal
        if request.POST.get('remove_image'):
            if profile.image:
                # Delete the file from storage
                profile.image.delete(save=False)
                profile.image = None
        
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)

    context = {
        'form': form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile_edit.html', context)


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for new user
            Profile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    """User dashboard"""
    return render(request, 'users/dashboard.html')



def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            messages.success(request, 'Account created! You can now log in.')
            return redirect('users:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def edit_profile(request):
    return render(request, 'users/edit_profile.html')


@require_http_methods(["GET", "POST"])
@login_required
def logout_view(request):
    """Logs out the user on GET or POST request."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('users:login')  # or 'home'

