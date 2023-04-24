import logging
import sys

import telegram.error
from telegram import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Dispatcher, Filters, MessageHandler, Updater, CallbackQueryHandler)

from selfstorage.settings import DEBUG, TELEGRAM_TOKEN
from selfstoragebot.handlers.common import handlers as common_handlers
from selfstoragebot.handlers.rent import handlers as rent_handlers

rent_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('^(Оформить заказ)$'),
                       rent_handlers.ask_pd),
        MessageHandler(Filters.regex('^(Список действующих боксов)$'),
                       rent_handlers.get_user_choice),
        MessageHandler(Filters.regex('^(Выход)$'),
                       rent_handlers.exit),
    ],
    states={
        rent_handlers.ORDER: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.send_message_with_addresses)
        ],
        rent_handlers.OPTION: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.delivery_options)
        ],
        rent_handlers.OUR_DELIVERY: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.pantry_delivery)
        ],
        rent_handlers.ADDRESS: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_store_address)
        ],
        rent_handlers.EMAIL: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_user_email)
        ],
        rent_handlers.PHONE: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_user_phone)
        ],
        rent_handlers.WEIGHT: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_good_weight)
        ],
        rent_handlers.VOLUME: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_good_volume)
        ],
        rent_handlers.NAME: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_item_name)
        ],
        rent_handlers.PERIOD: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_retention_period)
        ],
        rent_handlers.BOX_DETAIL: [
            CallbackQueryHandler(rent_handlers.show_detail_box)
        ]
    },
    fallbacks=[
        CommandHandler("cancel", common_handlers.command_cancel)
    ]
    #
)


def setup_dispatcher(dp):
    dp.add_handler(rent_handler)

    dp.add_handler(CommandHandler("start", common_handlers.command_start))
    dp.add_handler(CommandHandler("cancel", common_handlers.command_cancel))
    dp.add_handler(CommandHandler("faq", common_handlers.show_faq))

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f'https://t.me/{bot_info["username"]}'

    print(f"Pooling of '{bot_link}' started")

    updater.start_polling()
    updater.idle()


bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)

n_workers = 1 if DEBUG else 4
dispatcher = setup_dispatcher(
    Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True)
)
