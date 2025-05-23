# Generated by Django 5.1.7 on 2025-04-06 09:25

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Обрабатывается'), ('SHIPPED', 'Отправлен'), ('DELIVERED', 'Доставлен'), ('CANCELLED', 'Отменён')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_percent',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('method', models.CharField(choices=[('CARD', 'Кредитная карта'), ('CASH_ON_DELIVERY', 'Наложенный платеж'), ('PAYPAL', 'PayPal')], max_length=50)),
                ('status', models.CharField(choices=[('PENDING', 'Ожидает'), ('COMPLETED', 'Завершён'), ('FAILED', 'Неудача')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='store.order')),
            ],
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
