import os
import requests
import telegram
from typing import List

from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove

from core.configs import SettingFile
config = SettingFile(
    file_path="/home/pi/proyects/bot_pi_wheather/settings.yaml")
config_admin = SettingFile(
    file_path="/home/pi/proyects/bot_pi_wheather/admin.yml")
config_telegram = config.load_external_services_file()
config_admin_user = config_admin.load_external_services_file()

INTERVAL_BY_HOURS = 7200  # 2h


def clima_command(update: Update, context: CallbackContext):
    # keyboard_este = []

    keyboard_este = list(
        map(lambda ink: InlineKeyboardButton(
            text=ink.get('text'),
            callback_data=ink.get(
                'callback'),
        ), config_telegram.get('telegram').get('mun_este'),
        )
    )
    keyboard_oeste = list(
        map(lambda ink: InlineKeyboardButton(
            text=ink.get('text'),
            callback_data=ink.get(
                'callback'),
        ), config_telegram.get('telegram').get('mun_oeste'),
        )
    )

    keyboard = [
        keyboard_este,
        keyboard_oeste
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def covid19_command(update: Update, context: CallbackContext):
    keyboard_provs = list(
        map(lambda ink: InlineKeyboardButton(
            text=ink.get('text'),
            callback_data=ink.get(
                'callback'),
        ), config_telegram.get('telegram').get('provs'),
        )
    )
    keyboard = [
        keyboard_provs
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def dev_command(update: Update, context: CallbackContext):
    keyboard_devto_left = list(
        map(lambda ink: InlineKeyboardButton(
            text=ink.get('text'),
            callback_data="dev_to",
        ), config_telegram.get('telegram').get('dev_to_left'),
        )
    )
    keyboard_devto_rigth = list(
        map(lambda ink: InlineKeyboardButton(
            text=ink.get('text'),
            callback_data="dev_to",
        ), config_telegram.get('telegram').get('dev_to_rigth'),
        )
    )
    keyboard = [
        keyboard_devto_left,
        keyboard_devto_rigth
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text('waiting... ', reply_markup=reply_markup)


def hide_command(update: Update, context: CallbackContext):
    """Hides the keyboard in the specified chat."""
    update.message.reply_text("\U0001F44D", reply_markup=ReplyKeyboardRemove())


def help_command(update: Update, context: CallbackContext):
    name = update.message.from_user.username

    text = f"""
    CMDS:
    /help - F1
    /covid19  - datos sobre el covid19
    /clima - datos sobre el clima
    /dev_to - Top 5 articulos from https://dev.to/
    """

    update.message.reply_text(text)


def start_command(update: Update, context: CallbackContext):
    name = update.message.from_user.username

    text = f"""
    Bot con fines educativos tecle el comando /help
    para obtener ayuda
    """

    update.message.reply_text(text)


def make_request_by_url(service: dict) -> dict:
    value = {
        "name": service.get('name'),
        "status": 0
    }
    if service.get('name') == 'clima':
        r = requests.get(
            f"{service.get('url')}cerro",
        )
        value['status'] = r.status_code
        return value
    else:
        r = requests.get(
            f"{service.get('url')}",
        )
        value['status'] = r.status_code
        return value


def callback_alarm(context: CallbackContext):
    services = list(
        map(lambda s: make_request_by_url(s), config_telegram.get('services'))
    )
    text = "Listado de servicios: \n\t"

    for s in services:
        text += f"🏘️: {s.get('name')} con status: {s.get('status')}\n\n"

    for user in config_admin_user.get('users'):
        if user.get('enable') == True:
            context.bot.send_message(chat_id=user.get('chat_id'), text=text)


def start_alarm_command(update: Update, context: CallbackContext):
    for user in config_admin_user.get('users'):
        if user.get('enable') == True:
            context.job_queue.start()
            context.job_queue.run_repeating(
                callback_alarm, interval=INTERVAL_BY_HOURS, first=0)
    update.message.reply_text(
        text="sending alert to users")


def stop_alarm_command(update: Update, context: CallbackContext):
    context.job_queue.stop()
