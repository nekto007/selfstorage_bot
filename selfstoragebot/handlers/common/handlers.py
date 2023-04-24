from telegram import Update
from telegram.ext import (
    ConversationHandler,
)

from selfstoragebot.handlers.common import static_text
from selfstoragebot.models import Clients
from .keyboard_utils import make_keyboard_for_start_command


def command_start(update: Update, _):
    print('command_start')
    user_info = update.message.from_user.to_dict()
    user, created = Clients.objects.get_or_create(
        telegram_id=user_info['id'],
        username=user_info['username'],
    )

    if created:
        text = static_text.start_created.format(
            first_name=user_info['first_name']
        )
    else:
        text = static_text.start_not_created.format(
            first_name=user_info['first_name']
        )

    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_start_command(),
    )


def command_cancel(update: Update, _):
    print('command_cancel')
    text = static_text.cancel_text
    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_start_command(),
    )
    return ConversationHandler.END


def show_faq(update, _):
    ''' Часто задаваемые вопросы '''

    text = static_text.faq
    update.message.reply_text(
        text=text,
        parse_mode='HTML',
    )
    return ConversationHandler.END


def show_permitted_items(update, _):
    ''' Список разрешенных вещей '''

    text = static_text.permitted_items
    update.message.reply_text(
        text=text,
        parse_mode='HTML',
    )
    return ConversationHandler.END