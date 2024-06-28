import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.ext.filters import Regex, COMMAND
from passwords import TOKEN
from connector import Connector

token = TOKEN
con = Connector()

ADD, DELETE, ANY = range(3)

con_established = False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Add new stock"], ["Remove one of my stocks"], ["Show my stocks"], ["Stop conversation"]]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I'm a screener bot, I can show some statistics on "
                                        "different stocks and shares! You can choose any option and get a description",
                                   reply_markup=markup_key)
    if not con_established:
        await con.Init()
    return ANY


async def any_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "add" in update.message.text.lower():
        await update.effective_user.send_message(
            "Write a tiсker (or a name, but ticker is better) of a stock you want to add.",
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
        data = await show_user_securities(update)
    else:
        await update.effective_user.send_message(
            f"I don`t know what does {update.message.text} means, please choose on of the options on reply keyboard")
    return ANY


async def add_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await con.add_security(update.effective_user.id, update.message.text)
    return ADD
#TODO choose beetwen many


async def show_user_securities(update: Update):
    data = await con.get_user_securities(update.effective_user.id)
    for i in data:
        await update.effective_user.send_message(i)
    #TODO graphics and more info about securities


async def remove_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await con.remove_security(update.effective_user.id, update.message.text)
    return DELETE


async def end_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Add new stock"], ["Remove one of my stock"], ["Show my stock"], ["Stop conversation"]]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.effective_user.send_message(text="Ok that`s it, anything else?", reply_markup=markup_key)
    return ANY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Bye, if you want to restart conversation write /start",
                                   reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    app = Application.builder().token(token).build()
    conv_handler = ConversationHandler(entry_points=[CommandHandler("start", start_command)],
                                       states={
                                           ANY: [MessageHandler(filters.TEXT & (~ filters.COMMAND) & (
                                               ~ filters.Regex('Stop conversation')), any_state)],
                                           ADD: [MessageHandler(filters.TEXT & (~ filters.COMMAND), add_paper),
                                                 CommandHandler("end", end_process)],
                                           DELETE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), remove_paper),
                                                    CommandHandler("end", end_process)]
                                       },
                                       fallbacks=[CommandHandler('cancel', cancel), CommandHandler('stop', cancel),
                                                  MessageHandler(filters.Regex('Stop conversation'), cancel)])
    app.add_handler(conv_handler)

    app.run_polling(poll_interval=1)


if __name__ == "__main__":
    main()