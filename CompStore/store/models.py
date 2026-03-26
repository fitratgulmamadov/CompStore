from django.db import models
from django.utils.text import slugify


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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(blank=True)
    specs = models.JSONField(default=dict, blank=True)
    SOCKET_CHOICES = [
        ('', 'Не применимо'),
        # --- AMD ---
        ('AM1',   'AMD AM1'),
        ('AM2',   'AMD AM2'),
        ('AM2+',  'AMD AM2+'),
        ('AM3',   'AMD AM3'),
        ('AM3+',  'AMD AM3+'),
        ('AM4',   'AMD AM4'),
        ('AM5',   'AMD AM5'),
        ('FM1',   'AMD FM1'),
        ('FM2',   'AMD FM2'),
        ('FM2+',  'AMD FM2+'),
        ('SP3',   'AMD SP3 (EPYC)'),
        ('SP5',   'AMD SP5 (EPYC)'),
        ('TR4',   'AMD TR4 (Threadripper)'),
        ('TRX40', 'AMD TRX40 (Threadripper)'),
        ('TRX50', 'AMD TRX50 (Threadripper)'),
        # --- Intel ---
        ('LGA775',  'Intel LGA775'),
        ('LGA1150', 'Intel LGA1150'),
        ('LGA1151', 'Intel LGA1151'),
        ('LGA1155', 'Intel LGA1155'),
        ('LGA1156', 'Intel LGA1156'),
        ('LGA1200', 'Intel LGA1200'),
        ('LGA1700', 'Intel LGA1700'),
        ('LGA1851', 'Intel LGA1851'),
        ('LGA2011', 'Intel LGA2011'),
        ('LGA2011-3', 'Intel LGA2011-3'),
        ('LGA2066', 'Intel LGA2066 (HEDT)'),
        ('LGA4189', 'Intel LGA4189 (Xeon)'),
        ('LGA4677', 'Intel LGA4677 (Xeon)'),
    ]
    RAM_TYPE_CHOICES = [
        ('',     'Не применимо'),
        ('DDR3', 'DDR3'),
        ('DDR4', 'DDR4'),
        ('DDR5', 'DDR5'),
    ]
    socket = models.CharField(max_length=50, blank=True, choices=SOCKET_CHOICES, help_text='Для совместимости CPU/MB')
    ram_type = models.CharField(max_length=10, blank=True, choices=RAM_TYPE_CHOICES, help_text='Тип RAM (для MB и RAM-планок)')
    stock = models.PositiveIntegerField(default=10)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

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

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0


class PrebuiltLevel(models.Model):
    name = models.CharField('Название', max_length=50)
    color = models.CharField('Цвет бейджа (Bootstrap)', max_length=50, default='bg-secondary',
                             help_text='Например: bg-success, bg-info, bg-warning, bg-danger')
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
    level = models.ForeignKey(PrebuiltLevel, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='Уровень')
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    prebuilt = models.ForeignKey(PrebuiltPC, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'

    @property
    def item_name(self):
        return self.product.name if self.product else self.prebuilt.name

    @property
    def item_price(self):
        return self.product.price if self.product else self.prebuilt.price

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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
