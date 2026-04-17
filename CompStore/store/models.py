from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('cpu', 'Процессор'),
        ('gpu', 'Видеокарта'),
        ('ram', 'Оперативная память'),
        ('motherboard', 'Материнская плата'),
        ('storage', 'Накопитель'),
        ('psu', 'Блок питания'),
        ('case', 'Корпус'),
        ('cooling', 'Охлаждение'),
        ('other', 'Другое'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    icon = models.CharField(max_length=50, default='bi-cpu')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Номенклатура товаров — создаётся только администратором."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    brand = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(blank=True)
    specs = models.JSONField(default=dict, blank=True)
    SOCKET_CHOICES = [
        ('', 'Не применимо'),
        ('AM1',   'AMD AM1'), ('AM2',   'AMD AM2'), ('AM2+',  'AMD AM2+'),
        ('AM3',   'AMD AM3'), ('AM3+',  'AMD AM3+'), ('AM4',   'AMD AM4'),
        ('AM5',   'AMD AM5'), ('FM1',   'AMD FM1'), ('FM2',   'AMD FM2'),
        ('FM2+',  'AMD FM2+'), ('SP3',   'AMD SP3 (EPYC)'), ('SP5',   'AMD SP5 (EPYC)'),
        ('TR4',   'AMD TR4 (Threadripper)'), ('TRX40', 'AMD TRX40 (Threadripper)'),
        ('TRX50', 'AMD TRX50 (Threadripper)'),
        ('LGA775',  'Intel LGA775'), ('LGA1150', 'Intel LGA1150'), ('LGA1151', 'Intel LGA1151'),
        ('LGA1155', 'Intel LGA1155'), ('LGA1156', 'Intel LGA1156'), ('LGA1200', 'Intel LGA1200'),
        ('LGA1700', 'Intel LGA1700'), ('LGA1851', 'Intel LGA1851'), ('LGA2011', 'Intel LGA2011'),
        ('LGA2011-3', 'Intel LGA2011-3'), ('LGA2066', 'Intel LGA2066 (HEDT)'),
        ('LGA4189', 'Intel LGA4189 (Xeon)'), ('LGA4677', 'Intel LGA4677 (Xeon)'),
    ]
    RAM_TYPE_CHOICES = [
        ('', 'Не применимо'), ('DDR3', 'DDR3'), ('DDR4', 'DDR4'), ('DDR5', 'DDR5'),
    ]
    socket = models.CharField(max_length=50, blank=True, choices=SOCKET_CHOICES)
    ram_type = models.CharField(max_length=10, blank=True, choices=RAM_TYPE_CHOICES)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Номенклатура'
        verbose_name_plural = 'Номенклатура товаров'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile', verbose_name='Пользователь')
    company_name = models.CharField('Компания', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'

    def __str__(self):
        return self.company_name or self.user.username


class SellerListing(models.Model):
    """Предложение продавца — цена и остаток для конкретного товара из номенклатуры."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='listings', verbose_name='Товар')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', verbose_name='Продавец')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField('Остаток', default=0)
    is_active = models.BooleanField('Активно', default=True, help_text='Продавец может деактивировать своё предложение')
    is_approved = models.BooleanField('Одобрено', default=False, help_text='Только администратор может активировать')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Предложение продавца'
        verbose_name_plural = 'Предложения продавцов'
        unique_together = ('product', 'seller')
        ordering = ['price']

    def __str__(self):
        return f'{self.product.name} — {self.seller.username} — {self.price} сом.'

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0


class PrebuiltLevel(models.Model):
    name = models.CharField('Название', max_length=50)
    color = models.CharField('Цвет бейджа (Bootstrap)', max_length=50, default='bg-secondary')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Уровень сборки'
        verbose_name_plural = 'Уровни сборок'

    def __str__(self):
        return self.name


class PrebuiltPC(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    level = models.ForeignKey(PrebuiltLevel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Уровень')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='prebuilts/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    components = models.ManyToManyField(Product, through='PrebuiltComponent')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Готовая сборка'
        verbose_name_plural = 'Готовые сборки'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while PrebuiltPC.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class PrebuiltComponent(models.Model):
    prebuilt = models.ForeignKey(PrebuiltPC, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Компонент сборки'
        verbose_name_plural = 'Компоненты сборки'


class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    listing = models.ForeignKey(SellerListing, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Предложение')
    prebuilt = models.ForeignKey(PrebuiltPC, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'

    @property
    def item_name(self):
        return self.listing.product.name if self.listing else self.prebuilt.name

    @property
    def item_price(self):
        return self.listing.price if self.listing else self.prebuilt.price

    @property
    def subtotal(self):
        return self.item_price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} — {self.first_name} {self.last_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    seller_name = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'


class PageVisit(models.Model):
    path = models.CharField('Страница', max_length=500)
    session_key = models.CharField('Сессия', max_length=40, blank=True)
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=300, blank=True)
    referer = models.CharField('Источник', max_length=500, blank=True)
    created_at = models.DateTimeField('Время', auto_now_add=True)

    class Meta:
        verbose_name = 'Посещение'
        verbose_name_plural = 'Статистика посещений'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.path} — {self.created_at:%d.%m.%Y %H:%M}'
