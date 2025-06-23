# cart/cart.py
from products.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        self.cart[product_id] = self.cart.get(product_id, 0) + quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def items(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            quantity = self.cart[str(product.id)]
            yield {
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity
            }

    def total(self):
        return sum(item['total_price'] for item in self.items())
