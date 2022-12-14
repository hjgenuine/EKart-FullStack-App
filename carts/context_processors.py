from .models import Cart, CartItem
from .views import _cart_id

def get_items_count(request):
    if 'admin' in request.path:
        return {}

    cnt = 0

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        items = CartItem.objects.filter(cart=cart)
        for item in items:
            cnt += item.quantity
    except Cart.DoesNotExist:
        pass

    return {"items_count": cnt}