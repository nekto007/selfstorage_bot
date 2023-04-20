from django.contrib import admin

from .models import Clients, Goods, Orders, Warehouses


class ClientsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'telegram_id', 'username', 'first_name', 'last_name',
    ]
    search_fields = ['telegram_id', 'username', 'last_name']


class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'address',
    ]


class GoodsAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'seasonal', 'week_tariff', 'month_tariff',
    ]


class OrdersAdmin(admin.ModelAdmin):
    list_display = [
        'num', 'order_date', 'warehouse', 'user', 'seasonal_store',
        'good',
    ]
    list_filter = ['warehouse']
    fields = [
        'order_date', 'warehouse', 'user', 'seasonal_store', 'good',
        'seasonal_good_count', 'store_duration',
        'store_duration_type', 'summa'
    ]


admin.site.register(Clients, ClientsAdmin)
admin.site.register(Warehouses, WarehouseAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(Orders, OrdersAdmin)
