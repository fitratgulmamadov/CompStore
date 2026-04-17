from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Subquery, OuterRef
import json

from .models import Category, Product, SellerListing, PrebuiltPC, PrebuiltLevel, Cart, CartItem, Order, OrderItem


# ── Queryset helper ───────────────────────────────────────────────────────────

def _active_listings_subq(**extra_filters):
    return SellerListing.objects.filter(
        product=OuterRef('pk'),
        is_active=True,
        is_approved=True,
        stock__gt=0,
        **extra_filters,
    ).order_by('price')


def with_best_price(qs):
    """Аннотирует queryset товаров лучшей ценой (минимум среди одобренных активных предложений)."""
    active = _active_listings_subq()
    return qs.annotate(
        best_price=Subquery(active.values('price')[:1]),
        best_listing_id=Subquery(active.values('id')[:1]),
        best_old_price=Subquery(active.values('old_price')[:1]),
    )


def available_products(qs=None):
    """Товары из номенклатуры, у которых есть хотя бы одно активное одобренное предложение."""
    if qs is None:
        qs = Product.objects.select_related('category')
    return with_best_price(qs).filter(best_price__isnull=False)


# ── Cart helper ───────────────────────────────────────────────────────────────

def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


# ── Views ─────────────────────────────────────────────────────────────────────

def home(request):
    categories = Category.objects.all()
    featured_products = available_products().filter(is_featured=True)[:8]
    new_products = available_products().order_by('-created_at')[:8]
    featured_prebuilts = PrebuiltPC.objects.filter(is_featured=True)[:3]
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'featured_prebuilts': featured_prebuilts,
        'new_products': new_products,
    }
    return render(request, 'store/home.html', context)


