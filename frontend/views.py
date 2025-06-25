from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from products.models import Product, Category
from .models import ContactMessage, TeamMember
import json
import uuid
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
import requests

def home(request):
    """
    Home page view
    """
    # Get featured products for the homepage
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    
    # If no featured products, get latest products
    if not featured_products:
        featured_products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    
    # Get categories for navigation
    categories = Category.objects.all()[:6]
    
    # Get cart count for header
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'cart_count': cart_count,
        'page_title': 'Welcome to MzBell\'s Bakery'
    }
    
    return render(request, 'home.html', context)


def products(request):
    """
    Products listing page with search and filtering
    """
    products_list = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filtering
    category_id = request.GET.get('category', '')
    if category_id:
        try:
            products_list = products_list.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            pass
    
    # Price range filtering
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        try:
            products_list = products_list.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            products_list = products_list.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_high':
        products_list = products_list.order_by('-price')
    elif sort_by == 'newest':
        products_list = products_list.order_by('-created_at')
    elif sort_by == 'popular':
        # You can implement popularity based on orders or views
        products_list = products_list.order_by('-created_at')  # Placeholder
    else:
        products_list = products_list.order_by('name')
    
    # Pagination
    paginator = Paginator(products_list, 12)  # 12 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Get cart count
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'cart_count': cart_count,
        'page_title': 'Our Products'
    }
    
    return render(request, 'frontend/products.html', context)


def product_detail(request, product_id):
    """
    Individual product detail page
    """
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    # Get related products from the same category
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product_id)[:4]
    
    # Get cart count
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    
    # Check if product is already in cart
    in_cart = str(product_id) in cart
    cart_quantity = cart.get(str(product_id), 0) if in_cart else 0
    
    context = {
        'product': product,
        'related_products': related_products,
        'cart_count': cart_count,
        'in_cart': in_cart,
        'cart_quantity': cart_quantity,
        'page_title': product.name
    }
    
    return render(request, 'frontend/product_detail.html', context)


