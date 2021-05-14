import os

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Updater, Filters, MessageHandler, CallbackContext

BLOCKLIST = [word.lower() for word in (os.getenv("BLOCKLIST") or "bit.ly/").split(",")]


def default_handler(update: Update, context: CallbackContext, updater: Updater):
    message = update.effective_message
    text = message.text if message.text else message.caption

    print(f"Message ({text}) from {update.effective_user.first_name} in {message.chat_id}")

    if any(blocktext in text.lower() for blocktext in BLOCKLIST):
        print(f"delete message ({text}) due to substring 'bit.ly/'")
        try:
            message.forward(chat_id=-1001448278800)
            message.delete()

            if not context.user_data["bot"]:
                updater.bot.send_message(chat_id=message.chat_id,
                                         text=f"{update.effective_user.first_name} ist ein Boot und Merts Profilbild ist fake",
                                         disable_notification=True)
            context.user_data["bot"] = True
        except BadRequest as e:
            print(e)


def main(token: str):
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.all, lambda u, c: default_handler(u, c, updater)))
    updater.start_polling()
    updater.idle()


main(os.getenv("TOKEN"))
