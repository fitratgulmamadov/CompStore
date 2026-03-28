from .models import Cart
# from admin_interface.models import Theme


def cart_context(request):
    cart = None
    if request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
    # theme = Theme.objects.get_active()
    # site_name = theme.title if theme else 'CompStore'
    site_name = 'CompStore'  # Фиксированное название сайта
    return {'cart': cart, 'site_name': site_name}
