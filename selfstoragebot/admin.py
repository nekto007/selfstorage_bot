from django.contrib import admin

from .models import Clients, Orders, Warehouses, InvitationLink


class ClientsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'telegram_id', 'username', 'first_name', 'last_name',
        'is_admin',
    ]
    search_fields = ['telegram_id', 'username', 'last_name']


class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'address',
    ]


class OrdersAdmin(admin.ModelAdmin):
    list_display = [
        'order_date', 'num', 'warehouse', 'user', 'name',
        'type_delivery', 'delivery_status'
    ]
    list_filter = ['warehouse']
    fields = [
        'order_date', 'num', 'warehouse', 'user', 'name',
        'weight', 'volume', 'store_duration', 'cost',
        'type_delivery', 'delivery_status', 'date_delivery_from',
        'address_from'
    ]


class InvitationLinkAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'link_id', 'click_count',
    ]
    search_fields = ['link_id']


admin.site.register(Clients, ClientsAdmin)
admin.site.register(Warehouses, WarehouseAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(InvitationLink, InvitationLinkAdmin)