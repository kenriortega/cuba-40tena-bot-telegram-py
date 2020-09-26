import logging
import os
from threading import Thread
import sys
from dotenv import load_dotenv
# telegram api
from telegram import BotCommand
# from telegram.update import Update
# from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

# my own libs
from core.commands import help_command, covid19_command, clima_command, hide_command, dev_command, start_command, start_alarm_command, stop_alarm_command, forecast_command
from core.handler import get_acction_buttom, filter_devto_by_tag
from core.configs import SettingFile

# Load methods
logdir_path = os.path.dirname(os.path.abspath(__file__))
logfile_path = os.path.join(logdir_path, "logs", "bot.log")

if not os.path.exists(os.path.join(logdir_path, "logs")):
    os.makedirs(os.path.join(logdir_path, "logs"))

logfile_handler = logging.handlers.WatchedFileHandler(
    logfile_path, 'a', 'utf-8')

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - func:%(funcName)s',
    level=logging.INFO,
    # handlers=[logfile_handler],
)
load_dotenv()

__author__ = os.getenv('ADMIN_USER')


def main():
    config = SettingFile(
        file_path="/home/pi/proyects/bot_pi_wheather/settings.yaml")
    config_telegram = config.load_external_services_file()
    updater = Updater(
        token=os.getenv('TELEGRAM_TOKEN'),
        use_context=True,
        request_kwargs={'read_timeout': 60, 'connect_timeout': 70},
    )
    bot_commands = list(
        map(lambda ink: BotCommand(
            command=ink.get('text'),
            description=ink.get('description'),
        ), config_telegram.get('telegram').get('commands'),
        )
    )
    updater.bot.set_my_commands(bot_commands)
    dp = updater.dispatcher
    # jq = updater.job_queue

    dp.add_handler(CommandHandler('clima', clima_command))
    dp.add_handler(CommandHandler('forecast', forecast_command))
    dp.add_handler(CommandHandler('covid19', covid19_command))
    dp.add_handler(CommandHandler('dev_to', dev_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('hide', hide_command))
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(
        CommandHandler(
            'start_alert',
            start_alarm_command,
            filters=Filters.user(
                username=os.getenv('ADMIN_USER'),
            ),
        ),
    )
    dp.add_handler(
        CommandHandler(
            'stop_alert',
            stop_alarm_command,
            filters=Filters.user(
                username=os.getenv('ADMIN_USER'),
            ),
        ),
    )
    dp.add_handler(CallbackQueryHandler(get_acction_buttom))

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        logger.info('Bot stopped gracefully')
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler(
        'r', restart, filters=Filters.user(username=os.getenv('ADMIN_USER'))))
    # ...or here, depending on your preference :)

    # bot's text handlers
    text_update_handler = MessageHandler(Filters.text, filter_devto_by_tag)
    dp.add_handler(text_update_handler)

    # Start BOT
    updater.start_polling()
    logger.info('Listening humans as %s..' % updater.bot.username)
    updater.idle()
    logger.info('Bot stopped gracefully')


if __name__ == "__main__":
    main()
