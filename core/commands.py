from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove


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


def dev_command(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                "vue",
                callback_data='covid19',
            ),
            InlineKeyboardButton(
                "javascript",
                callback_data='covid19',
            ),
        ],

        [
            InlineKeyboardButton(
                "dotnet",
                callback_data='qa_hide',
            ),
            InlineKeyboardButton(
                "python",
                callback_data='qa_hide',
            ),
        ],
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
