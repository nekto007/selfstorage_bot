import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selfstorage.settings')
django.setup()

from selfstoragebot.models import Warehouses
from db_data_examples import (
    warehouses
)


def init():
    for city, address in warehouses.items():
        Warehouses.objects.get_or_create(
            name=city,
            address=address
        )


if __name__ == '__main__':
    init()