def cart(request):
    """
    Shopping cart page
    """
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_available=True)
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            # Remove unavailable products from cart
            del cart[product_id]
            request.session['cart'] = cart
            request.session.modified = True
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': sum(cart.values()) if cart else 0,
        'page_title': 'Shopping Cart'
    }
    
    return render(request, 'frontend/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    """
    Add product to cart
    """
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    # Get or create cart in session
    cart = request.session.get('cart', {})
    
    # Get quantity from POST data, default to 1
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    # Add to cart
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    
    # Save cart back to session
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, f'{product.name} added to cart!')
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': sum(cart.values())
        })
    
    # Redirect to previous page or cart
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/cart/'))
    return redirect(next_url)


@require_POST
def update_cart(request, product_id):
    """
    Update quantity of item in cart
    """
    cart = request.session.get('cart', {})
    
    try:
        quantity = int(request.POST.get('quantity', 0))
        
        if quantity <= 0:
            # Remove item from cart
            if str(product_id) in cart:
                del cart[str(product_id)]
                messages.success(request, 'Item removed from cart!')
        else:
            # Update quantity
            if str(product_id) in cart:
                cart[str(product_id)] = quantity
                messages.success(request, 'Cart updated!')
    except (ValueError, TypeError):
        messages.error(request, 'Invalid quantity!')
    
    # Save cart back to session
    request.session['cart'] = cart
    request.session.modified = True
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values())
        })
    
    return redirect('frontend:cart')


@require_POST
def remove_from_cart(request, product_id):
    """
    Remove product from cart
    """
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart!')
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values())
        })
    
    return redirect('frontend:cart')


def checkout(request):
    """
    Checkout page
    """
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('frontend:cart')
    
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_available=True)
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            continue
    
    if request.method == 'POST':
        # Get form data
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        special_instructions = request.POST.get('special_instructions', '').strip()
        
        # Basic validation
        if not all([customer_name, customer_email, customer_phone]):
            messages.error(request, 'Please fill in all required fields!')
            return render(request, 'frontend/checkout.html', {
                'cart_items': cart_items,
                'total': total,
                'page_title': 'Checkout'
            })
        
        # Create a simple order record in session (for demo purposes)
        order_id = str(uuid.uuid4())[:8].upper()
        order_data = {
            'id': order_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'delivery_address': delivery_address,
            'special_instructions': special_instructions,
            'items': cart_items,
            'total': float(total),
            'status': 'pending',
            'created_at': timezone.now().isoformat()
        }
        
        # Store order in session (in a real app, save to database)
        orders = request.session.get('orders', [])
        orders.append(order_data)
        request.session['orders'] = orders
        
        # Clear cart after successful order
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, f'Order #{order_id} placed successfully! We\'ll contact you soon.')
        return redirect('frontend:order_confirmation', order_id=order_id)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'page_title': 'Checkout'
    }
    
    return render(request, 'frontend/checkout.html', context)


def order_confirmation(request, order_id):
    """
    Order confirmation page
    """
    orders = request.session.get('orders', [])
    order = None
    
    for o in orders:
        if o['id'] == order_id:
            order = o
            break
    
    if not order:
        messages.error(request, 'Order not found!')
        return redirect('frontend:home')
    
    context = {
        'order': order,
        'page_title': f'Order Confirmation - #{order_id}'
    }
    
    return render(request, 'frontend/order_confirmation.html', context)


def orders(request):
    """
    User's orders page
    """
    orders = request.session.get('orders', [])
    # Sort orders by creation date (newest first)
    orders.sort(key=lambda x: x['created_at'], reverse=True)
    
    context = {
        'orders': orders,
        'page_title': 'My Orders'
    }
    
    return render(request, 'frontend/orders.html', context)


def order_detail(request, order_id):
    """
    Individual order detail page
    """
    orders = request.session.get('orders', [])
    order = None
    
    for o in orders:
        if o['id'] == order_id:
            order = o
            break
    
    if not order:
        messages.error(request, 'Order not found!')
        return redirect('frontend:orders')
    
    context = {
        'order': order,
        'page_title': f'Order #{order_id}'
    }
    
    return render(request, 'frontend/order_detail.html', context)


def track_order(request, order_id):
    """
    Order tracking page
    """
    orders = request.session.get('orders', [])
    order = None
    
    for o in orders:
        if o['id'] == order_id:
            order = o
            break
    
    if not order:
        messages.error(request, 'Order not found!')
        return redirect('frontend:home')
    
    # Define order status progression
    status_progression = {
        'pending': {'label': 'Order Received', 'progress': 25},
        'processing': {'label': 'Preparing Your Order', 'progress': 50},
        'ready': {'label': 'Ready for Pickup/Delivery', 'progress': 75},
        'completed': {'label': 'Order Completed', 'progress': 100},
        'cancelled': {'label': 'Order Cancelled', 'progress': 0}
    }
    
    current_status = status_progression.get(order['status'], status_progression['pending'])
    
    context = {
        'order': order,
        'current_status': current_status,
        'page_title': f'Track Order #{order_id}'
    }
    
    return render(request, 'frontend/track_order.html', context)


def about(request):
    """
    About us page with team members
    """
    team = TeamMember.objects.all()

    context = {
        'page_title': "About MzBell's Bakery",
        'team': team
    }

    return render(request, 'frontend/about.html', context)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, message]):
            messages.error(request, 'Please fill in all required fields!')
        else:
            # Save to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            # Send email (optional - already configured)
            send_mail(
                subject or 'New Contact Message',
                f"From: {name} <{email}>\n\n{message}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False
            )

            return redirect('frontend:contact_thank_you')

    return render(request, 'frontend/contact.html', {'page_title': 'Contact Us'})
def menu(request):
    """
    Bakery menu page
    """
    # Get products organized by category (only available ones)
    categories = Category.objects.prefetch_related('products').filter(
        products__is_available=True
    ).distinct()

    # Get cart count
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0

    context = {
        'categories': categories,
        'cart_count': cart_count,
        'page_title': 'Our Menu'
    }

    return render(request, 'frontend/menu.html', context)

import uuid
def custom_order_form(request):
    """
    Custom order form page
    """
    if request.method == 'POST':
        # Handle custom order form submission
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        event_type = request.POST.get('event_type', '').strip()
        event_date = request.POST.get('event_date', '').strip()
        guest_count = request.POST.get('guest_count', '').strip()
        description = request.POST.get('description', '').strip()
        budget = request.POST.get('budget', '').strip()
        
        # Basic validation
        if not all([name, email, phone, event_type, event_date, description]):
            messages.error(request, 'Please fill in all required fields!')
        else:
            # Store custom order request (in a real app, save to database)
            custom_orders = request.session.get('custom_orders', [])
            custom_order = {
                'id': str(uuid.uuid4())[:8].upper(),
                'name': name,
                'email': email,
                'phone': phone,
                'event_type': event_type,
                'event_date': event_date,
                'guest_count': guest_count,
                'description': description,
                'budget': budget,
                'status': 'pending',
                'created_at': timezone.now().isoformat()
            }
            custom_orders.append(custom_order)
            request.session['custom_orders'] = custom_orders
            request.session.modified = True
            
            messages.success(request, f'Your custom order request #{custom_order["id"]} has been submitted! We\'ll contact you soon.')
            return redirect('frontend:custom_order_form')
    
    context = {
        'page_title': 'Custom Orders'
    }
    
    return render(request, 'frontend/custom_order_form.html', context)


def catering(request):
    """
    Catering services page
    """
    if request.method == 'POST':
        # Handle catering inquiry form
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        event_date = request.POST.get('event_date', '').strip()
        guest_count = request.POST.get('guest_count', '').strip()
        event_type = request.POST.get('event_type', '').strip()
        requirements = request.POST.get('requirements', '').strip()
        
        if not all([name, email, phone, event_date, guest_count]):
            messages.error(request, 'Please fill in all required fields!')
        else:
            messages.success(request, 'Thank you for your catering inquiry! We\'ll contact you with a quote.')
            return redirect('frontend:catering')
    
    context = {
        'page_title': 'Catering Services'
    }
    
    return render(request, 'frontend/catering.html', context)


def events(request):
    """
    Events and special occasions page
    """
    context = {
        'page_title': 'Events & Special Occasions'
    }
    
    return render(request, 'frontend/events.html', context)


def services(request):
    """
    Services overview page
    """
    context = {
        'page_title': 'Our Services'
    }
    
    return render(request, 'frontend/services.html', context)


# AJAX Views for dynamic functionality
@csrf_exempt
def get_cart_count(request):
    """
    Get current cart count via AJAX
    """
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    
    return JsonResponse({'cart_count': cart_count})


def search_products(request):
    """
    AJAX product search
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_available=True
    )[:10]
    
    products_data = [{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'image_url': p.image.url if p.image else None
    } for p in products]
    
    return JsonResponse({'products': products_data})

