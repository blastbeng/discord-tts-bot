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


class SpeakClonedException(Exception):
    pass

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)
        if(CHAT_ID == chatid):
            strid = "000000"
        if strid:
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

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        if strid:
            message = update.message.text[5:].strip();
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
        if strid:
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


async def speakcloned(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        if strid:
            userinput = update.message.text[13:].strip()
            splitted = userinput.split("-")
            message = splitted[0].strip()
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):

                url = API_VOICECLONE_URL + API_VOICECLONE_PATH + "/listvoices"

                voices = None
                voice = None
                voice_name = None

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
                        
                if voice is not None and voice_name is not None:             
                    url = API_VOICECLONE_URL + API_VOICECLONE_PATH + "talk/" + urllib.parse.quote(voice_name) + "/" + urllib.parse.quote(message) + "/"

                    count = 0
                    generated = False
                    response = requests.get(url)
                    if (response.status_code == 206):
                        await update.message.reply_text("altri processi di generazione audio sono attivi, riprovare piú tardi", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                    elif (response.status_code == 200):
                        while count < 120:
                            poll_url = response.json()["poll_url"]
                            poll_response = requests.get(poll_url)
                            poll_json = poll_response.json()
                            if (poll_response.status_code == 200 and poll_json["status"] == 'Completed'):
                                audio_url = poll_json["audio_url"]
                                audio_response = requests.get(audio_url)
                                audio = BytesIO(audio_response.content)
                                title = "Messaggio vocale"
                                await update.message.reply_audio(audio, disable_notification=True, title=title, performer=voice_name,  filename=get_random_string(12)+ "audio.mp3", reply_to_message_id=update.message.message_id, protect_content=False)
                                count = 120
                                generated = True
                            else:
                                time.sleep(2)
                                count = count + 1
                        if count >= 120 and generated is False:                 
                            await update.message.reply_text("la generazione ha impiegato troppo tempo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                    else:
                        await update.message.reply_text("è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                else:
                    raise SpeakClonedException("user input error")
            else:
                raise SpeakClonedException("user input error")

               
    except SpeakClonedException:
        text = "se vuoi che ripeto qualcosa devi scrivere una frase dopo /speakcloned (massimo 500 caratteri).\n\n\n"
        text = text + "PS: Il modello vocale é obbligatorio, aggiungi:\n"
        text = text + "'- modello vocale' al fondo della frase.\n\n"
        text = text + "Esempio: '/speakcloned ciao - utente'.\n\n"
        text = text + "Usa /listclonedvoices per una lista dei modelli disponibili."
        await update.message.reply_text(text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await update.message.reply_text("Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
application.add_handler(CommandHandler('speakcloned', speakcloned))

async def listvoices(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = "lista dei modelli vocali disponibili:\n"
    
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"    
        if strid:
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

async def listclonedvoices(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = "lista dei modelli vocali clonati disponibili:\n"
    
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"    
        if strid:
            url = API_VOICECLONE_URL + API_VOICECLONE_PATH + "/listvoices"
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
           
application.add_handler(CommandHandler('listclonedvoices', listclonedvoices))

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:

        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"    
        if strid:
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

    text = "ask - chiedi qualcosa (text)\n"
    text = text + "help - visualizza i comandi\n"
    text = text + "listvoices - elenca i modelli vocali\n"
    text = text + "listclonedvoices - elenca i modelli vocali\n"
    text = text + "restart - riavvia il bot\n"
    text = text + "speak - ripete il messaggio via audio\n"
    text = text + "speakcloned - ripete il messaggio via audio usando i modelli vocali clonati\n"

    await update.message.reply_text(text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
           
application.add_handler(CommandHandler('help', help))


application.run_polling()
