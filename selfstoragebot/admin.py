from django.contrib import admin

from .models import Clients, Orders, Warehouses, InvitationLink


class ClientsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'telegram_id', 'username', 'first_name', 'last_name',
    ]
    search_fields = ['telegram_id', 'username', 'last_name']


class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'address',
    ]


class OrdersAdmin(admin.ModelAdmin):
    list_display = [
        'num', 'order_date', 'warehouse', 'user', 'name',
    ]
    list_filter = ['warehouse']
    fields = [
        'order_date', 'warehouse', 'user', 'name',
        'weight', 'volume', 'store_duration', 'cost'
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