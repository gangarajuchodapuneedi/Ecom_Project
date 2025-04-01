from core.models import *
from cart.models import Cart
def add_variable_to_context(request):
    if request.user.is_authenticated:
        return{
        "wish_count":Wishlist.objects.filter(user = request.user).count()
            }
    else:
        return{
        "wish_count":0
            }
        

def cart_total_amount(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.product.price * item.quantity for item in cart_items)
        return {"cart_total_amount": total}
    return {"cart_total_amount": 0}