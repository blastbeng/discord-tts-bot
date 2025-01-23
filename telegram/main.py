import logging
import os
import base64
import random
import requests
import string
import sys
import urllib
import time

from datetime import datetime
from dotenv import load_dotenv
from io import BytesIO
from pytz import timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()


TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID")
API_URL = os.environ.get("API_URL")
API_PATH_TEXT = os.environ.get("API_PATH_TEXT")
API_PATH_AUDIO = os.environ.get("API_PATH_AUDIO")
API_PATH_UTILS = os.environ.get("API_PATH_UTILS")
API_VOICECLONE_URL = os.environ.get("API_VOICECLONE_URL")
API_VOICECLONE_PATH = os.environ.get("API_VOICECLONE_PATH")
BOT_NAME = os.environ.get("BOT_NAME")

logging.info("Starting Telegram Client...")

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

application = ApplicationBuilder().token(TOKEN).build()

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)
        if(CHAT_ID == chatid):
            strid = "000000"
            message = update.message.text.strip()
            if(message != ""    ):
                url = API_URL + API_PATH_TEXT + "ask/" + urllib.parse.quote(message) + "/000000/it"

                response = requests.get(url)
                if (response.status_code == 200):
                    await update.message.reply_text(response.text, disable_notification=True, protect_content=False)
                else:
                    await update.message.reply_text("si è verificato un errore stronzo", disable_notification=True, protect_content=False)
                
            else:
                await update.message.reply_text("se vuoi dirmi o chiedermi qualcosa devi scrivere una frase dopo /ask (massimo 500 caratteri)", disable_notification=True, protect_content=False)

    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      await update.message.reply_text("Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)
        if(CHAT_ID == chatid or GROUP_CHAT_ID == chatid):
            strid = "000000"
            message = update.message.text[8:].strip()
            url = API_URL + API_PATH_TEXT + "/random/000000/"
            if(message != ""):
                url = url + urllib.parse.quote(message)

            response = requests.get(url)
            if (response.status_code == 200):
                await update.message.reply_text(response.text, disable_notification=True, protect_content=False)
            else:
                await update.message.reply_text("si è verificato un errore stronzo", disable_notification=True, protect_content=False)

    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      await update.message.reply_text("Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

application.add_handler(CommandHandler('random', random))

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
            message = update.message.text[5:].strip()
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_TEXT + "ask/" + urllib.parse.quote(message) + "/000000/it"

                response = requests.get(url)
                if (response.status_code == 200):
                    await update.message.reply_text(response.text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                else:
                    await update.message.reply_text("si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:
                await update.message.reply_text("se vuoi dirmi o chiedermi qualcosa devi scrivere una frase dopo /ask (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      await update.message.reply_text("Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
application.add_handler(CommandHandler('ask', ask))


async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
            userinput = update.message.text[7:].strip()
            splitted = userinput.split("-")
            message = splitted[0].strip()
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):

                url = API_URL + API_PATH_UTILS + "/fakeyou/listvoices/it"

                voices = None
                voice = "google"
                voice_name = "google"

                response = requests.get(url)
                if (response.status_code == 200):
                    voices = response.json()
                
                if len(splitted) == 2 and voices is not None:
                    sel_voice = splitted[1].lower().strip()
                    for voice_rest in voices:   
                        if sel_voice.lower() in voice_rest.lower():
                            voice = voices[voice_rest]
                            voice_name = voice_rest
                            break

                url = API_URL + API_PATH_AUDIO + "repeat/learn/user/" + urllib.parse.quote(str(update.message.chat.id)) + "/" + urllib.parse.quote(message) + "/" + urllib.parse.quote(voice) + "/" + urllib.parse.quote(strid) + "/"

                response = requests.get(url)
                if (response.status_code == 200):
                    audio = BytesIO(response.content)
                    title = "Messaggio vocale"
                    if "X-Generated-Text" in response.headers:
                        title = response.headers["X-Generated-Text"]
                    await update.message.reply_audio(audio, disable_notification=True, title=title, performer=voice_name,  filename=get_random_string(12)+ "audio.mp3", reply_to_message_id=update.message.message_id, protect_content=False)
                else:
                    await update.message.reply_text("si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:

                text = "se vuoi che ripeto qualcosa devi scrivere una frase dopo /speak (massimo 500 caratteri).\n\n\n"
                text = text + "PS: se vuoi customizzare la voce aggiungi:\n"
                text = text + "'- modello vocale' al fondo della frase.\n\n"
                text = text + "Esempio: '/speak ciao - gerry scotti'.\n\n"
                text = text + "Usa /listvoices per una lista dei modelli disponibili."
                await update.message.reply_text(text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      await update.message.reply_text("Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
application.add_handler(CommandHandler('speak', speak))



async def listvoices(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = "lista dei modelli vocali disponibili:\n"
    
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"    
            url = API_URL + API_PATH_UTILS + "/fakeyou/listvoices/it"

            response = requests.get(url)
            if (response.status_code == 200):
                data = response.json()
                for voice in data:   
                    text = text + "- "+voice+"\n"
                await update.message.reply_text(text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            else:
                await update.message.reply_text("si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
                         
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await update.message.reply_text("Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

           
application.add_handler(CommandHandler('listvoices', listvoices))

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:

        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"    
            await update.message.reply_text("Riavvio in corso...", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await update.message.reply_text("Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)


application.add_handler(CommandHandler('restart', restart))

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = "ask - chiedi qualcosa al bot\n"
    text = text + "disable - disabilita modalitá automatica\n"
    text = text + "enable - abilita modalitá automatica\n"
    text = text + "help - visualizza i comandi\n"
    text = text + "listvoices - elenca i modelli vocali\n"
    text = text + "restart - riavvia il bot\n"
    text = text + "speak - ripete il messaggio via audio\n"
    text = text + "stop - interrompe la modalitá automatica\n"

    await update.message.reply_text(text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
           
application.add_handler(CommandHandler('help', help))

async def callback_auto_message(context):
    try:
        url = API_URL + API_PATH_TEXT + "/random/000000/"
        response = requests.get(url)
        if (response.status_code == 200):
            await context.bot.send_message(chat_id=context.job.chat_id, text=response.text, disable_notification=True, protect_content=False)

    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        chatid = str(update.effective_chat.id)
        if(CHAT_ID == chatid):
            strid = "000000"
            message = update.message.text.strip()
            if(message != ""    ):
                url = API_URL + API_PATH_TEXT + "ask/" + urllib.parse.quote(message) + "/000000/it"

                response = requests.get(url)
                if (response.status_code == 200):
                    await update.message.reply_text(response.text, disable_notification=True, protect_content=False)
                else:
                    await update.message.reply_text("si è verificato un errore stronzo", disable_notification=True, protect_content=False)
                
            else:
                await update.message.reply_text("se vuoi dirmi o chiedermi qualcosa devi scrivere una frase dopo /ask (massimo 500 caratteri)", disable_notification=True, protect_content=False)


    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)   
        if(GROUP_CHAT_ID == chatid):
            job = context.job_queue.get_jobs_by_name(chatid)
            if not job:
                context.job_queue.run_repeating(callback_auto_message, 600, chat_id=chatid, name=str(chatid))

        await update.message.reply_text("abilito la modalitá automatica", disable_notification=True, protect_content=False)

    except Exception as e:
      await update.message.reply_text("si è verificato un errore stronzo", disable_notification=True, protect_content=False)
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

application.add_handler(CommandHandler("enable", enable))


async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)   
        if(GROUP_CHAT_ID == chatid):
            job_removed = remove_job_if_exists(str(chatid), context)

            await update.message.reply_text("disabilito la modalitá automatica", disable_notification=True, protect_content=False)
    except Exception as e:
      await update.message.reply_text("si è verificato un errore stronzo", disable_notification=True, protect_content=False)
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

application.add_handler(CommandHandler("disable", disable))



application.run_polling(allowed_updates=Update.ALL_TYPES)