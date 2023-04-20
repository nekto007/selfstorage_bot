import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selfstorage.settings')
django.setup()

from selfstoragebot.models import Goods, Warehouses
from db_data_examples import (
    warehouses,
    goods,
)


def init():
    for city, address in warehouses.items():
        Warehouses.objects.get_or_create(
            name=city,
            address=address
        )

    for name, property in goods.items():
        Goods.objects.get_or_create(
            name=name,
            seasonal=property['seasonal'],
            week_tariff=property['week_tariff'],
            month_tariff=property['month_tariff']
        )


if __name__ == '__main__':
    init()
