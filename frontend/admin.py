from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from .models import ContactMessage, TeamMember, Testimonial

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


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_quote', 'image_preview')

    def short_quote(self, obj):
        return (obj.quote[:50] + '...') if len(obj.quote) > 50 else obj.quote
    short_quote.short_description = 'Quote'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;width:50px;border-radius:50%;">', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'