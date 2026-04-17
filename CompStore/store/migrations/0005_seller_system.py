from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_initial_listings(apps, schema_editor):
    """Создаёт предложения продавца из существующих товаров (только при наличии суперпользователя)."""
    Product = apps.get_model('store', 'Product')
    SellerListing = apps.get_model('store', 'SellerListing')
    CartItem = apps.get_model('store', 'CartItem')
    User = apps.get_model('auth', 'User')

    # Очищаем корзины — старые CartItem ссылаются на product, которого больше нет
    CartItem.objects.all().delete()

    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        return

    for product in Product.objects.all():
        price = getattr(product, 'price', None)
        if not price:
            continue
        SellerListing.objects.get_or_create(
            product=product,
            seller=superuser,
            defaults={
                'price': price,
                'old_price': getattr(product, 'old_price', None),
                'stock': getattr(product, 'stock', 10) or 10,
                'is_active': True,
                'is_approved': True,
            },
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_pagevisit'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Профиль продавца
        migrations.CreateModel(
            name='SellerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, max_length=200, verbose_name='Компания')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='seller_profile',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Пользователь',
                )),
            ],
            options={
                'verbose_name': 'Продавец',
                'verbose_name_plural': 'Продавцы',
            },
        ),
        # 2. Предложение продавца
        migrations.CreateModel(
            name='SellerListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('old_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Старая цена')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='Остаток')),
                ('is_active', models.BooleanField(default=True, help_text='Продавец может деактивировать своё предложение', verbose_name='Активно')),
                ('is_approved', models.BooleanField(default=False, help_text='Только администратор может активировать', verbose_name='Одобрено')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='listings',
                    to='store.product',
                    verbose_name='Товар',
                )),
                ('seller', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='listings',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Продавец',
                )),
            ],
            options={
                'verbose_name': 'Предложение продавца',
                'verbose_name_plural': 'Предложения продавцов',
                'ordering': ['price'],
                'unique_together': {('product', 'seller')},
            },
        ),
        # 3. Добавляем listing в CartItem (nullable)
        migrations.AddField(
            model_name='cartitem',
            name='listing',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cart_items',
                to='store.sellerlisting',
                verbose_name='Предложение',
            ),
        ),
        # 4. Данные: создаём предложения из старых товаров, чистим корзины
        migrations.RunPython(create_initial_listings, noop),
        # 5. Убираем старый product FK из CartItem
        migrations.RemoveField(model_name='cartitem', name='product'),
        # 6. Убираем price/old_price/stock из Product
        migrations.RemoveField(model_name='product', name='price'),
        migrations.RemoveField(model_name='product', name='old_price'),
        migrations.RemoveField(model_name='product', name='stock'),
    ]
