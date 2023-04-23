import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selfstorage.settings')
django.setup()

from selfstoragebot.dispatcher import run_pooling

if __name__ == "__main__":
    run_pooling()