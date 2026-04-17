import json
from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline

from .models import (
    Category, Product, SellerProfile, SellerListing,
    PrebuiltPC, PrebuiltComponent, Cart, CartItem,
    Order, OrderItem, PrebuiltLevel, PageVisit,
)

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(ModelAdmin, DjangoUserAdmin):
    add_fieldsets = DjangoUserAdmin.add_fieldsets
    fieldsets = DjangoUserAdmin.fieldsets


# ── Helpers ──────────────────────────────────────────────────────────────────

def _is_seller(user):
    return not user.is_superuser and hasattr(user, 'seller_profile')


# ── Dashboard callback ────────────────────────────────────────────────────────

def dashboard_callback(request, context):
    today = timezone.localdate()

    if _is_seller(request.user):
        listings = SellerListing.objects.filter(seller=request.user)
        context.update({
            'kpi': [
                {'label': 'Мои предложения',      'value': listings.count(),                          'icon': 'sell'},
                {'label': 'Активные',              'value': listings.filter(is_active=True).count(),   'icon': 'check_circle'},
                {'label': 'Ожидают одобрения',     'value': listings.filter(is_approved=False).count(),'icon': 'hourglass_empty'},
                {'label': 'Одобрены',              'value': listings.filter(is_approved=True).count(), 'icon': 'verified'},
            ],
            'order_statuses': [],
            'chart_labels': json.dumps([]),
            'chart_data': json.dumps([]),
        })
        return context

    visits_qs = PageVisit.objects.all()
    visits_today = visits_qs.filter(created_at__date=today).count()
    visits_week  = visits_qs.filter(created_at__date__gte=today - timedelta(days=6)).count()

    chart_labels, chart_data = [], []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime('%d.%m'))
        chart_data.append(visits_qs.filter(created_at__date=day).count())

    orders_qs    = Order.objects.all()
    orders_today = orders_qs.filter(created_at__date=today).count()
    orders_total = orders_qs.count()
    revenue      = orders_qs.exclude(status='cancelled').aggregate(s=Sum('total'))['s'] or 0

    pending_listings = SellerListing.objects.filter(is_approved=False, is_active=True).count()

    STATUS_META = {
        'pending':    ('Ожидает',      '#f59e0b'),
        'processing': ('В обработке',  '#3b82f6'),
        'shipped':    ('Отправлен',    '#8b5cf6'),
        'delivered':  ('Доставлен',    '#10b981'),
        'cancelled':  ('Отменён',      '#ef4444'),
    }
    status_counts = {row['status']: row['cnt'] for row in orders_qs.values('status').annotate(cnt=Count('id'))}
    order_statuses = [
        {
            'label': STATUS_META[s][0],
            'color': STATUS_META[s][1],
            'count': status_counts.get(s, 0),
            'link':  f'/admin/store/order/?status__exact={s}',
        }
        for s in STATUS_META
    ]

    context.update({
        'kpi': [
            {'label': 'Визитов сегодня',         'value': visits_today,  'icon': 'visibility'},
            {'label': 'Визитов за 7 дней',        'value': visits_week,   'icon': 'analytics'},
            {'label': 'Заказов сегодня',          'value': orders_today,  'icon': 'shopping_bag'},
            {'label': 'Всего заказов',            'value': orders_total,  'icon': 'receipt_long'},
            {'label': 'Выручка (сомони)',         'value': f"{int(revenue):,}".replace(',', ' '), 'icon': 'payments'},
            {'label': 'Ожидают одобрения (товары)', 'value': pending_listings, 'icon': 'pending'},
        ],
        'order_statuses': order_statuses,
        'chart_labels':   json.dumps(chart_labels),
        'chart_data':     json.dumps(chart_data),
    })
    return context


# ── Sidebar navigation ────────────────────────────────────────────────────────

