import logging
import re
import datetime

from telegram import Update
from telegram.ext import (
    ConversationHandler,
)
from selfstoragebot.models import Clients, Orders
from selfstoragebot.handlers.rent import static_text
from .keyboard_utils import (
    make_choose_keyboard,
    make_keyboard_with_addresses,
    make_yes_no_keyboard,
    make_keyboard_with_orders,
    make_keyboard_return
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ORDER, OPTION, OUR_DELIVERY, ADDRESS, EMAIL, PHONE, WEIGHT, VOLUME, PERIOD, NAME, BOX_DETAIL = range(11)


def ask_pd(update: Update, _):
    print('ask_pd')
    text = static_text.pd
    update.message.reply_text(
        text,
        reply_markup=make_yes_no_keyboard()
    )
    return ADDRESS


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


def delivery_options(update: Update, rent_description):
    print('delivery_options')
    answer = update.message.text
    if static_text.choose_option.index(answer) == 0:
        text = static_text.request_email
        rent_description.bot_data['type_delivery'] = 0
        update.message.reply_text(
            text
        )
        return EMAIL
    else:
        text = static_text.request_address_to
        update.message.reply_text(
            text
        )
        return OUR_DELIVERY


def get_store_address(update: Update, rent_description):
    print('get_store_address')
    address = update.message.text
    print(address)
    if address not in static_text.addresses:
        text = static_text.choose_address
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_addresses(),
        )
        return ADDRESS
    rent_description.bot_data['address'] = address
    rent_description.bot_data['user_telegram_id'] = update.message.from_user.id

    text = static_text.delivery_option
    update.message.reply_text(
        text=text,
        reply_markup=make_choose_keyboard()
    )
    return OPTION


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


def get_user_choice(update, _):
    print('get_user_choice')
    user = update.message.from_user
    user_id = user.id
    orders = fetch_active_orders(user_id)
    reply_markup = make_keyboard_with_orders(orders)
    if orders:
        text = static_text.order_list
    else:
        text = static_text.empty_orders
    update.message.reply_text(
            text=text,
            reply_markup=reply_markup
        )
    return BOX_DETAIL


def exit(update, _):
    first_name = update.message.from_user.first_name
    text = static_text.bye_bye.format(
            first_name=first_name
    )
    update.message.reply_text(text=text)
    return CommandHandler.END


def show_detail_box(update: Update, context):
    query = update.callback_query
    user = query.from_user
    if query.data == 'back':
        command_cancel(update, rent_description)
    else:    
        reply_markup = make_keyboard_return()
        order_id = query.data
        order = Orders.objects.get(id=order_id)
        name = order.name
        address = order.warehouse
        data_end = get_date_end(order.order_date, order.store_duration)
        # name = rent_description['name']
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'{name}\nАдрес: {address}\nХраним до: {data_end}',
            reply_markup=reply_markup
        )
    return CommandHandler.END


def pantry_delivery(update: Update, rent_description):
    ''' Cпрашиваем исходящий адрес '''

    print('pantry_delivery')
    address_from = update.message.text
    user = update.message.from_user
    rent_description.bot_data['address_from'] = address_from
    rent_description.bot_data['type_delivery'] = '1'
    logger.info('Пользователь %s ввел исходящий адрес %s', user.first_name, address_from)
    text = static_text.request_email
    update.message.reply_text(
            text=text
        )
    return EMAIL


def get_user_phone(update: Update, rent_description):
    print('get_user_phone')
    ''' Сохраняем номер телефона'''

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


def get_date_end(begin, duration):
    return begin + datetime.timedelta(days=duration*30)


def fetch_active_orders(user_id):
    user = Clients.objects.get(telegram_id=user_id)
    orders_obj = Orders.objects.filter(user=user).exclude(delivery_status=5)
    orders = []
    for order in orders_obj:
        temp_order = {}
        temp_order['id'] = order.id
        temp_order['num'] = order.num
        temp_order['name'] = order.name
        temp_order['address_from'] = order.address_from
        temp_order['date_delivery_from'] = order.date_delivery_from
        # temp_order['address_to'] = order.address_to
        # temp_order['date_delivery_to'] = order.date_delivery_to
        temp_order['date_end'] = get_date_end(order.order_date,
            order.store_duration)
        temp_order['delivery_status'] = order.delivery_status
        orders.append(temp_order)
    return orders


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


def get_good_volume(update: Update,  rent_description):
    print('handle_volume')
    volume = update.message.text.strip()
    if volume.isnumeric() and 0 < int(volume):
        rent_description.bot_data['volume'] = int(volume)
        text = static_text.request_name
        update.message.reply_text(
            text=text,

        )
        return NAME
    text = static_text.wrong_volume
    update.message.reply_text(
        text=text,

    )
    return VOLUME


def get_item_name(update: Update,  rent_description):
    print('get_item_name')
    name_item = update.message.text
    if name_item:
        rent_description.bot_data['name_item'] = name_item
        text = static_text.request_period
        update.message.reply_text(
            text=text,

        )
        return PERIOD
    text = static_text.request_name
    update.message.reply_text(
        text=text,

    )
    return NAME

def get_retention_period(update: Update,  rent_description):
    print('get_retention_period')
    months = update.message.text.strip()
    if months.isnumeric() and 0 < int(months) <= 24:
        rent_description.bot_data['months'] = int(months)

        order_weight = rent_description.bot_data['weight']
        order_volume = rent_description.bot_data['volume']
        order_cost = calculate_the_order_cost(order_weight, order_volume, int(months))

        order_cost = round(order_cost)
        rent_description.bot_data['order_cost'] = order_cost
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
        qr_filename = Orders.save_order(rent_description.bot_data)
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