# Generated by Django 4.2 on 2023-04-24 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstoragebot', '0004_clients_is_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='delivery_status',
            field=models.CharField(choices=[('0', 'Создан'), ('1', 'В работе'), ('2', 'Ожидает доставки'), ('3', 'Курьер в пути'), ('4', 'Груз на складе'), ('5', 'Возвращен'), ('6', 'Истех срок хранения')], db_index=True, default=0, max_length=15, null=True, verbose_name='Статус доставки заказа'),
        ),
    ]
