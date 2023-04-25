from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from .static_text import (
    addresses, choose_option, yes_no, return_or_no, deliveries
)


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def make_yes_no_keyboard() -> ReplyKeyboardMarkup:
    print('make_yes_no_keyboard')
    buttons = [KeyboardButton(answer) for answer in yes_no]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_choose_keyboard() -> ReplyKeyboardMarkup:
    print('make_choose_keyboard')
    buttons = [KeyboardButton(choose) for choose in choose_option]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_addresses() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(address) for address in addresses]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_orders(orders):
    buttons = []
    if orders:
        buttons = [InlineKeyboardButton(order['name'], callback_data=order['id']) for \
        order in orders]
    buttons.append(InlineKeyboardButton('Назад', callback_data='back'))
    reply_markup = InlineKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_return(order_id):
    buttons = [KeyboardButton(return_.format(order_id=order_id)) for return_ in return_or_no]
    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_delivery(order_id):
    buttons = [KeyboardButton(delivery.format(order_id=order_id)) for delivery in deliveries]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup