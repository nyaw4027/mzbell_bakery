from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from .models import ContactMessage, TeamMember

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'image_tag')
    search_fields = ('name', 'role')
    list_filter = ('role',)
    ordering = ('name',)
    list_per_page = 10

    fields = (
        'name', 'role', 'bio', 'image', 'order',
        'twitter', 'facebook', 'instagram', 'linkedin'
    )

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;">', obj.image.url)
        return "-"
    image_tag.short_description = 'Photo'



class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    quote = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)

    def __str__(self):
        return self.name