def dashboard(request):
    return render(request, 'frontend/dashboard.html')


    
@csrf_exempt
def process_checkout(request):
    if request.method == 'POST':
        # Collect submitted form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        # Optionally: create Order object, send email, etc.
        # For now just redirect to success
        return redirect('checkout_success')  # Create this view later

    return redirect('checkout')  # Redirect back if not POST

def checkout_success(request):
    return render(request, 'frontend/checkout_success.html')


def initiate_momo_payment(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')

        tx_ref = str(uuid.uuid4())

        momo_data = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": "GHS",
            "payment_options": "mobilemoneyghana",
            "redirect_url": request.build_absolute_uri('/checkout/success/'),
            "customer": {
                "email": email,
                "phonenumber": phone,
                "name": full_name,
            },
            "customizations": {
                "title": "MzBell Bakery Payment",
                "description": "Payment for order"
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post('https://api.flutterwave.com/v3/payments', json=momo_data, headers=headers)

        if response.status_code == 200:
            payment_link = response.json()['data']['link']
            return redirect(payment_link)
        else:
            return JsonResponse({'error': 'Payment initiation failed'}, status=400)

    return redirect('checkout')

def contact_view(request):
        return render(request, 'frontend/contact.html')


def about_view(request):
    team_members = TeamMember.objects.all()
    return render(request, 'about.html', {'team_members': team_members})



