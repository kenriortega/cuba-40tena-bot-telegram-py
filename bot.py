import logging
import os
import sys
import json
import requests
from threading import Thread
from dotenv import load_dotenv
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from settings import SettingFile

__author__ = os.getenv('ADMIN_USER')
# Load methods
logdir_path = os.path.dirname(os.path.abspath(__file__))
logfile_path = os.path.join(logdir_path, "logs", "bot.log")

if not os.path.exists(os.path.join(logdir_path, "logs")):
    os.makedirs(os.path.join(logdir_path, "logs"))

logfile_handler = logging.handlers.WatchedFileHandler(
    logfile_path, 'a', 'utf-8')

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    # handlers=[logfile_handler],
)
load_dotenv()


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

    text = "/help - {}\n" \
           "/covid19  - {}\n" \
           "/clima - {}\n" \
           "/quick_actions - {}\n" \
           "/hide - {}" \
        .format("F1",
                "datos sobre el covid19",
                "datos sobre el clima",
                "quick actions [developing]",
                "ocultar quick actions",
                )

    update.message.reply_text(text)


def get_acction_buttom(update: Update, context: CallbackContext):
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


def filter_text_input(update, context):

    usr_msg_text = update.message.text
    usr_chat_id = update.effective_chat.id

    if "👇" in usr_msg_text:
        context.bot.sendMessage(
            chat_id=update.effective_chat.id, text=f"/hide")


def main():
    # config = SettingFile(
    #     file_path="/home/pi/proyects/bot_pi_wheather/secrets.yaml")
    updater = Updater(
        token=os.getenv('TELEGRAM_TOKEN'),
        use_context=True,
        # request_kwargs={'read_timeout': 60, 'connect_timeout': 70},
    )

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('clima', clima_command))
    dp.add_handler(CommandHandler('covid19', covid19_command))
    dp.add_handler(CommandHandler('quick_actions', acctions_command))
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

    # ...or here...

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
