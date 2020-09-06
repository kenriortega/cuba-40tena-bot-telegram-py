import logging
from settings import SettingFile
from dotenv import load_dotenv
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import requests
import json
# Load methods
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
# logger = logging.getLogger(__name__)
load_dotenv()


def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton(
                "Playa",
                callback_data='playa',
            ),
            InlineKeyboardButton(
                "Centro Habana",
                callback_data='centro habana',
            ),
            InlineKeyboardButton(
                "Habana del Este",
                callback_data='habana del este',
            ),
        ],

        [
            InlineKeyboardButton(
                "Diez de Octubre",
                callback_data='diez de octubre',
            ),
            InlineKeyboardButton(
                "Cerro",
                callback_data='cerro',
            ),
            InlineKeyboardButton(
                "Plaza de la revolucion",
                callback_data='plaza de la revolucion',
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def help_command(update, context):
    name = update.message.from_user.username

    update.message.reply_text(f"Hi {name} Use /start to test this bot.")


def button(update, context):
    query = update.callback_query

    query.answer()
    r = requests.get(
        f"https://cuba-weather-serverless.vercel.app/api/get-weather?name={query.data}",
    )
    query.edit_message_text(text=f"""
                    El tiempo en {query.data} es:
        tempC: {r.json().get('tempC')}
        tempF: {r.json().get('tempF')}
        Humedad: {r.json().get('humidity')}
        Presion: {r.json().get('pressure')}
        Time: {r.json().get('timestamp')}
        Viento: {r.json().get('windDirectionDescription')}
        Descripcion: {r.json().get('descriptionWeather')}
        icon: {r.json().get('iconWeather')}
                            """)


def main():
    # config = SettingFile(
    #     file_path="/home/pi/proyects/bot_pi_wheather/secrets.yaml")
    updater = Updater(token=os.getenv('TELEGRAM_TOKEN'), use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # Start BOT
    updater.start_polling()
    print("Estoy up")
    # EN espera de mensajes
    updater.idle()


if __name__ == "__main__":
    main()
