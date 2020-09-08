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


def clima(update, context):
    keyboard = [
        [
            InlineKeyboardButton(
                "Playa",
                callback_data='wh_playa',
            ),
            InlineKeyboardButton(
                "Centro Habana",
                callback_data='wh_centro habana',
            ),
            InlineKeyboardButton(
                "Habana del Este",
                callback_data='wh_habana del este',
            ),
        ],

        [
            InlineKeyboardButton(
                "Diez de Octubre",
                callback_data='wh_diez de octubre',
            ),
            InlineKeyboardButton(
                "Cerro",
                callback_data='wh_cerro',
            ),
            InlineKeyboardButton(
                "Plaza de la revolucion",
                callback_data='wh_plaza de la revolucion',
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def covid19_prov(update, context):
    keyboard = [
        [
            InlineKeyboardButton(
                "La Habana",
                callback_data='cv_lha',
            ),
            InlineKeyboardButton(
                "Artemisa",
                callback_data='cv_art',
            ),
            InlineKeyboardButton(
                "Camaguey",
                callback_data='cv_cam',
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def help_command(update, context):
    name = update.message.from_user.username

    update.message.reply_text(f"""
    Hi {name} Use this commands:

    /covid19 to get status in your municipality.

    /clima to get wheather in your locale
                              """)


def get_acction_buttom(update, context):
    query = update.callback_query
    query.answer()

    try:
        data = json.loads(query.data)
    except json.JSONDecodeError:
        data = query.data

    try:
        if 'wh' in data.split("_"):
            municipio = data.split("_")[1]
            r = requests.get(
                f"https://cuba-weather-serverless.vercel.app/api/get-weather?name={municipio}",
            )
            query.edit_message_text(text=f"""
                El clima en {data.split("_")[1]} es:
                tempC: {r.json().get('tempC')}
                tempF: {r.json().get('tempF')}
                Humedad: {r.json().get('humidity')}
                Presion: {r.json().get('pressure')}
                Time: {r.json().get('timestamp')}
                Viento: {r.json().get('windDirectionDescription')}
                Descripcion: {r.json().get('descriptionWeather')}
                icon: {r.json().get('iconWeather')}
                                    """)
        elif 'cv' in data.split("_"):
            prov = data.split("_")[1]

            r = requests.get(
                "https://covid19cuba.github.io/covid19cubadata.github.io/api/v2/full.json",
            )
            provincia = r.json().get('provinces')[prov].get('all')
            fecha_updated = provincia.get('updated')
            affected = provincia.get(
                'deceases_affected_municipalities')
            text_affected = ""
            for af in affected:
                text_affected += f"🏘️: {af.get('name')} con 🤢: {af.get('value')}\n\n"

            message = f"📅: {fecha_updated}\n\n {text_affected}"
            context.bot.sendMessage(
                chat_id=update.effective_chat.id, text=message)

    except Exception as e:
        logging.error(e)


def main():
    # config = SettingFile(
    #     file_path="/home/pi/proyects/bot_pi_wheather/secrets.yaml")
    updater = Updater(
        token=os.getenv('TELEGRAM_TOKEN'),
        use_context=True,
        # request_kwargs={'read_timeout': 60, 'connect_timeout': 70},
    )

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('clima', clima))
    dp.add_handler(CommandHandler('covid19', covid19_prov))
    dp.add_handler(CallbackQueryHandler(get_acction_buttom))
    dp.add_handler(CommandHandler('help', help_command))

    # Start BOT
    updater.start_polling()
    print("Estoy up")
    # EN espera de mensajes
    updater.idle()


if __name__ == "__main__":
    main()
