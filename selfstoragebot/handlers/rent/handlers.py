import logging
import re

from telegram import Update
from telegram.ext import (
    ConversationHandler,
)

from selfstoragebot.handlers.rent import static_text
from .keyboard_utils import (make_choose_keyboard, make_keyboard_with_addresses, make_yes_no_keyboard)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ORDER, OPTION, OUR_DELIVERY, ADDRESS, EMAIL, PHONE = range(6)


def ask_pd(update: Update, _):
    print('ask_pd')
    text = static_text.pd
    update.message.reply_text(
        text,
        reply_markup=make_yes_no_keyboard()
    )
    return OPTION


def send_message_with_addresses(update: Update, _):
    print('send_message_with_addresses')
    answer = update.message.text
    if static_text.choose_option.index(answer) == 0:
        text = static_text.choose_address
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_addresses(),
        )
        return ADDRESS
    else:
        return OUR_DELIVERY


def delivery_options(update: Update):
    print('delivery_options')
    answer = update.message.text
    if static_text.yes_no.index(answer) == 0:
        text = static_text.delivery_option
        update.message.reply_text(
            text,
            reply_markup=make_choose_keyboard()
        )
        return ORDER
    else:
        return ConversationHandler.END


def get_store_address(update: Update, rent_description):
    address = update.message.text
    if address not in static_text.addresses:
        text = static_text.choose_address
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_addresses(),
        )
        return ADDRESS
    rent_description.bot_data['address'] = address
    rent_description.bot_data['user_telegram_id'] = update.message.from_user.id

    text = static_text.request_email
    update.message.reply_text(
        text=text
    )
    return EMAIL


def get_user_email(update: Update, rent_description):
    print('get_user_email')
    ''' Сохраняем e-mail и запрашиваем номер телефона '''

    user = update.message.from_user
    user_email = update.message.text
    if re.search(r'@', user_email) and re.search(r'.', user_email):
        rent_description.bot_data['email'] = user_email
        logger.info('Пользователь %s ввел e-mail %s', user.first_name, user_email)
        text = static_text.request_phone
        update.message.reply_text(
            text=text
        )
        return PHONE
    update.message.reply_text('Вы ввели некорректные данные. Попробуйте еще раз')
    return EMAIL

def get_user_choice(update, context):
    return ConversationHandler.END


def pantry_delivery(update, context):
    print('pantry_delivery')
    ''' Сохраняем вид доставки вещей от клиента и спрашиваем адрес '''

    query = update.callback_query
    # variant = format_delivery_method(int(query.data))
    # query.answer()
    # query.edit_message_text(text=f"Вы выбрали: {variant}")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Введите адрес, откуда забрать вещи')
    # return USER_ADDRESS
    return ConversationHandler.END


def get_user_phone(update, context):
    print('get_user_phone')
    ''' Сохраняем номер телефона и завершаем разговор'''

    user = update.message.from_user
    user_phone = update.message.text
    logger.info('Пользователь %s ввел телефон %s', user.first_name, user_phone)
    update.message.reply_text('Давайте рассчитаем примерную стоимость хранения')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Пожалуйста, введите вес Ваших вещей (в кг.)')
    # return WEIGHT
    return ConversationHandler.END