from django.contrib import admin
from .models import Category, Product, PrebuiltPC, PrebuiltComponent, Cart, CartItem, Order, OrderItem, PrebuiltLevel


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
        ('Описание', {'fields': ('description', 'specs', 'socket')}),
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

admin.site.site_header = 'CompStore — Панель управления'
admin.site.site_title = 'CompStore Admin'
admin.site.index_title = 'Управление магазином'
