import os
import re

from telegram import Update, Message, Bot, MessageEntity, Chat
from telegram.error import BadRequest, TelegramError
from telegram.ext import Updater, Filters, MessageHandler, CallbackContext

BLOCKLIST = [word.lower().strip() for word in (os.getenv("BLOCKLIST") or "bit.ly/").split(",")]


def new_member_handler(update: Update):
    update.effective_message.delete()


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
        is_spam_entity(bot, entity, message.parse_entity)
        for entity in message.entities
    ) or any(
        is_spam_entity(bot, entity, message.parse_caption_entity)
        for entity in message.caption_entities
    ):
        print(f"delete message ({text}) due to channel mention'")
        return True

    return False


def is_spam_entity(bot: Bot, entity: MessageEntity, parse_entity) -> bool:
    parsed_entity: str = parse_entity(entity)
    if entity.type == MessageEntity.MENTION:
        return is_spam_mention(bot, parsed_entity)
    if entity.type == MessageEntity.PHONE_NUMBER:
        return is_spam_phone_number(parsed_entity)
    return False


def is_spam_mention(bot: Bot, mention: str) -> bool:
    try:
        chat: Chat = bot.get_chat(mention)
    except TelegramError:
        return False
    else:
        return chat.type != "private"


def is_spam_phone_number(number: str) -> bool:
    # Match +33 or 033 (with any number of leading zeroes)
    return bool(re.fullmatch(r"^(\+|0+)33.*", number))


def handle_spam_message(update: Update, context: CallbackContext, updater: Updater):
    message = update.effective_message
    try:
        context.user_data["bot"] = True
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
    dispatcher.add_handler(MessageHandler(
        Filters.status_update.new_chat_members,
        lambda u, _: new_member_handler(u),
    ))

    updater.start_polling()
    updater.idle()


main(os.getenv("BOT_TOKEN"))
