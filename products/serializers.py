from rest_framework import serializers
from .models import Product, Category, Tag, ProductVariation, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = ['id', 'size', 'color', 'additional_price']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ProductReview
        fields = ['user', 'rating', 'comment', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'sale_price', 'stock',
            'category', 'image_url', 'is_available', 'is_featured', 'is_new_arrival',
            'is_on_sale', 'tags', 'ingredients', 'allergens', 'variations', 'reviews',
            'average_rating'
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        img = obj.get_image()
        return request.build_absolute_uri(img) if request and img.startswith('/') else img

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  # Or list specific fields
