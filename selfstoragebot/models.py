import uuid

import qrcode
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class InvitationLink(models.Model):
    link_id = models.CharField(max_length=255, unique=True)
    click_count = models.IntegerField(default=0)


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

    class Meta:
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'


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
    email = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='email'
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


class Orders(models.Model):
    class Status(models.TextChoices):
        created = '0', _('Создан')
        in_progress = '1', _('В работе')
        waiting_for_delivery = '2', _('Ожидает доставки')
        in_route = '3', _('Курьер в пути')
        Completed = '4', _('Груз на складе')
        retrieved = '5', _('Возвращен')
        expired = '6', _('Истех срок хранения')

    class TypeDelivery(models.TextChoices):
        yourself = '0', _('Самостоятельно')
        сourier = '1', _('Курьером')

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
    weight = models.IntegerField(
        null=True,
        default=0,
        verbose_name='Weight of item')
    volume = models.IntegerField(
        null=True,
        default=0,
        verbose_name='Volume of item')
    store_duration = models.IntegerField(
        null=True,
        verbose_name='Duration of storage')
    name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Name of item'
    )
    cost = models.FloatField(
        null=False,
        default=0,
        verbose_name='Storage cost')
    address_from = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Address of picking up'
    )
    date_delivery_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date of delivery to the warehouse'
    )
    delivery_status = models.CharField(
        "Статус доставки заказа",
        null=True,
        max_length=15,
        choices=Status.choices,
        default=0,
        db_index=True,
    )
    type_delivery = models.CharField(
        "Тип доставки",
        null=True,
        max_length=15,
        choices=TypeDelivery.choices,
        db_index=True,
    )

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

        user = Clients.objects.get(
            telegram_id=order_values['user_telegram_id'])
        new_order = Orders(
            num=Orders.get_order_num(1, user),
            warehouse=Warehouses.objects.get(name=order_values['address']),
            user=user
        )
        new_order.weight = order_values['weight']
        new_order.volume = order_values['volume']
        new_order.name = order_values['name_item']
        new_order.store_duration = int(order_values['months'])
        new_order.num = Orders.get_order_num(new_order.id, user)
        new_order.cost = order_values['order_cost']
        new_order.type_delivery = order_values['type_delivery']
        if order_values.get('address_from'):
            new_order.address_from = order_values['address_from']
        new_order.save()
        return new_order.create_qr_code()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
