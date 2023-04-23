import uuid

import qrcode
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Warehouses(UUIDMixin, TimeStampedMixin):
    name = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Name')
    address = models.CharField(
        max_length=1024,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Warehouse Address')

    class Meta:
        db_table = "warehouse"
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')

    def __str__(self):
        return f'{self.name}'


class Clients(UUIDMixin, TimeStampedMixin):
    telegram_id = models.IntegerField(unique=True)
    username = models.CharField(
        max_length=64,
        null=True,
        blank=False,
        verbose_name='User Name'
    )
    first_name = models.CharField(
        max_length=256,
        null=True,
        blank=False,
        verbose_name='First Name'
    )
    middle_name = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name='Middle Name'
    )
    last_name = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name='Last Name'
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Phone Number'
    )
    is_admin = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        verbose_name='Администратор'
    )

    def __str__(self):
        if self.username:
            return f'@{self.username}'
        else:
            return f'{self.telegram_id}'

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'


class Goods(UUIDMixin, TimeStampedMixin):
    name = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Name goods'
    )
    seasonal = models.BooleanField(
        null=False,
        default=False,
        verbose_name='Сезонная вещь'
    )
    week_tariff = models.IntegerField(
        null=False,
        default=0,
        verbose_name='Storage price per week'
    )
    month_tariff = models.IntegerField(
        null=False,
        default=0,
        verbose_name='Storage price per month'
    )

    def __str__(self):
        if self.name:
            return f'{self.name}'
        else:
            return f'{self.id}'

    def get_storage_tariff(self):
        cost = {}
        if self.week_tariff > 0:
            cost['week_tariff'] = self.week_tariff
        if self.month_tariff > 0:
            cost['month_tariff'] = self.month_tariff
        return cost

    def get_storage_cost(
            self,
            duration: int,
            is_month: bool,
            count: int
    ):

        if self.seasonal:
            if is_month:
                cost = int(duration) * self.month_tariff * int(count)
            else:
                cost = int(duration) * self.week_tariff * int(count)
        else:
            if int(count) > 1:
                cost = self.week_tariff * int(duration) + \
                       self.month_tariff * (int(count) - 1) * int(duration)
            else:
                cost = self.week_tariff * int(duration)
        return cost

    class Meta:
        verbose_name = 'Stored item'
        verbose_name_plural = 'Stored items'


class Orders(models.Model):
    class DurationType(models.TextChoices):
        week = '0', _('week')
        month = '1', _('month')

    num = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False,
        default='1',
        verbose_name='Order number')
    order_date = models.DateField(
        null=False,
        default=timezone.now,
        verbose_name='Order Date')
    warehouse = models.ForeignKey(
        Warehouses,
        on_delete=models.CASCADE,
        default=None,
        related_name='orders',
        verbose_name='Warehouse')
    user = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Client')
    seasonal_store = models.BooleanField(
        null=False,
        default=False,
        verbose_name='Seasonal items')
    good = models.ForeignKey(
        Goods,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Stored item')
    other_type_size = models.IntegerField(
        null=True,
        default=0,
        verbose_name='Cell size')
    seasonal_goods_count = models.IntegerField(
        null=True,
        verbose_name='Number of seasonal items')
    store_duration = models.IntegerField(
        null=True,
        verbose_name='Duration of storage')
    store_duration_type = models.CharField(
        max_length=1,
        choices=DurationType.choices,
        default='0',
        verbose_name='Unit of storage time')
    cost = models.FloatField(
        null=False,
        default=0,
        verbose_name='Storage cost')

    def __str__(self):
        return self.get_order_num(self.id, self.user)

    @staticmethod
    def get_order_num(order_id, user):
        return f'{order_id}-{user.telegram_id}-' \
               f'{timezone.now().strftime("%Y%m%d%H%M%S")}'

    def create_qr_code(self):
        data = self.get_order_num(self.id, self.user)
        filename = f'{data}.png'
        qrcode.make(data).save(filename)
        return filename

    @classmethod
    def save_order(cls, order_values):
        seasonal_things_count = 0
        other_type_size = 0
        is_month = '1' if order_values['period_name'] == 'month' else '0'
        is_seasonal = True if order_values['category'] == 'Seasonal items' else \
            False

        if is_seasonal:
            thing = Goods.objects.get(
                name=order_values['stuff_category'])
            seasonal_things_count = int(order_values['stuff_count'])
        else:
            thing = Goods.objects.get(name=order_values['category'])
            other_type_size = int(order_values['dimensions'])

        user = Clients.objects.get(
            telegram_id=order_values['user_telegram_id'])

        new_order = Orders(
            order_num=Orders.get_order_num(1, user),
            storage=Warehouses.objects.get(name=order_values['address']),
            user=user,
            thing=thing
        )
        new_order.seasonal_store = is_seasonal
        new_order.store_duration = int(order_values['period_count'])
        new_order.store_duration_type = is_month
        new_order.seasonal_goods_count = int(seasonal_things_count)
        new_order.other_type_size = int(other_type_size)
        new_order.save()
        new_order.order_num = Orders.get_order_num(new_order.id, user)
        new_order.summa = thing.get_storage_cost(
            int(order_values['period_count']),
            True if is_month == '1' else False,
            new_order.seasonal_goods_count if is_seasonal else new_order.other_type_size
        )
        new_order.save()
        return new_order.create_qr_code()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