def get_sidebar_navigation(request):
    if _is_seller(request.user):
        return [
            {
                'title': 'Мои товары',
                'items': [
                    {'title': 'Мои предложения', 'icon': 'sell', 'link': '/admin/store/sellerlisting/'},
                ],
            },
        ]
    return [
        {
            'title': 'Магазин',
            'items': [
                {'title': 'Номенклатура',       'icon': 'memory',         'link': '/admin/store/product/'},
                {'title': 'Категории',           'icon': 'category',       'link': '/admin/store/category/'},
                {'title': 'Предложения продавцов','icon': 'sell',          'link': '/admin/store/sellerlisting/'},
                {'title': 'Продавцы',            'icon': 'storefront',     'link': '/admin/store/sellerprofile/'},
                {'title': 'Готовые сборки',      'icon': 'desktop_windows','link': '/admin/store/prebuiltpc/'},
                {'title': 'Уровни сборок',       'icon': 'bar_chart',      'link': '/admin/store/prebuiltlevel/'},
            ],
        },
        {
            'title': 'Заказы',
            'items': [
                {'title': 'Заказы',  'icon': 'shopping_bag', 'link': '/admin/store/order/'},
                {'title': 'Корзины', 'icon': 'shopping_cart', 'link': '/admin/store/cart/'},
            ],
        },
        {
            'title': 'Аналитика',
            'items': [
                {'title': 'Посещаемость', 'icon': 'analytics', 'link': '/admin/store/pagevisit/'},
            ],
        },
        {
            'title': 'Система',
            'items': [
                {'title': 'Пользователи', 'icon': 'person', 'link': '/admin/auth/user/'},
                {'title': 'Группы',       'icon': 'group',  'link': '/admin/auth/group/'},
            ],
        },
    ]


# ── Inlines ───────────────────────────────────────────────────────────────────

class PrebuiltComponentInline(UnfoldTabularInline):
    model = PrebuiltComponent
    extra = 1
    autocomplete_fields = ['product']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product_name', 'seller_name', 'price', 'quantity', 'get_subtotal')
    readonly_fields = ('product_name', 'seller_name', 'price', 'quantity', 'get_subtotal')
    can_delete = False

    @admin.display(description='Сумма')
    def get_subtotal(self, obj):
        if obj.pk and obj.price is not None:
            return obj.subtotal
        return '—'


# ── Admin-only models ─────────────────────────────────────────────────────────

def _admin_only(cls):
    """Декоратор: доступ только суперпользователям."""
    for method in ('has_module_perms', 'has_view_permission', 'has_add_permission',
                   'has_change_permission', 'has_delete_permission'):
        setattr(cls, method, lambda self, request, obj=None: request.user.is_superuser)
    return cls


@admin.register(PrebuiltLevel)
@_admin_only
class PrebuiltLevelAdmin(ModelAdmin):
    list_display = ('name', 'color', 'order')
    list_editable = ('color', 'order')


@admin.register(Category)
@_admin_only
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'type', 'icon', 'order')
    list_editable = ('order', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
@_admin_only
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'brand', 'category', 'is_featured', 'listing_count', 'created_at')
    list_filter = ('category', 'is_featured', 'brand')
    list_editable = ('is_featured',)
    search_fields = ('name', 'brand', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('category', 'name', 'slug', 'brand', 'image', 'is_featured')}),
        ('Совместимость', {'fields': ('socket', 'ram_type')}),
        ('Описание', {'fields': ('description', 'specs')}),
    )

    @admin.display(description='Предложений')
    def listing_count(self, obj):
        approved = obj.listings.filter(is_approved=True, is_active=True).count()
        total = obj.listings.count()
        return f'{approved} / {total}'


