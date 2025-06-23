from django.shortcuts import render

# Create your views here.
# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart:view_cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('cart:view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    cart_items = []

    for product in products:
        quantity = cart[str(product.id)]
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': quantity * product.price
        })

    total = sum(item['total_price'] for item in cart_items)

    return render(request, 'products/cart_view.html', {
        'cart_items': cart_items,
        'total': total
    })
