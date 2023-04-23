from telegram import KeyboardButton, ReplyKeyboardMarkup

from .static_text import (
    addresses, choose_option, yes_no,
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