import json
from datetime import timedelta

from django.contrib import admin
from django.db.models import Count
from django.utils import timezone

from .models import (
    Category, Product, PrebuiltPC, PrebuiltComponent,
    Cart, CartItem, Order, OrderItem, PrebuiltLevel, PageVisit,
)


@admin.register(PrebuiltLevel)
class PrebuiltLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'order')
    list_editable = ('color', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'icon', 'order')
    list_editable = ('order', 'icon')
    prepopulated_fields = {'slug': ('name',)}


class PrebuiltComponentInline(admin.TabularInline):
    model = PrebuiltComponent
    extra = 1
    autocomplete_fields = ['product']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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
class PrebuiltPCAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'price', 'is_featured', 'created_at')
    list_editable = ('price', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PrebuiltComponentInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity', 'subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'city', 'total', 'status', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    list_editable = ('status',)
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    inlines = [OrderItemInline]
    readonly_fields = ('total', 'created_at', 'session_key')


admin.site.register(Cart)
admin.site.register(CartItem)


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
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
        today = timezone.localdate()  # дата в локальном часовом поясе (Asia/Tashkent)

        qs = PageVisit.objects.all()

        stats = {
            'today':          qs.filter(created_at__date=today).count(),
            'yesterday':      qs.filter(created_at__date=today - timedelta(days=1)).count(),
            'week':           qs.filter(created_at__date__gte=today - timedelta(days=6)).count(),
            'month':          qs.filter(created_at__date__gte=today - timedelta(days=29)).count(),
            'total':          qs.count(),
            'unique_today':   qs.filter(created_at__date=today)
                               .exclude(session_key='').values('session_key').distinct().count(),
            'unique_week':    qs.filter(created_at__date__gte=today - timedelta(days=6))
                               .exclude(session_key='').values('session_key').distinct().count(),
        }

        # Chart: last 14 days
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
            'visit_stats':   stats,
            'chart_labels':  json.dumps(labels),
            'chart_data':    json.dumps(data),
            'top_pages':     top_pages,
        })
        return super().changelist_view(request, extra_context=extra_context)


admin.site.site_header = 'CompStore — Панель управления'
admin.site.site_title = 'CompStore Admin'
admin.site.index_title = 'Управление магазином'
