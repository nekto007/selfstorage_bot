import logging
import re
import datetime
import os
from dateutil.relativedelta import relativedelta
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler
)
from selfstorage.settings import BASE_DIR
from selfstoragebot.models import Clients, Orders
from selfstoragebot.handlers.rent import static_text
from .keyboard_utils import (
    make_choose_keyboard,
    make_keyboard_with_addresses,
    make_yes_no_keyboard,
    make_keyboard_with_orders,
    make_keyboard_return,
    make_keyboard_delivery
)
from ..common.handlers import command_start

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ORDER, OPTION, OUR_DELIVERY, ADDRESS, EMAIL, PHONE, WEIGHT, VOLUME, PERIOD, NAME, BOX_DETAIL, AGREE_DISAGREE, RETURN_METHOD, BOXES, METHOD, ADDRESS_TO = range(16)


def ask_pd(update: Update, context):
    print('ask_pd')
    text = static_text.pd
    update.message.reply_text(
        text,
        reply_markup=make_yes_no_keyboard()
    )
    return AGREE_DISAGREE


def agree_disagree_handler(update: Update, _):
    response = update.message.text

    if response == 'Не согласен':
        update.message.reply_text("Извините, для дальнейшей работы вам необходимо согласиться с приведенным выше документом.")
        return ConversationHandler.END
    elif response == 'Согласен':
        text = static_text.choose_address
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_addresses(),
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
        text = static_text.request_address_from
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


def get_user_choice(update, context):
    print('get_user_choice')
    if update.message:
        user_id = update.message.from_user.id
    else:
        user_id = context.user_data['user_id']
    orders = fetch_active_orders(user_id)
    reply_markup = make_keyboard_with_orders(orders)
    if orders:
        text = static_text.order_list
    else:
        text = static_text.empty_orders
    context.bot.send_message(
            chat_id=update.effective_chat.id,
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
    return ConversationHandler.END


def show_detail_box(update: Update, context):
    print('show_detail_box')
    query = update.callback_query
    user = query.from_user
    if query.data == 'back':
        context.user_data['user_id'] = user.id
        context.user_data['username'] = user.username
        context.user_data['first_name'] = user.first_name
        return command_start(update, context)
    else:    
        order_id = query.data
        order = Orders.objects.get(id=order_id)
        name = order.name
        address = order.warehouse
        data_end = get_date_end(order.order_date, order.store_duration)
        reply_markup = make_keyboard_return(order_id)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'{name}\nАдрес: {address}\nХраним до: {data_end}',
            reply_markup=reply_markup
        )
    return RETURN_METHOD


def ask_return_method(update: Update, context):
    print('ask_return_method')
    client_wish = update.message.text
    user = update.message.from_user
    if client_wish == static_text.return_or_no[1]:
        logger.info(f'Пользователь %s оставляет бокс без изменений', user.first_name)
        context.user_data['user_id'] = user.id
        update.message.reply_text(text='Пусть полежит')
        return get_user_choice(update, context)
    else:
        order_id = client_wish.split()[-1]
        logger.info(f'Пользователь %s хочет забрать бокс %s', user.first_name, order_id)
        order = Orders.objects.get(id=order_id)
        order.delivery_status = '2'
        order.save()
        text = static_text.request_delivery
        reply_markup = make_keyboard_delivery(order_id)
        update.message.reply_text(text=text, reply_markup=reply_markup)
        return METHOD
        

def ask_address_to(update: Update, context):
    print('ask_address_to')
    client_wish = update.message.text
    order_id = update.message.text.split()[-1]
    order = Orders.objects.get(id=order_id)
    if client_wish == static_text.deliveries[0]:
        order.type_delivery = '0'
        order.save()
        text = static_text.self_return.format(address=order.warehouse)
        update.message.reply_text(text=text)
        return ConversationHandler.END
    else:
        order.type_delivery = '1'
        order.save()
        text = static_text.request_address_to
        context.user_data['id'] = order_id
        update.message.reply_text(text=text)
        return ADDRESS_TO


def get_address_to(update: Update, context):
    print('get_address_to')
    address_to = update.message.text
    order_id = context.user_data['id']
    order = Orders.objects.get(id=order_id)
    order.address_to = address_to
    order.save()
    text = static_text.courier_return
    update.message.reply_text(text=text)
    return ConversationHandler.END


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
    if weight.isnumeric() and 0 < int(weight) < 1000:
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
    if volume.isnumeric() and 0 < int(volume) < 100:
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
        text = static_text.order_complete.format(
            first_name=rent_description.bot_data['first_name'],
            last_name=rent_description.bot_data['last_name'],
            phone_number=rent_description.bot_data['phone_number'],
            email=rent_description.bot_data['email'],
            address=rent_description.bot_data['address'],
            item=rent_description.bot_data['name_item'],
            weight=rent_description.bot_data['weight'],
            volume=rent_description.bot_data['volume'],
            period=rent_description.bot_data['months'],
        )
        update.message.reply_text(
            text=text,

        )
        period_count = rent_description.bot_data['months']
        date_from = datetime.datetime.now()
        date_to = date_from + relativedelta(months=int(period_count))
        with open(qr_filename, 'rb') as qr_file:
            caption = static_text.qr_caption.format(
                date_from=date_from.strftime('%d.%m.%Y'),
                date_to=date_to.strftime('%d.%m.%Y')
            )
            update.message.reply_document(document=qr_file,
                                          caption=caption)
        os.remove(BASE_DIR / qr_filename)
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