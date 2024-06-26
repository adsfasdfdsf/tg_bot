import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.ext.filters import Regex, COMMAND
from passwords import TOKEN

<<<<<<< HEAD
token = "6996718949:AAEk05cwz8CxJEsjk9tln8b4B4UsbBdQ95Q"
=======
token = TOKEN
>>>>>>> tmp

ADD, DELETE, ANY = range(3)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Add new stock"], ["Remove one of my stocks"], ["Show my stocks"], ["Stop conversation"]]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I'm a screener bot, I can show some statistics on "
                                        "different stocks and shares! You can choose any option and get a description",
                                   reply_markup=markup_key)
    return ANY


async def any_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "add" in update.message.text.lower():
        await update.effective_user.send_message(
            "Write a name of a stock you want to add.",
            reply_markup=ReplyKeyboardRemove())
        await update.effective_user.send_message(
            "If you want to add more than one, type the names in different "
            "messages or in one separated with ' '. To end adding type /end")
        return ADD
    if "remove" in update.message.text.lower():
        await update.effective_user.send_message(
            "Write a name of a stock you want to remove.",
            reply_markup=ReplyKeyboardRemove())
        await update.effective_user.send_message(
            "If you want to remove more than one, type the names in different "
            "messages or in one separated with ' '. To end removing type /end")
        return DELETE
    if "show" in update.message.text.lower():
        await update.effective_user.send_message("Connecting to database...")
        data = await get_user_from_db(update.effective_user)
    else:
        await update.effective_user.send_message(
            f"I don`t know what does {update.message.text} means, please choose on of the options on reply keyboard")
    return ANY


async def add_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO connection to db
    return ADD


async def get_user_from_db(user: Update.effective_user):
    # TODO connection to db
    return 0


async def remove_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO connection to db
    return DELETE


async def end_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Add new stock"], ["Remove one of my stock"], ["Show my stock"], ["Stop conversation"]]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.effective_user.send_message(text="ok that`s it, anything else?", reply_markup=markup_key)
    return ANY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Bye, if you want to restart conversation write /start",
                                   reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == "__main__":
    app = Application.builder().token(token).build()
    conv_handler = ConversationHandler(entry_points=[CommandHandler("start", start_command)],
                                       states={
                                           ANY: [MessageHandler(filters.TEXT & (~ filters.COMMAND) & (
                                               ~ filters.Regex('Stop conversation')), any_state)],
                                           ADD: [MessageHandler(filters.TEXT & (~ filters.COMMAND), add_paper),
                                                 CommandHandler("end", end_process)],
                                           DELETE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), add_paper),
                                                    CommandHandler("end", end_process)]
                                       },
                                       fallbacks=[CommandHandler('cancel', cancel), CommandHandler('stop', cancel),
                                                  MessageHandler(filters.Regex('Stop conversation'), cancel)])
    app.add_handler(conv_handler)

    app.run_polling(poll_interval=1)
