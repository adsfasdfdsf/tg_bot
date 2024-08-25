import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from connector import Connector
from keyboards import CHOICE_KEYBOARD, MENU_KEYBOARD
from states import State
from texts import texts
from passwords import TOKEN


con = Connector()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup_key = ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=texts["greeting"],
                                   reply_markup=markup_key)
    return State.ANY


async def any_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "add" in update.message.text.lower():
        await update.effective_user.send_message(
            texts["bond_or_share"],
            reply_markup=ReplyKeyboardMarkup(CHOICE_KEYBOARD, one_time_keyboard=False))
        return State.SECRITY_CHOICE
    if "remove" in update.message.text.lower():
        await update.effective_user.send_message(
            texts["remove_method_description1"],
            reply_markup=ReplyKeyboardRemove())
        await update.effective_user.send_message(texts["remove_method_description2"])
        return State.DELETE
    if "show" in update.message.text.lower():
        await update.effective_user.send_message("Connecting to database...")
        data = await show_user_securities(update)
    else:
        await update.effective_user.send_message(
            texts["missed_option"].format(update.message.text))
    return State.ANY


async def add_bond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await con.find_bond(update.message.text.strip())
    if len(data) == 0:
        await update.effective_user.send_message(texts["add_method_not_found"],
                                                 reply_markup=ReplyKeyboardMarkup(CHOICE_KEYBOARD))
        return State.SECRITY_CHOICE
    elif len(data) == 1:
        await update.effective_user.send_message("We've found security. \n" +
                                                 texts["security_description"].format(data[0]['secid'],
                                                                                      data[0]['isin'],
                                                                                      data[0]['shortname'],
                                                                                      data[0]['name'],
                                                                                      data[0]['type'],
                                                                                      parse_mode="HTML"))
        await con.add_security(update.effective_user.id, data[0]["secid"])
        await con.add_security_to_db(data[0]['secid'], data[0]['isin'], data[0]['shortname'], data[0]['name'],
                                     data[0]['type'])
        await update.effective_user.send_message(texts["continue_operation"])
        return State.SECRITY_CHOICE
    else:
        await update.effective_user.send_message(texts["several_securities_found"])
        count = len(data)

        context.chat_data["choice_message_ids"] = []
        choices = {}
        for i in range(1, count + 1):
            response = texts["security_option"].format(i,
                                                       data[i - 1]['secid'],
                                                       data[i - 1]['isin'],
                                                       data[i - 1]['shortname'],
                                                       data[i - 1]['name'],
                                                       data[i - 1]['type'])

            choices[str(i)] = f"{data[i - 1]['secid']}%){data[i - 1]['isin']}%)" \
                              f"{data[i - 1]['shortname']}%){data[i - 1]['name']}%){data[i - 1]['type']}"
            msg = await update.message.reply_text(response, parse_mode="HTML")
            context.chat_data["choice_message_ids"] += [msg.message_id]
        context.chat_data[f"choice_messages"] = choices
        return State.CHOICE


async def add_share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await con.find_share(update.message.text.strip())
    if len(data) == 0:
        await update.effective_user.send_message(texts["add_method_not_found"],
                                                 reply_markup=ReplyKeyboardMarkup(CHOICE_KEYBOARD))
        return State.SECRITY_CHOICE
    elif len(data) == 1:
        await update.effective_user.send_message("We've found security. \n" +
                                                 texts["security_description"].format(data[0]['secid'],
                                                                                      data[0]['isin'],
                                                                                      data[0]['shortname'],
                                                                                      data[0]['name'],
                                                                                      data[0]['type'],
                                                                                      parse_mode="HTML"))
        await con.add_security(update.effective_user.id, data[0]["secid"])
        await con.add_security_to_db(data[0]['secid'], data[0]['isin'], data[0]['shortname'], data[0]['name'],
                                     data[0]['type'])
        await update.effective_user.send_message(texts["continue_operation"])
        return State.SECRITY_CHOICE
    else:
        await update.effective_user.send_message(texts["several_securities_found"])
        count = len(data)

        context.chat_data["choice_message_ids"] = []
        choices = {}
        for i in range(1, count + 1):
            response = texts["security_option"].format(i,
                                                       data[i - 1]['secid'],
                                                       data[i - 1]['isin'],
                                                       data[i - 1]['shortname'],
                                                       data[i - 1]['name'],
                                                       data[i - 1]['type'])
            choices[str(i)] = f"{data[i - 1]['secid']}%){data[i - 1]['isin']}%)" \
                              f"{data[i - 1]['shortname']}%){data[i - 1]['name']}%){data[i - 1]['type']}"
            msg = await update.message.reply_text(response, parse_mode="HTML")
            context.chat_data["choice_message_ids"] += [msg.message_id]
        context.chat_data[f"choice_messages"] = choices
        return State.CHOICE