@admin.register(SellerProfile)
@_admin_only
class SellerProfileAdmin(ModelAdmin):
    list_display = ('user', 'company_name', 'phone', 'listing_count', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone')
    autocomplete_fields = ['user']

    @admin.display(description='Предложений')
    def listing_count(self, obj):
        return obj.user.listings.count()


@admin.register(PrebuiltPC)
@_admin_only
class PrebuiltPCAdmin(ModelAdmin):
    list_display = ('name', 'level', 'price', 'is_featured', 'created_at')
    list_editable = ('price', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PrebuiltComponentInline]


STATUS_COLORS = {
    'pending':    ('Ожидает',     '#f59e0b'),
    'processing': ('В обработке', '#3b82f6'),
    'shipped':    ('Отправлен',   '#8b5cf6'),
    'delivered':  ('Доставлен',   '#10b981'),
    'cancelled':  ('Отменён',     '#ef4444'),
}


@admin.register(Order)
@_admin_only
class OrderAdmin(ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'city', 'total', 'status_badge', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    inlines = [OrderItemInline]
    readonly_fields = ('total', 'created_at', 'session_key')

    @admin.display(description='Статус', ordering='status')
    def status_badge(self, obj):
        label, color = STATUS_COLORS.get(obj.status, (obj.status, '#6b7280'))
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:6px;padding:3px 10px;'
            'border-radius:20px;font-size:0.75rem;font-weight:600;'
            'background:{}22;color:{}">'
            '<span style="width:6px;height:6px;border-radius:50%;background:{}"></span>{}'
            '</span>',
            color, color, color, label,
        )


@admin.register(Cart)
@_admin_only
class CartAdmin(ModelAdmin):
    pass


@admin.register(PageVisit)
@_admin_only
class PageVisitAdmin(ModelAdmin):
    list_display = ('path', 'ip_address', 'short_agent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('path', 'ip_address', 'session_key')
    readonly_fields = ('path', 'session_key', 'ip_address', 'user_agent', 'referer', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='User Agent')
    def short_agent(self, obj):
        return obj.user_agent[:70] + '…' if len(obj.user_agent) > 70 else obj.user_agent

    def changelist_view(self, request, extra_context=None):
        today = timezone.localdate()
        qs = PageVisit.objects.all()

        stats = {
            'today':        qs.filter(created_at__date=today).count(),
            'yesterday':    qs.filter(created_at__date=today - timedelta(days=1)).count(),
            'week':         qs.filter(created_at__date__gte=today - timedelta(days=6)).count(),
            'month':        qs.filter(created_at__date__gte=today - timedelta(days=29)).count(),
            'total':        qs.count(),
            'unique_today': qs.filter(created_at__date=today).exclude(session_key='').values('session_key').distinct().count(),
            'unique_week':  qs.filter(created_at__date__gte=today - timedelta(days=6)).exclude(session_key='').values('session_key').distinct().count(),
        }

        labels, data = [], []
        for i in range(13, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%d.%m'))
            data.append(qs.filter(created_at__date=day).count())

        top_pages = (
            qs.filter(created_at__date__gte=today - timedelta(days=6))
              .values('path').annotate(cnt=Count('id')).order_by('-cnt')[:10]
        )

        extra_context = extra_context or {}
        extra_context.update({
            'visit_stats':  stats,
            'chart_labels': json.dumps(labels),
            'chart_data':   json.dumps(data),
            'top_pages':    top_pages,
        })
        return super().changelist_view(request, extra_context=extra_context)


# ── SellerListing Admin ───────────────────────────────────────────────────────

@admin.register(SellerListing)
class SellerListingAdmin(ModelAdmin):
    list_display = ('product', 'seller_name', 'price', 'stock', 'is_active', 'approval_badge', 'created_at')
    list_filter = ('is_approved', 'is_active')
    search_fields = ('product__name', 'seller__username')
    list_editable = ('price', 'stock', 'is_active')

    def get_list_editable(self, request):
        if request.user.is_superuser:
            return ('price', 'stock', 'is_active', 'is_approved')
        return ('price', 'stock', 'is_active')

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('product', 'seller_name', 'price', 'stock', 'is_active', 'approval_badge', 'created_at')
        return ('product', 'price', 'stock', 'is_active', 'approval_badge', 'created_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('product', 'seller')
        if request.user.is_superuser:
            return qs
        return qs.filter(seller=request.user)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        if obj:
            return ('seller', 'product', 'is_approved', 'created_at')
        return ('seller', 'is_approved')

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (
                (None, {'fields': ('product', 'seller')}),
                ('Цена и наличие', {'fields': ('price', 'old_price', 'stock')}),
                ('Статус', {'fields': ('is_active', 'is_approved')}),
            )
        return (
            (None, {'fields': ('product',)}),
            ('Цена и наличие', {'fields': ('price', 'old_price', 'stock')}),
            ('Статус', {'fields': ('is_active',)}),
        )

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change:
            obj.seller = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.seller == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.seller == request.user

    def has_module_perms(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.seller == request.user

    @admin.display(description='Продавец')
    def seller_name(self, obj):
        try:
            return obj.seller.seller_profile.company_name or obj.seller.username
        except Exception:
            return obj.seller.username

    @admin.display(description='Одобрено', ordering='is_approved')
    def approval_badge(self, obj):
        if obj.is_approved:
            return mark_safe('<span style="color:#10b981;font-weight:600">✓ Одобрено</span>')
        return mark_safe('<span style="color:#f59e0b;font-weight:600">⏳ Ожидает</span>')


# ── CartItem Admin (admin only) ───────────────────────────────────────────────

@admin.register(CartItem)
@_admin_only
class CartItemAdmin(ModelAdmin):
    pass


admin.site.site_header = 'CompStore'
admin.site.site_title  = 'CompStore Admin'
admin.site.index_title = 'Управление магазином'
