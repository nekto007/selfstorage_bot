from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

from selfstoragebot.handlers.admin import static_text
from selfstoragebot.models import Clients, Orders
from .keyboard_utils import make_keyboard_with_admin_features


def command_admin(update: Update, _):
    print('command_admin')
    user = Clients.objects.get(telegram_id=update.message.from_user.id)
    if not user.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return ConversationHandler.END
    text = static_text.admin_features

    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_with_admin_features())
    return send_orders_statistics


def send_orders_statistics(update: Update, context: CallbackContext):
    print('send_orders_statistics')
    query = update.callback_query
    query.answer()
    filter_orders = Orders.objects.filter(delivery_status=6)
    context.bot.sendMessage(chat_id=query.from_user.id, text='Номера просроченных заказов:')
    for order in filter_orders:
        url = f'<a href="{static_text.admin_url}selfstoragebot/orders/{order.id}/">{order.num}</a>'
        context.bot.sendMessage(chat_id=query.from_user.id, text=url,
                                parse_mode=ParseMode.HTML)



