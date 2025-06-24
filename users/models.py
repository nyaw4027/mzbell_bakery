from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
import os


def user_avatar_upload_path(instance, filename):
    # Saves avatar as avatars/user_<id>.<ext>
    ext = filename.split('.')[-1]
    return f"avatars/user_{instance.user.id}.{ext}"


class Profile(models.Model):
    """Extended user profile with additional info."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    dietary_preferences = models.CharField(max_length=100, blank=True, help_text="e.g., Vegan, Gluten-free")
    favorite_flavors = models.CharField(max_length=100, blank=True, help_text="e.g., Chocolate, Vanilla")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_address(self):
        parts = [self.address, self.city, self.state]
        return ', '.join(filter(None, parts))

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Automatically create or update Profile on User creation
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
