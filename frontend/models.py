from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from PIL import Image
import os

# Reusable validator for image size
def validate_image_size(image):
    max_size_mb = 1  # 1MB max
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image must be under {max_size_mb}MB in size.")

# Reusable validator for image dimensions
def validate_image_dimensions(image):
    max_width = 2000
    max_height = 2000
    
    try:
        img = Image.open(image)
        if img.width > max_width or img.height > max_height:
            raise ValidationError(f"Image dimensions must be under {max_width}x{max_height} pixels.")
    except Exception:
        raise ValidationError("Invalid image file.")

# Contact Form Messages
class ContactMessage(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('resolved', 'Resolved'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email} ({self.created_at.date()})"

# Team Members with social links
class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='team/',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_dimensions]
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Contact information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Social media links
    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.role}"

# Customer Testimonials
class Testimonial(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    quote = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_dimensions]
    )
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} stars"

# Gallery Categories
class GalleryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#d63384', help_text='Hex color code for category badge')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Gallery Categories"
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_image_count(self):
        return self.images.filter(is_active=True).count()

# Gallery Images for frontend display
class GalleryImage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='gallery/',
        validators=[validate_image_size, validate_image_dimensions]
    )
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='images'
    )
    alt_text = models.CharField(max_length=255, blank=True, help_text='Alternative text for accessibility')
    
    # SEO and metadata
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')
    
    # Status and visibility
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Order and dates
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Generate alt text if not provided
        if not self.alt_text:
            self.alt_text = f"{self.title} - {self.category.name if self.category else 'Gallery image'}"
        super().save(*args, **kwargs)
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

# Blog/News Posts
class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(max_length=300, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(
        upload_to='blog/',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_dimensions]
    )
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')
    
    # Status and publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Author (can be linked to User model later)
    author_name = models.CharField(max_length=100, default='MzBell\'s Bakery')
    
    # Dates
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

# FAQ Section
class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('ordering', 'Ordering'),
        ('delivery', 'Delivery'),
        ('products', 'Products'),
        ('custom', 'Custom Orders'),
        ('general', 'General'),
    ]
    
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question

# Newsletter Subscribers
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

# Site Settings (for dynamic content)
class SiteSettings(models.Model):
    # Business Information
    business_name = models.CharField(max_length=100, default="MzBell's Bakery")
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Business Hours
    business_hours = models.TextField(blank=True, help_text='HTML formatted business hours')
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Features
    delivery_available = models.BooleanField(default=True)
    custom_orders_available = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return f"Site Settings - {self.business_name}"

    @classmethod
    def get_settings(cls):
        """Get or create site settings"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings