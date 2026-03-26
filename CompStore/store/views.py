from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
import json

from .models import Category, Product, PrebuiltPC, PrebuiltLevel, Cart, CartItem, Order, OrderItem


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True).select_related('category')[:8]
    featured_prebuilts = PrebuiltPC.objects.filter(is_featured=True)[:3]
    new_products = Product.objects.order_by('-created_at')[:8]
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'featured_prebuilts': featured_prebuilts,
        'new_products': new_products,
    }
    return render(request, 'store/home.html', context)


def catalog(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.select_related('category').all()
    current_category = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name': 'name',
        '-created_at': '-created_at',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    context = {
        'categories': categories,
        'products': products,
        'current_category': current_category,
        'current_sort': sort,
    }
    return render(request, 'store/catalog.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    context = {
        'product': product,
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
        products_by_category[cat.type] = [
            {
                'id': p.id,
                'name': p.name,
                'brand': p.brand,
                'price': float(p.price),
                'socket': p.socket,
                'ram_type': p.ram_type,
                'specs': p.specs,
            }
            for p in Product.objects.filter(category=cat)
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
    product_id = request.POST.get('product_id')
    prebuilt_id = request.POST.get('prebuilt_id')
    quantity = int(request.POST.get('quantity', 1))

    if product_id:
        product = get_object_or_404(Product, pk=product_id)
        item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product, prebuilt=None)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        messages.success(request, f'«{product.name}» добавлен в корзину.')
    elif prebuilt_id:
        prebuilt = get_object_or_404(PrebuiltPC, pk=prebuilt_id)
        item, created = CartItem.objects.get_or_create(cart=cart_obj, prebuilt=prebuilt, product=None)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        messages.success(request, f'«{prebuilt.name}» добавлен в корзину.')
    elif request.POST.get('builder_items'):
        try:
            items = json.loads(request.POST.get('builder_items'))
            for item_data in items:
                product = get_object_or_404(Product, pk=item_data['id'])
                item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product, prebuilt=None)
                if not created:
                    item.quantity += 1
                item.save()
            messages.success(request, 'Сборка добавлена в корзину!')
        except (json.JSONDecodeError, KeyError):
            pass

    next_url = request.POST.get('next', '/')
    return redirect(next_url)


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
        for item in cart_obj.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.item_name,
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


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(brand__icontains=query) | Q(description__icontains=query)
    ).select_related('category') if query else Product.objects.none()
    context = {'products': products, 'query': query}
    return render(request, 'store/search.html', context)
