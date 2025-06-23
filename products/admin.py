from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Tag, ProductVariation, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Image Options', {
            'fields': ('image', 'image_url', 'image_preview'),
            'description': 'Upload an image or paste an image URL.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def image_preview(self, obj):
        img = obj.get_image()
        if img:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="60" height="60" style="object-fit: cover; border-radius: 5px;" />'
                '</a>', img
            )
        return "(No image)"
    image_preview.short_description = 'Image Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'is_available', 'is_featured', 'image_preview')
    list_filter = ('is_available', 'is_featured', 'is_new_arrival', 'is_on_sale', 'category')
    search_fields = ('name', 'description', 'ingredients', 'allergens')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'description', 'price', 'stock', 'category', 'tags')
        }),
        ('Availability', {
            'fields': ('is_available', 'is_featured', 'is_new_arrival', 'is_on_sale', 'sale_price')
        }),
        ('Ingredients & Allergens', {
            'fields': ('ingredients', 'allergens')
        }),
        ('Image Options', {
            'fields': ('image', 'image_url', 'image_preview'),
            'description': 'Upload an image or paste an image URL.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def image_preview(self, obj):
        img = obj.get_image()
        if img:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="60" height="60" style="object-fit: cover; border-radius: 5px;" />'
                '</a>', img
            )
        return "(No image)"
    image_preview.short_description = 'Image Preview'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'additional_price')
    list_filter = ('size', 'color')
    search_fields = ('product__name',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username')
    list_filter = ('rating', 'created_at')
