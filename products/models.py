from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from django.utils.html import mark_safe

User = settings.AUTH_USER_MODEL

# === Validators ===
def validate_image_url(value):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not any(value.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError("Image URL must end with .jpg, .jpeg, .png, .gif, or .webp")

def validate_image_size(image):
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("Image file size must be less than 5MB")


# === Category ===
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True, validators=[validate_image_size])
    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        validators=[URLValidator(), validate_image_url],
        help_text="Paste an image URL (e.g., https://example.com/image.jpg)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return '/static/images/placeholder.jpg'

    def image_tag(self):
        img = self.get_image()
        if img:
            return mark_safe(f'<img src="{img}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />')
        return "(No image)"
    image_tag.short_description = 'Image Preview'


# === Tag ===
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# === Product ===
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, validators=[validate_image_size])
    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        validators=[URLValidator(), validate_image_url],
        help_text="Paste an image URL (e.g., https://example.com/image.jpg)"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True)

    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    ingredients = models.TextField(blank=True)
    allergens = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_image(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return '/static/images/placeholder.jpg'

    def image_tag(self):
        img = self.get_image()
        if img:
            return mark_safe(f'<img src="{img}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />')
        return "(No image)"
    image_tag.short_description = 'Image Preview'

    def average_rating(self):
        reviews = self.reviews.all()
        return round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews.exists() else 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# === ProductVariation ===
class ProductVariation(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('white', 'White'),
        ('black', 'Black'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, null=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, blank=True, null=True)
    additional_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.product.name} - {self.size or ''} {self.color or ''}".strip()


# === ProductReview ===
class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.product.name} ({self.rating})"
