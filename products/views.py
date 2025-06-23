from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Product, Category, Tag
from .forms import ProductReviewForm
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from .serializers import CategorySerializer
from rest_framework import generics
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from .serializers import ProductSerializer





from rest_framework.views import APIView
from rest_framework.response import Response

# Import yclass ProductListour models as needed

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # ✅ Makes it public
    def get_queryset(self):
        # ✅ Fix: explicitly order by a consistent field like `created_at`, `id`, or `name`
        return Product.objects.all().order_by('-id')  # or any field you prefer

class ProductDetailView(DetailView):
    """
    Class-based view to display individual product details
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class CategoryListView(ListView):
    """
    Class-based view to display all categories
    """
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'


def featured_products(request):
    products = Product.objects.filter(is_featured=True, is_available=True)

    # Filters
    category_id = request.GET.get('category')
    tag_id = request.GET.get('tag')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort_by')

    if category_id:
        products = products.filter(category_id=category_id)

    if tag_id:
        products = products.filter(tags__id=tag_id)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # Sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'latest':
        products = products.order_by('-created_at')

    context = {
        'featured_products': products,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'selected_category': category_id,
        'selected_tag': tag_id,
    }
    return render(request, 'products/featured_products.html', context)


def view_cart(request):
    """
    View function to display the shopping cart
    """
    # Get cart items from session
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': sum(cart.values())
    }
    return render(request, 'products/cart.html', context)




def custom_order_form(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        event_date = request.POST.get('event_date')
        product_type = request.POST.get('product_type')
        servings = request.POST.get('servings')
        flavor = request.POST.get('flavor')
        budget = request.POST.get('budget')
        requirements = request.POST.getlist('requirements')
        design_description = request.POST.get('design_description')
        additional_notes = request.POST.get('additional_notes')
        delivery_option = request.POST.get('delivery_option')
        delivery_address = request.POST.get('delivery_address')

        # Optionally save to DB or send email
        # ...

        # AJAX response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Your custom order has been submitted successfully!'
            })

        # Regular POST response
        messages.success(request, 'Your custom order request has been submitted successfully!')
        return redirect('custom_order_success')

    return render(request, 'orders/custom_order_form.html')


def menu(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/menu.html', {'page_obj': page_obj})


@require_POST
@login_required
def add_to_cart(request, product_id):
    """
    Add a product to the cart with session storage.
    Handles both form and JSON (AJAX) requests.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    # Determine if it's a JSON (AJAX) request
    if request.content_type == 'application/json':
        import json
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except Exception:
            return HttpResponseBadRequest('Invalid JSON')
    else:
        quantity = int(request.POST.get('quantity', 1))

    # Update cart
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + quantity
    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': sum(cart.values()),
            'product_id': product.id,
            'product_name': product.name
        })

    # Non-AJAX fallback
    messages.success(request, f'{product.name} added to cart!')
    return redirect('products:product_detail', pk=product_id)
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    reviews = product.reviews.all()

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            try:
                review.save()
                messages.success(request, "Review submitted successfully!")
                return redirect('product_detail', slug=product.slug)
            except:
                messages.warning(request, "You’ve already reviewed this product.")
    else:
        form = ProductReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'products/product_detail.html', context)

def home(request):
    products = Product.objects.filter(is_available=True)[:6]  # or .all() for all
    return render(request, 'home.html', {'products': products})


def product_list(request):
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    
    paginator = Paginator(products, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'products/product_list.html', context)



class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.values('id', 'name')
        return Response({'categories': categories})
    

def home(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'home.html', {'products': products})

def all_products(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    tags = Tag.objects.all()

    category_id = request.GET.get('category')
    tag_id = request.GET.get('tag')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_id:
        products = products.filter(category__id=category_id)
    if tag_id:
        products = products.filter(tags__id=tag_id)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'products': products,
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'products/all_products.html', context)

def product_list(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'products/product_list.html', {'products': products})


def custom_order(request):
    return render(request, 'products/custom_order.html')


    
def custom_order(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        event_date = request.POST.get('event_date')
        product_type = request.POST.get('product_type')
        servings = request.POST.get('servings')
        flavor = request.POST.get('flavor')
        budget = request.POST.get('budget')
        design_description = request.POST.get('design_description')
        additional_notes = request.POST.get('additional_notes')
        delivery_option = request.POST.get('delivery_option')
        delivery_address = request.POST.get('delivery_address')

        print("Received custom order from:", full_name)

        messages.success(request, "Your custom order request was submitted successfully!")
        return redirect('custom_order')

    return render(request, 'products/custom_order_form.html')  # ✅ Corrected this line

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    request.session['cart'] = cart

    messages.success(request, f"{product.name} added to cart.")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))




class CategoryListView(APIView):
    permission_classes = [AllowAny]

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


def category_product_list(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()  # Adjust if using related_name
    return render(request, 'products/products_by_category.html', {
        'category': category,
        'products': products
    })
def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})


def product_list_view(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'products/product_list.html', {'products': products})
