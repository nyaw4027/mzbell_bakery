from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from .models import ContactMessage, TeamMember, Testimonial, GalleryImage



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('created_at', 'is_read')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')
    mark_as_unread.short_description = "Mark selected messages as unread"


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'image_tag', 'order', 'is_active')
    search_fields = ('name', 'role', 'bio')
    list_filter = ('role', 'is_active')
    ordering = ('order', 'name')
    list_per_page = 10
    list_editable = ('order', 'is_active')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'role', 'bio', 'image', 'order', 'is_active')
        }),
        ('Social Media Links', {
            'fields': ('twitter', 'facebook', 'instagram', 'linkedin'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%; object-fit:cover;" />',
                obj.image.url
            )
        return "-"
    image_tag.short_description = 'Photo'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_quote', 'image_preview', 'rating', 'is_featured', 'created_at')
    search_fields = ('name', 'quote')
    list_filter = ('rating', 'is_featured', 'created_at')
    ordering = ('-created_at', '-rating')
    list_per_page = 20
    list_editable = ('is_featured', 'rating')
    readonly_fields = ('image_preview', 'created_at')
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'image', 'image_preview')
        }),
        ('Testimonial Details', {
            'fields': ('quote', 'rating', 'is_featured')
        }),
        ('Additional Info', {
            'fields': ('product', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'unmark_as_featured']

    def short_quote(self, obj):
        if obj.quote:
            return (obj.quote[:50] + '...') if len(obj.quote) > 50 else obj.quote
        return "-"
    short_quote.short_description = 'Quote Preview'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px; width:50px; border-radius:50%; object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Customer Photo'
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonial(s) marked as featured.')
    mark_as_featured.short_description = "Mark selected testimonials as featured"
    
    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} testimonial(s) unmarked as featured.')
    unmark_as_featured.short_description = "Remove featured status"


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'thumbnail_preview', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'alt_text')
    list_filter = ('category', 'is_featured', 'created_at')
    ordering = ('-created_at', 'title')
    list_per_page = 20
    list_editable = ('is_featured', 'category')
    readonly_fields = ('thumbnail_preview', 'image_size', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Image Information', {
            'fields': ('title', 'image', 'thumbnail_preview', 'alt_text')
        }),
        ('Categorization', {
            'fields': ('category', 'is_featured', 'description')
        }),
        ('Technical Details', {
            'fields': ('image_size', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'unmark_as_featured']

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px; width:60px; object-fit:cover; border-radius:8px; border:1px solid #ddd;" />',
                obj.image.url
            )
        return "No image"
    thumbnail_preview.short_description = 'Preview'
    
    def image_size(self, obj):
        if obj.image:
            try:
                return f"{obj.image.width} x {obj.image.height} pixels"
            except:
                return "Size unavailable"
        return "No image"
    image_size.short_description = 'Dimensions'
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} image(s) marked as featured.')
    mark_as_featured.short_description = "Mark selected images as featured"
    
    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} image(s) unmarked as featured.')
    unmark_as_featured.short_description = "Remove featured status"


# Customize the admin site header and title
admin.site.site_header = "MzBell's Bakery Admin"
admin.site.site_title = "MzBell's Bakery"
admin.site.index_title = "Welcome to MzBell's Bakery Administration"