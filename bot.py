import logging
import os
import sys
import json
import requests
import redis
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime
# telegram api
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

# my own libs


# current date and time

# Load methods
logdir_path = os.path.dirname(os.path.abspath(__file__))
logfile_path = os.path.join(logdir_path, "logs", "bot.log")

if not os.path.exists(os.path.join(logdir_path, "logs")):
    os.makedirs(os.path.join(logdir_path, "logs"))

logfile_handler = logging.handlers.WatchedFileHandler(
    logfile_path, 'a', 'utf-8')

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - func:%(funcName)s - line:%(funcName)s',
    level=logging.INFO,
    # handlers=[logfile_handler],
)
load_dotenv()

__author__ = os.getenv('ADMIN_USER')

rds = redis.Redis(host=os.getenv('REDIS_URI'), port=os.getenv(
    'REDIS_PORT'), password=os.getenv('REDIS_PASS'), db=0)
print(type(os.getenv(
    'REDIS_PORT')))
now = datetime.now()


def clima_command(update: Update, context: CallbackContext):
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


def covid19_command(update: Update, context: CallbackContext):
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


def acctions_command(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                "🤢",
                callback_data='covid19',
            ),
        ],

        [
            InlineKeyboardButton(
                "👇",
                callback_data='qa_hide',
            ),
        ],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text('... ', reply_markup=reply_markup)


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
    """

    update.message.reply_text(text)


def get_clima_from_redis(key: str) -> dict:
    try:
        municipio, fecha = key.split("_")
        value = rds.get(name=key)

        if value is None:
            # no existe value make request
            r = requests.get(
                f"https://cuba-weather-serverless.vercel.app/api/get-weather?name={municipio}",
            )
            value = r.json()
            value = {
                "fecha": fecha,
                **r.json()
            }

            rds.set(name=key, value=f"{json.dumps(value)}", ex=3000)
            return value
        else:
            value = json.loads(value.decode("utf-8"))
            return value
    except Exception as e:
        logger.error(e)


def get_covid19_from_redis(key: str) -> dict:
    try:
        prov, fecha = key.split("_")
        value = rds.get(name=key)
        if value is None:
            # no existe value make request
            r = requests.get(
                "https://covid19cuba.github.io/covid19cubadata.github.io/api/v2/full.json",
            )
            provincia = r.json().get('provinces')[prov].get('all')
            fecha_updated = provincia.get('updated')
            affected = provincia.get(
                'deceases_affected_municipalities')
            value = {
                "fecha": fecha_updated,
                "afectados": affected
            }
            rds.set(name=key, value=f"{json.dumps(value)}", ex=3000)
            return value
        else:
            value = json.loads(value.decode("utf-8"))

            return value
    except Exception as e:
        logger.error(e)


def get_acction_buttom(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    try:
        data = json.loads(query.data)
    except json.JSONDecodeError:
        data = query.data

    date_time = now.strftime("%m-%d-%YT%H")
    # date_time = now.strftime("%m-%d-%YT%H:%M")

    try:
        if 'wh' in data.split("_"):
            municipio = data.split("_")[1]

            value = get_clima_from_redis(key=f"{municipio}_{date_time}")

            query.edit_message_text(text=f"""
                El clima en {municipio} es:
                tempC: {value.get('tempC')}
                tempF: {value.get('tempF')}
                Humedad: {value.get('humidity')}
                Presion: {value.get('pressure')}
                Time: {value.get('timestamp')}
                Viento: {value.get('windDirectionDescription')}
                Descripcion: {value.get('descriptionWeather')}
                icon: {value.get('iconWeather')}
                                    """)

        elif 'cv' in data.split("_"):

            prov = data.split("_")[1]

            value = get_covid19_from_redis(key=f"{prov}_{date_time}")

            text_affected = ""

            for af in value.get('afectados'):
                text_affected += f"🏘️: {af.get('name')} con 🤢: {af.get('value')}\n\n"

            message = f"📅: {value.get('fecha')}\n\n {text_affected}"
            context.bot.sendMessage(
                chat_id=update.effective_chat.id, text=message)

    except Exception as e:
        logging.error(e)


def filter_text_input(update, context):

    usr_msg_text = update.message.text
    usr_chat_id = update.effective_chat.id

    if "👇" in usr_msg_text:
        context.bot.sendMessage(
            chat_id=update.effective_chat.id, text=f"/hide")


def main():
    updater = Updater(
        token=os.getenv('TELEGRAM_TOKEN'),
        use_context=True,
        request_kwargs={'read_timeout': 60, 'connect_timeout': 70},
    )

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('clima', clima_command))
    dp.add_handler(CommandHandler('covid19', covid19_command))
    # dp.add_handler(CommandHandler('quick_actions', acctions_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('hide', hide_command))
    dp.add_handler(CallbackQueryHandler(get_acction_buttom))

    # Restart bot

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler(
        'r', restart, filters=Filters.user(username=os.getenv('ADMIN_USER'))))
    # ...or here, depending on your preference :)

    # bot's text handlers
    text_update_handler = MessageHandler(Filters.text, filter_text_input)
    dp.add_handler(text_update_handler)

    # here put the jobs for the bot
    # job_queue = updater.job_queue

    # check api list - each 60sec, start on 5sec after the bot starts
    # job_queue.run_repeating()
    # Start BOT
    updater.start_polling()
    logger.info('Listening humans as %s..' % updater.bot.username)
    updater.idle()
    logger.info('Bot stopped gracefully')


if __name__ == "__main__":
    main()
