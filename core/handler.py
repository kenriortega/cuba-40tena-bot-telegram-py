from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
import json
import requests
import redis
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

EXP_KEY_CLIMA = 30000*60
EXP_KEY_DEVTO = 10000*60
EXP_KEY_COVID = 60000*60
COUNT_PER_PAGE_DEVTO = 5

rds = redis.Redis(host=os.getenv('REDIS_URI'), port=os.getenv(
    'REDIS_PORT'), password=os.getenv('REDIS_PASS'), db=0)

now = datetime.now()


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

            rds.set(name=key, value=f"{json.dumps(value)}", ex=EXP_KEY_CLIMA)
            return value
        else:
            value = json.loads(value.decode("utf-8"))
            return value
    except Exception as e:
        logging.error(e)


def get_devto_from_redis(key: str) -> dict:
    try:
        tag, fecha = key.split("_")
        value = rds.get(name=key)

        if value is None:
            # no existe value make request
            r = requests.get(
                f"https://dev.to/api/articles?tag={tag}&per_page={COUNT_PER_PAGE_DEVTO}",
            )
            value = list(map(
                lambda article: {
                    # "title": article.get('title'),
                    # "description": article.get('description'),
                    "url": article.get('url'),
                    "published_at": article.get('published_at'),
                }, r.json(),
            ))

            value = {
                "fecha": fecha,
                "articles": value
            }

            rds.set(name=key, value=f"{json.dumps(value)}", ex=EXP_KEY_DEVTO)
            return value
        else:
            value = json.loads(value.decode("utf-8"))
            return value
    except Exception as e:
        logging.error(e)


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
            rds.set(name=key, value=f"{json.dumps(value)}", ex=EXP_KEY_COVID)
            return value
        else:
            value = json.loads(value.decode("utf-8"))

            return value
    except Exception as e:
        logging.error(e)


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


def filter_devto_by_tag(update, context):

    usr_tag_text = update.message.text
    usr_chat_id = update.effective_chat.id
    date_time = now.strftime("%m-%d-%YT%H")

    value = get_devto_from_redis(key=f"{usr_tag_text}_{date_time}")
    for a in value.get('articles'):
        context.bot.sendMessage(
            chat_id=update.effective_chat.id,
            text=f"#{usr_tag_text}: \n{a.get('url')}"
        )
