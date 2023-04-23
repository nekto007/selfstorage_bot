import logging
import re
import phonenumbers
from telegram import Update
from telegram.ext import (
    ConversationHandler,
)
from selfstoragebot.models import Clients, Orders, Goods
from selfstoragebot.handlers.rent import static_text
from .keyboard_utils import (
    make_choose_keyboard,
    make_keyboard_with_addresses,
    make_yes_no_keyboard
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ORDER, OPTION, OUR_DELIVERY, ADDRESS, EMAIL, PHONE, WEIGHT, VOLUME, PERIOD = range(9)


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


def delivery_options(update: Update, _):
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
    print('get_store_address')
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
        rent_description.bot_data['first_name'] = user.first_name
        rent_description.bot_data['last_name'] = user.last_name
        logger.info('Пользователь %s ввел e-mail %s', user.first_name, user_email)
        text = static_text.request_phone
        update.message.reply_text(
            text=text
        )
        return PHONE
    update.message.reply_text('Вы ввели некорректные данные. Попробуйте еще раз')
    return EMAIL


def get_user_choice(update, context):
    print('get_user_choice')
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


def get_user_phone(update: Update, rent_description):
    print('get_user_phone')
    ''' Сохраняем номер телефона и завершаем разговор'''

    user = update.message.from_user
    phone_number = update.message.text
    phonenumber = phone_number.replace('+', '').replace('-', '')
    if not phonenumber.isdigit() or len(phonenumber) < 11:
        text = static_text.request_phone
        update.message.reply_text(
            text=text,

        )
        return PHONE

    logger.info('Пользователь %s ввел телефон %s', user.first_name, phonenumber)
    rent_description.bot_data['phone_number'] = phonenumber
    text = static_text.request_weight
    update.message.reply_text(
        text=text,

    )
    update_data_in_database(rent_description)
    return WEIGHT


def update_data_in_database(rent_description):
    user = Clients.objects.get(telegram_id=rent_description.bot_data['user_telegram_id'])
    user.first_name = rent_description.bot_data['first_name']
    user.last_name = rent_description.bot_data['last_name']
    user.phone_number = rent_description.bot_data['phone_number']
    user.email = rent_description.bot_data['email']
    user.save()

def get_good_weight(update: Update,  rent_description):
    print('handle_weight')
    weight = update.message.text.strip()
    if weight.isnumeric() and 0 < int(weight):
        rent_description.bot_data['weight'] = int(weight)
        text = static_text.request_volume
        update.message.reply_text(
            text=text,

        )
        return VOLUME
    text = static_text.wrong_weight
    update.message.reply_text(
        text=text,

    )
    return WEIGHT


def get_good_volume(update,  rent_description):
    print('handle_volume')
    volume = update.message.text.strip()
    if volume.isnumeric() and 0 < int(volume):
        rent_description.bot_data['volume'] = int(volume)
        text = static_text.request_period
        update.message.reply_text(
            text=text,

        )
        return PERIOD
    text = static_text.wrong_volume
    update.message.reply_text(
        text=text,

    )
    return VOLUME


def get_retention_period(update,  rent_description):
    print('handle_months')
    months = update.message.text.strip()
    if months.isnumeric() and 0 < int(months) <= 24:
        rent_description.bot_data['months'] = int(months)

        order_weight = rent_description.bot_data['weight']
        order_volume = rent_description.bot_data['volume']
        order_cost = calculate_the_order_cost(order_weight, order_volume, int(months))

        order_cost = round(order_cost)
        if order_cost is not None:
            text = static_text.order_cost.format(
            order_cost=order_cost
        )
            update.message.reply_text(
                text=text,

            )
        else:
            text = static_text.wrong_cost
            update.message.reply_text(
                text=text,

            )
            return ask_pd()
        text = static_text.order_complete
        update.message.reply_text(
            text=text,

        )
        return ConversationHandler.END
    else:
        text = static_text.wrong_period
        update.message.reply_text(
            text=text,

        )
        return PERIOD


def calculate_the_order_cost(order_weight, order_volume, months):
    print('calculate_the_order_cost')
    order_cost = 0
    initial_price = 1500

    if 0 < order_weight < 10:
        order_cost += initial_price
    elif 10 <= order_weight < 25:
        order_cost += initial_price * 1.2
    elif 25 <= order_weight < 40:
        order_cost += initial_price * 1.4
    elif 40 <= order_weight < 70:
        order_cost += initial_price * 1.6
    elif 70 <= order_weight < 100:
        order_cost += initial_price * 1.8
    elif order_weight >= 100:
        order_cost += initial_price * 2

    if 0 < order_volume < 3:
        order_cost *= 2
    elif 3 <= order_volume < 7:
        order_cost *= 2.2
    elif 7 <= order_volume < 10:
        order_cost *= 2.4
    elif 10 <= order_volume < 13:
        order_cost *= 2.6
    elif 13 <= order_volume < 17:
        order_cost *= 2.8
    elif 17 <= order_volume:
        order_cost *= 3

    return order_cost * months