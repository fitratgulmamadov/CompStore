import json
from datetime import timedelta

from django.contrib import admin
from django.db.models import Count, Sum
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Category, Product, PrebuiltPC, PrebuiltComponent,
    Cart, CartItem, Order, OrderItem, PrebuiltLevel, PageVisit,
)


# ── Dashboard callback ──────────────────────────────────────────────────────

def dashboard_callback(request, context):
    today = timezone.localdate()

    # Статистика посещений
    visits_qs = PageVisit.objects.all()
    visits_today = visits_qs.filter(created_at__date=today).count()
    visits_week  = visits_qs.filter(created_at__date__gte=today - timedelta(days=6)).count()

    # График посещений за 14 дней
    chart_labels, chart_data = [], []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime('%d.%m'))
        chart_data.append(visits_qs.filter(created_at__date=day).count())

    # Статистика заказов
    orders_qs    = Order.objects.all()
    orders_today = orders_qs.filter(created_at__date=today).count()
    orders_total = orders_qs.count()
    revenue      = orders_qs.exclude(status='cancelled').aggregate(s=Sum('total'))['s'] or 0

    # Разбивка по статусам
    STATUS_META = {
        'pending':    ('Ожидает',      '#f59e0b'),
        'processing': ('В обработке',  '#3b82f6'),
        'shipped':    ('Отправлен',    '#8b5cf6'),
        'delivered':  ('Доставлен',    '#10b981'),
        'cancelled':  ('Отменён',      '#ef4444'),
    }
    status_counts = {
        row['status']: row['cnt']
        for row in orders_qs.values('status').annotate(cnt=Count('id'))
    }
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
        "kpi": [
            {"label": "Визитов сегодня",  "value": visits_today, "icon": "visibility"},
            {"label": "Визитов за 7 дней","value": visits_week,  "icon": "analytics"},
            {"label": "Заказов сегодня",  "value": orders_today, "icon": "shopping_bag"},
            {"label": "Всего заказов",    "value": orders_total, "icon": "receipt_long"},
            {"label": "Выручка (сомони)", "value": f"{int(revenue):,}".replace(",", " "), "icon": "payments"},
        ],
        "order_statuses": order_statuses,
        "chart_labels":   json.dumps(chart_labels),
        "chart_data":     json.dumps(chart_data),
    })
    return context


# ── Inlines ─────────────────────────────────────────────────────────────────

class PrebuiltComponentInline(TabularInline):
    model = PrebuiltComponent
    extra = 1
    autocomplete_fields = ['product']


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity', 'subtotal')


# ── ModelAdmin classes ───────────────────────────────────────────────────────

@admin.register(PrebuiltLevel)
class PrebuiltLevelAdmin(ModelAdmin):
    list_display = ('name', 'color', 'order')
    list_editable = ('color', 'order')


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'type', 'icon', 'order')
    list_editable = ('order', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured', 'brand')
    list_editable = ('price', 'stock', 'is_featured')
    search_fields = ('name', 'brand', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('category', 'name', 'slug', 'brand', 'image')}),
        ('Цены и наличие', {'fields': ('price', 'old_price', 'stock', 'is_featured')}),
        ('Совместимость', {'fields': ('socket', 'ram_type')}),
        ('Описание', {'fields': ('description', 'specs')}),
    )


@admin.register(PrebuiltPC)
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
class OrderAdmin(ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'city', 'total', 'status_badge', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    inlines = [OrderItemInline]
    readonly_fields = ('total', 'created_at', 'session_key')

    @admin.display(description='Статус', ordering='status')
    def status_badge(self, obj):
        from django.utils.html import format_html
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
class CartAdmin(ModelAdmin):
    pass


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    pass


@admin.register(PageVisit)
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
            'unique_today': qs.filter(created_at__date=today)
                             .exclude(session_key='').values('session_key').distinct().count(),
            'unique_week':  qs.filter(created_at__date__gte=today - timedelta(days=6))
                             .exclude(session_key='').values('session_key').distinct().count(),
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


admin.site.site_header = 'CompStore'
admin.site.site_title  = 'CompStore Admin'
admin.site.index_title = 'Управление магазином'
