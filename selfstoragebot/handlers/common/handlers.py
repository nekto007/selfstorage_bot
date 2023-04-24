import uuid

from telegram import Update
from telegram.ext import (
    ConversationHandler, CallbackContext
)

from selfstoragebot.handlers.common import static_text
from selfstoragebot.models import Clients, InvitationLink
from .keyboard_utils import make_keyboard_for_start_command


def command_start(update: Update, context):
    print('command_start')
    user_info = update.message.from_user.to_dict()
    user, created = Clients.objects.get_or_create(
        telegram_id=user_info['id'],
        username=user_info['username'],
    )

    args = context.args
    if args:
        link_id = args[0]
        try:
            invitation_link = InvitationLink.objects.get(link_id=link_id)
            invitation_link.click_count += 1
            invitation_link.save()
        except InvitationLink.DoesNotExist:
            pass

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


def generate_unique_link_id() -> str:
    return str(uuid.uuid4())


def generate_unique_invitation_link(bot_username: str) -> str:
    unique_link_id = generate_unique_link_id()
    invitation_link = InvitationLink(link_id=unique_link_id)
    invitation_link.save()

    invitation_url = f"https://t.me/{bot_username}?start={unique_link_id}"
    return invitation_url


def command_generate_invitation_link(update: Update, context: CallbackContext):
    bot_username = context.bot.username
    invitation_link = generate_unique_invitation_link(bot_username)
    update.message.reply_text(f"Your unique invitation link: {invitation_link}")


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