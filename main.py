import os

from telegram import Update, Message, Bot, MessageEntity, Chat
from telegram.error import BadRequest, TelegramError
from telegram.ext import Updater, Filters, MessageHandler, CallbackContext

BLOCKLIST = [word.lower().strip() for word in (os.getenv("BLOCKLIST") or "bit.ly/").split(",")]


def default_handler(update: Update, context: CallbackContext, updater: Updater):
    message = update.effective_message
    text = message.text if message.text else message.caption
    if not text:
        return

    print(f"Message ({text}) from {update.effective_user.first_name} in {message.chat_id}")

    if is_spam(updater.bot, message, text):
        handle_spam_message(update, context, updater)


def is_spam(bot: Bot, message: Message, text: str) -> bool:
    blocked_texts = [blocktext for blocktext in BLOCKLIST if blocktext in text.lower()]
    if blocked_texts:
        print(f"delete message ({text}) due to substring(s) {blocked_texts}")
        return True

    if any(
        is_channel_mention(bot, entity, message.parse_entity)
        for entity in message.entities
    ) or any(
        is_channel_mention(bot, entity, message.parse_caption_entity)
        for entity in message.caption_entities
    ):
        print(f"delete message ({text}) due to channel mention'")
        return True

    return False


def is_channel_mention(bot: Bot, entity: MessageEntity, parse_entity) -> bool:
    if entity.type != MessageEntity.MENTION:
        return False

    mention: str = parse_entity(entity)
    try:
        chat: Chat = bot.get_chat(mention)
    except TelegramError:
        return False
    else:
        return chat.type != "private"


def handle_spam_message(update: Update, context: CallbackContext, updater: Updater):
    message = update.effective_message
    try:
        context.user_data["bot"] = True
        message.forward(chat_id=-1001448278800)
        message.delete()
        updater.bot.kick_chat_member(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
        )
    except BadRequest as e:
        print(e)


def main(token: str):
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(
        Filters.text | Filters.video | Filters.audio | Filters.photo,
        lambda u, c: default_handler(u, c, updater),
    ))
    updater.start_polling()
    updater.idle()


main(os.getenv("TOKEN"))
