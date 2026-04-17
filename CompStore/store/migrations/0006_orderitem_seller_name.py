from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_seller_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='seller_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Продавец'),
        ),
    ]
