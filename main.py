import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.ext.filters import Regex, COMMAND
from passwords import TOKEN
from connector import Connector

token = TOKEN
con = Connector()


ADD, DELETE, ANY, CHOICE = range(4)

con_established = False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.message_id)
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
    print(update.message.message_id)
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
    data = await con.find_security(update.message.text.strip())
    if len(data) == 0:
        await update.effective_user.send_message("We didn't find any securities on this name/ticker/isin")
        return ADD
    elif len(data) == 1:
        await update.effective_user.send_message(f"We've found security. \nTicker: <b>{data[0]['secid']}</b>"
                                                 f"\nISIN: <b>{data[0]['isin']}</b>"
                                                 f"\nShortname: <b>{data[0]['shortname']}</b>"
                                                 f"\nName: <b>{data[0]['name']}</b>"
                                                 f"\nType: <b>{data[0]['type']}</b>, it will be added"
                                                 f" to your securities", parse_mode="HTML")
        await con.add_security(update.effective_user.id, data[0]["secid"])
        await con.add_security_to_db(data[0]['secid'], data[0]['isin'], data[0]['shortname'], data[0]['name'], data[0]['type'])
        return ADD
    else:
        if len(data) < 11:
            await update.effective_user.send_message("We've found several securities on your request. "
                                                     "Please specify which one: by typing the number. Example: 1"
                                                     " or by typing ticker or by typing secid")
            response = ""
            choices = {}
            for i in range(1, len(data) + 1):
                response += f"{i}) Ticker: <b>{data[i - 1]['secid']}</b> " \
                            f"\nISIN: <b>{data[i - 1]['isin']}</b>" \
                            f"\nShortname: <b>{data[i - 1]['shortname']}</b>" \
                            f"\nName: <b>{data[i - 1]['name']}</b>" \
                            f"\nType: <b>{data[i - 1]['type']}</b> \n\n"
                choices[str(i)] = f"{data[i - 1]['secid']}%){data[i - 1]['isin']}%)" \
                                  f"{data[i - 1]['shortname']}%){data[i - 1]['name']}%){data[i - 1]['type']}"
            msg = await update.message.reply_text(response, parse_mode="HTML")
            context.chat_data["choice_message"] = choices
            context.chat_data["choice_message_id"] = msg.message_id
            return CHOICE
        else:
            await update.effective_user.send_message("We've found too many. Can not display in chat please "
                                                     "write an appropriate ticker")
            return ADD


async def choose_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    if text.isdigit():
        if text in context.chat_data["choice_message"]:
            await con.add_security_to_db(*context.chat_data["choice_message"][text].split("%)"))
            await con.add_security(update.effective_user.id, context.chat_data["choice_message"][text].split("%)")[0])
            await update.effective_user.send_message("Done")
            await context.bot.deleteMessage(message_id=context.chat_data['choice_message_id'],
                                            chat_id=update.message.chat_id)
            await context.bot.deleteMessage(message_id=context.chat_data['choice_message_id'] - 1,
                                            chat_id=update.message.chat_id)
            context.chat_data['choice_message_id'] = -1
            await update.effective_user.send_message("You may add any other security or /end")
            return ADD
        else:
            await update.effective_user.send_message("Choice doesn't fit any option fit any option."
                                                     " Try again or /end")
            return CHOICE
    else:
        for i in context.chat_data["choice_message"].values():
            if text in i.upper().split("%)"):
                await con.add_security_to_db(*i.split("%)"))
                await con.add_security(update.effective_user.id, i.split("%)")[0])
                await update.effective_user.send_message("Done")
                await context.bot.deleteMessage(message_id=context.chat_data['choice_message_id'],
                                           chat_id=update.message.chat_id)
                await context.bot.deleteMessage(message_id=context.chat_data['choice_message_id'] - 1,
                                                chat_id=update.message.chat_id)
                context.chat_data['choice_message_id'] = -1
                await update.effective_user.send_message("You may add any other security or /end")
                return ADD
        else:
            await update.effective_user.send_message("Choice doesn't fit any option."
                                                     " Try again or /end")
            return CHOICE


async def end_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data['choice_message_id'] != -1:
        await context.bot.deleteMessage(message_id=context.chat_data['choice_message_id'],
                                        chat_id=update.message.chat_id)
        await context.bot.deleteMessage(message_id=context.chat_data['choice_message_id'] - 1,
                                        chat_id=update.message.chat_id)
        context.chat_data['choice_message_id'] = -1
    reply_keyboard = [["Add new stock"], ["Remove one of my stock"], ["Show my stock"], ["Stop conversation"]]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.effective_user.send_message(text="Ok that`s it, anything else?", reply_markup=markup_key)
    return ANY


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
                                           CHOICE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), choose_paper),
                                                    CommandHandler("end_choosing", end_process)],
                                           DELETE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), remove_paper),
                                                    CommandHandler("end", end_process)]
                                       },
                                       fallbacks=[CommandHandler('cancel', cancel), CommandHandler('stop', cancel),
                                                  MessageHandler(filters.Regex('Stop conversation'), cancel)])
    app.add_handler(conv_handler)

    app.run_polling(poll_interval=.5)


if __name__ == "__main__":
    main()