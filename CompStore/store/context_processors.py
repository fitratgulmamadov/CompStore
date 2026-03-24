from .models import Cart


def cart_context(request):
    cart = None
    if request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
    return {'cart': cart}