async def choose_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    choice = context.chat_data["choice_messages"]
    if text.isdigit():
        if (int(text) <= len(choice)) and (int(text) > 0):
            data = choice[text].split("%)")
            await con.add_security_to_db(*data)
            await con.add_security(update.effective_user.id, data[0])
            msg = texts["security_description"].format(data[0],
                                                       data[1],
                                                       data[2],
                                                       data[3],
                                                       data[4]) + "was chosen ✅"
            await context.bot.editMessageText(chat_id=update.message.chat_id,
                                              message_id=context.chat_data['choice_message_ids'][0] - 1,
                                              text=msg, parse_mode="HTML")
            for i in context.chat_data['choice_message_ids']:
                await context.bot.deleteMessage(message_id=i,
                                                chat_id=update.message.chat_id)
            context.chat_data['choice_message_ids'] = []
            context.chat_data['choice_messages'] = {}
            await update.effective_user.send_message(texts["continue_operation"])
            return State.SECRITY_CHOICE
        else:
            await update.effective_user.send_message(texts["didnt_fit_any_option"])
            return State.CHOICE
    else:
        for i in context.chat_data["choice_message"].values():
            if text in i.upper().split("%)"):
                data = choice.split("%)")
                await con.add_security_to_db(*data)
                await con.add_security(update.effective_user.id, data[0])
                msg = texts["security_description"].format(data[0],
                                                           data[1],
                                                           data[2],
                                                           data[3],
                                                           data[4]) + "was chosen ✅"
                await context.bot.editMessageText(chat_id=update.message.chat_id, message_id=choice[0] - 1,
                                                  text=msg)
                for i in context.chat_data['choice_message_ids']:
                    await context.bot.deleteMessage(message_id=i,
                                                    chat_id=update.message.chat_id)
                context.chat_data['choice_message_ids'] = []
                context.chat_data['choice_messages'] = {}
                await update.effective_user.send_message(texts["continue_operation"])
                return State.SECRITY_CHOICE
        else:
            await update.effective_user.send_message(texts["didnt_fit_any_option"])
            return State.CHOICE


async def security_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "share" in update.message.text.lower():
        await update.effective_user.send_message(
            texts["add_share_description"],
            reply_markup=ReplyKeyboardRemove())
        await update.effective_user.send_message(
            texts["add_multiple"])
        return State.ADD_SHARE
    elif "bond" in update.message.text.lower():
        await update.effective_user.send_message(
            texts["add_bond_description"],
            reply_markup=ReplyKeyboardRemove())
        await update.effective_user.send_message(
            texts["add_multiple"])
        return State.ADD_BOND
    else:
        return State.SECRITY_CHOICE


async def end_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.deleteMessage(message_id=context.chat_data['choice_message_ids'][0] - 1,
                                    chat_id=update.message.chat_id)
    for i in context.chat_data['choice_message_ids']:
        await context.bot.deleteMessage(message_id=i,
                                        chat_id=update.message.chat_id)
    context.chat_data['choice_message_ids'] = []
    context.chat_data['choice_messages'] = {}
    markup_key = ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=False)
    await update.effective_user.send_message(text="Ok that`s it, anything else?", reply_markup=markup_key)
    return State.ANY


async def show_user_securities(update: Update):
    data = await con.get_user_securities(update.effective_user.id)
    for i in data:
        answer = await con.draw_price_graphic(i)
        if not answer:
            await update.effective_user.send_photo(f"{i}.png")
            os.remove(f"{i}.png")
        else:
            await update.effective_user.send_message(i)
        answer = await con.draw_payment_graph(i)
        if not answer:
            await update.effective_user.send_photo(f"{i}payment.png")
            os.remove(f"{i}payment.png")
        else:
            await update.effective_user.send_message(answer)


async def remove_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await con.remove_security(update.effective_user.id, update.message.text)
    return State.DELETE


async def end_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup_key = ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=False)
    await update.effective_user.send_message(text="Ok that`s it, anything else?", reply_markup=markup_key)
    return State.ANY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=texts["bye"],
                                   reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    conv_handler = ConversationHandler(entry_points=[CommandHandler("start", start_command)],
                                       states={
                                           State.ANY: [MessageHandler(filters.TEXT & (~ filters.COMMAND) & (
                                               ~ filters.Regex('Stop conversation')), any_state)],
                                           State.ADD_SHARE: [
                                               MessageHandler(filters.TEXT & (~ filters.COMMAND), add_share),
                                               CommandHandler("end", end_process)],
                                           State.ADD_BOND: [
                                               MessageHandler(filters.TEXT & (~ filters.COMMAND), add_bond),
                                               CommandHandler("end", end_process)],
                                           State.CHOICE: [
                                               MessageHandler(filters.TEXT & (~ filters.COMMAND), choose_paper),
                                               CommandHandler("end", end_choosing)],
                                           State.DELETE: [
                                               MessageHandler(filters.TEXT & (~ filters.COMMAND), remove_paper),
                                               CommandHandler("end", end_process)],
                                           State.SECRITY_CHOICE: [
                                               MessageHandler(filters.TEXT & (~ filters.COMMAND), security_choice),
                                               CommandHandler("end", end_process)]

                                       },
                                       fallbacks=[CommandHandler('cancel', cancel), CommandHandler('stop', cancel),
                                                  MessageHandler(filters.Regex('Stop conversation'), cancel)])
    app.add_handler(conv_handler)

    app.run_polling(poll_interval=.5)


if __name__ == "__main__":
    main()