def catalog(request, category_slug=None):
    categories = Category.objects.all()
    products = available_products()
    current_category = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    sort = request.GET.get('sort', '-created_at')
    sort_map = {
        'price_asc':  'best_price',
        'price_desc': '-best_price',
        'name':       'name',
        '-created_at': '-created_at',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    context = {
        'categories': categories,
        'products': products,
        'current_category': current_category,
        'current_sort': sort,
    }
    return render(request, 'store/catalog.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        with_best_price(Product.objects.select_related('category')),
        slug=slug,
    )
    listings = (
        SellerListing.objects
        .filter(product=product, is_active=True, is_approved=True)
        .select_related('seller__seller_profile')
        .order_by('price')
    )
    related = available_products().filter(category=product.category).exclude(pk=product.pk)[:4]
    context = {
        'product': product,
        'listings': listings,
        'related': related,
    }
    return render(request, 'store/product_detail.html', context)


def prebuilts(request):
    level = request.GET.get('level', '')
    prebuilt_list = PrebuiltPC.objects.prefetch_related('components')
    if level:
        prebuilt_list = prebuilt_list.filter(level_id=level)
    context = {
        'prebuilts': prebuilt_list,
        'current_level': level,
        'level_choices': PrebuiltLevel.objects.all(),
    }
    return render(request, 'store/prebuilts.html', context)


def prebuilt_detail(request, slug):
    prebuilt = get_object_or_404(PrebuiltPC, slug=slug)
    components = prebuilt.prebuiltcomponent_set.select_related('product', 'product__category').all()
    context = {
        'prebuilt': prebuilt,
        'components': components,
    }
    return render(request, 'store/prebuilt_detail.html', context)


def builder(request):
    categories = Category.objects.all()
    products_by_category = {}
    for cat in categories:
        cat_products = with_best_price(
            Product.objects.filter(category=cat)
        ).filter(best_price__isnull=False)
        products_by_category[cat.type] = [
            {
                'id': p.id,
                'listing_id': p.best_listing_id,
                'name': p.name,
                'brand': p.brand,
                'price': float(p.best_price),
                'socket': p.socket,
                'ram_type': p.ram_type,
                'specs': p.specs,
            }
            for p in cat_products
        ]
    context = {
        'categories': categories,
        'products_json': json.dumps(products_by_category, ensure_ascii=False),
    }
    return render(request, 'store/builder.html', context)


def cart(request):
    cart_obj = get_or_create_cart(request)
    context = {'cart': cart_obj}
    return render(request, 'store/cart.html', context)


@require_POST
def cart_add(request):
    cart_obj = get_or_create_cart(request)
    listing_id = request.POST.get('listing_id')
    product_id = request.POST.get('product_id')
    prebuilt_id = request.POST.get('prebuilt_id')
    quantity = int(request.POST.get('quantity', 1))

    if listing_id:
        listing = get_object_or_404(SellerListing, pk=listing_id, is_active=True, is_approved=True)
        item, created = CartItem.objects.get_or_create(cart=cart_obj, listing=listing, prebuilt=None)
        item.quantity = item.quantity + quantity if not created else quantity
        item.save()
        messages.success(request, f'«{listing.product.name}» добавлен в корзину.')

    elif product_id:
        # Для совместимости с конфигуратором — берём самое дешёвое предложение
        listing = (
            SellerListing.objects
            .filter(product_id=product_id, is_active=True, is_approved=True)
            .order_by('price')
            .first()
        )
        if listing:
            item, created = CartItem.objects.get_or_create(cart=cart_obj, listing=listing, prebuilt=None)
            item.quantity = item.quantity + quantity if not created else quantity
            item.save()
            messages.success(request, f'«{listing.product.name}» добавлен в корзину.')
        else:
            messages.error(request, 'Товар недоступен.')

    elif prebuilt_id:
        prebuilt = get_object_or_404(PrebuiltPC, pk=prebuilt_id)
        item, created = CartItem.objects.get_or_create(cart=cart_obj, prebuilt=prebuilt, listing=None)
        item.quantity = item.quantity + quantity if not created else quantity
        item.save()
        messages.success(request, f'«{prebuilt.name}» добавлен в корзину.')

    elif request.POST.get('builder_items'):
        try:
            items = json.loads(request.POST.get('builder_items'))
            for item_data in items:
                listing_id_b = item_data.get('listing_id') or None
                if listing_id_b:
                    listing = get_object_or_404(SellerListing, pk=listing_id_b, is_active=True, is_approved=True)
                else:
                    listing = (
                        SellerListing.objects
                        .filter(product_id=item_data['id'], is_active=True, is_approved=True)
                        .order_by('price').first()
                    )
                if listing:
                    item, created = CartItem.objects.get_or_create(cart=cart_obj, listing=listing, prebuilt=None)
                    if not created:
                        item.quantity += 1
                    item.save()
            messages.success(request, 'Сборка добавлена в корзину!')
        except (json.JSONDecodeError, KeyError):
            pass

    return redirect(request.POST.get('next', '/'))


@require_POST
def cart_update(request):
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    item = get_object_or_404(CartItem, pk=item_id)
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
    return redirect('store:cart')


def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    item.delete()
    messages.success(request, 'Товар удалён из корзины.')
    return redirect('store:cart')


def checkout(request):
    cart_obj = get_or_create_cart(request)
    if not cart_obj.items.exists():
        return redirect('store:cart')

    if request.method == 'POST':
        order = Order.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            total=cart_obj.total,
            session_key=request.session.session_key,
        )
        for item in cart_obj.items.select_related('listing__seller__seller_profile').all():
            seller_name = ''
            if item.listing:
                s = item.listing.seller
                try:
                    seller_name = s.seller_profile.company_name or s.get_full_name() or s.username
                except Exception:
                    seller_name = s.username
            OrderItem.objects.create(
                order=order,
                product_name=item.item_name,
                seller_name=seller_name,
                price=item.item_price,
                quantity=item.quantity,
            )
        cart_obj.items.all().delete()
        return redirect('store:order_success', order_id=order.id)

    context = {'cart': cart_obj}
    return render(request, 'store/checkout.html', context)


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_success.html', {'order': order})


def my_orders(request):
    if not request.session.session_key:
        request.session.create()
    orders = Order.objects.filter(session_key=request.session.session_key).prefetch_related('items')
    return render(request, 'store/my_orders.html', {'orders': orders})


def search(request):
    query = request.GET.get('q', '')
    if query:
        products = available_products(
            Product.objects.filter(
                Q(name__icontains=query) | Q(brand__icontains=query) | Q(description__icontains=query)
            ).select_related('category')
        )
    else:
        products = Product.objects.none()
    context = {'products': products, 'query': query}
    return render(request, 'store/search.html', context)
