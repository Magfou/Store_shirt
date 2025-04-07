# Generated by Django 5.1.7 on 2025-04-07 08:38

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_alter_review_unique_together_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={},
        ),
        migrations.RemoveIndex(
            model_name='order',
            name='store_order_user_id_75b17c_idx',
        ),
        migrations.RemoveIndex(
            model_name='order',
            name='store_order_created_4ba192_idx',
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_number',
        ),
        migrations.AddField(
            model_name='product',
            name='average_rating',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.CharField(choices=[('CARD', 'Кредитная карта'), ('CASH_ON_DELIVERY', 'Наложенный платеж'), ('PAYPAL', 'PayPal')], max_length=50),
        ),
        migrations.AlterField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='store.order'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Ожидает'), ('COMPLETED', 'Завершён'), ('FAILED', 'Неудача')], default='PENDING', max_length=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.category'),
        ),
        migrations.AlterField(
            model_name='productspecification',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specifications', to='store.product'),
        ),
        migrations.AlterField(
            model_name='productspecification',
            name='value',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='review',
            name='comment',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('product', 'user')},
        ),
    ]
