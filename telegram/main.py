import logging
import os
import base64
import random
import requests
import string
import sys
import urllib
from PIL import Image

from datetime import datetime
from dotenv import load_dotenv
from io import BytesIO
from pytz import timezone
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater


load_dotenv()


TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID")
API_URL = os.environ.get("API_URL")
API_PATH_TEXT = os.environ.get("API_PATH_TEXT")
API_PATH_AUDIO = os.environ.get("API_PATH_AUDIO")
API_PATH_IMAGES = os.environ.get("API_PATH_IMAGES")
API_PATH_UTILS = os.environ.get("API_PATH_UTILS")
BOT_NAME = os.environ.get("BOT_NAME")

logging.info("Starting Telegram Client...")

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

#def start(update: Update, context: CallbackContext):
#    strid = str(update.effective_chat.id)
#    if(CHAT_ID == strid):
#        context.bot.send_message(chat_id=update.effective_chat.id, text="Eccomi qua!")

#start_handler = CommandHandler('start', start)
#dispatcher.add_handler(start_handler)

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def ask(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
#        else:
#            strid = chatid
        if strid:
            message = update.message.text[5:].strip();
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_TEXT + "ask/" + urllib.parse.quote(str(update.message.chat.id)) + "/1/" + urllib.parse.quote(message) + "/" + urllib.parse.quote(strid)

                response = requests.get(url)
                if (response.status_code == 200):
                    context.bot.send_message(chat_id=update.effective_chat.id, text=response.text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="se vuoi dirmi o chiedermi qualcosa devi scrivere una frase dopo /ask (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
dispatcher.add_handler(CommandHandler('ask', ask))



def curse(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
#        else:
#            strid = chatid
        if strid:
            message = update.message.text[5:].strip();
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_TEXT + "curse/" + urllib.parse.quote(strid)

                response = requests.get(url)
                if (response.status_code == 200):
                    context.bot.send_message(chat_id=update.effective_chat.id, text=response.text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="se vuoi dirmi o chiedermi qualcosa devi scrivere una frase dopo /ask (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
dispatcher.add_handler(CommandHandler('curse', curse))


def generate(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            url = API_URL + API_PATH_UTILS + "/sentences/generate/" + urllib.parse.quote(strid) + "/1"
            response = requests.get(url)
            if (response.status_code == 200):
                context.bot.send_message(chat_id=update.effective_chat.id, text=response.text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)       
                          
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

dispatcher.add_handler(CommandHandler('generate', generate))

def story(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            url = API_URL + API_PATH_UTILS + "/paragraph/generate/" + urllib.parse.quote(strid)
            response = requests.get(url)
            if (response.status_code == 200):
                context.bot.send_message(chat_id=update.effective_chat.id, text=response.text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)       
                          
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
dispatcher.add_handler(CommandHandler('story', story))

def echo(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
       # else:
       #     strid = chatid
        if strid:
            message = update.message.text
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_TEXT + "ask/user/" + urllib.parse.quote(str(update.message.chat.id)) + "/" + urllib.parse.quote(message) + "/" + urllib.parse.quote(strid)

                response = requests.get(url)
                if (response.status_code == 200):
                    context.bot.send_message(chat_id=update.effective_chat.id, text=response.text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="se vuoi dirmi o chiedermi qualcosa devi scrivere una frase dopo /ask (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)


dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

def askaudio(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            message = update.message.text[10:].strip();
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_AUDIO + "ask/" + urllib.parse.quote(str(update.message.chat.id)) + "/1/" + urllib.parse.quote(message) + "/" + urllib.parse.quote(strid)

                response = requests.get(url)
                if (response.status_code == 200):
                    audio = BytesIO(response.content)
                    context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False, title="Messaggio vocale", performer="ScemoPezzente", filename=get_random_string(12)+ "audio.wav")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="se vuoi dirmi o chiedermi qualcosa devi scrivere una frase dopo /askaudio (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
dispatcher.add_handler(CommandHandler('askaudio', askaudio))



def speak(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            userinput = update.message.text[7:].strip();
            splitted = userinput.split("-")
            message = splitted[0].strip()
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):

                url = API_URL + API_PATH_UTILS + "/fakeyou/listvoices/it/0"

                voices = None
                voice = "google"

                response = requests.get(url)
                if (response.status_code == 200):
                    voices = response.json()
                
                if len(splitted) == 2 and voices is not None:
                    sel_voice = splitted[1].lower().strip()
                    #if sel_voice in voices:
                    #    voice = voices[sel_voice]
                    #else:
                    for voice_rest in voices:   
                        if sel_voice.lower() in voice_rest.lower():
                            voice = voices[voice_rest]
                            break

                url = API_URL + API_PATH_AUDIO + "repeat/learn/user/" + urllib.parse.quote(str(update.message.chat.id)) + "/" + urllib.parse.quote(message) + "/" + urllib.parse.quote(voice) + "/" + urllib.parse.quote(strid) 

                response = requests.get(url)
                if (response.status_code == 200):
                    audio = BytesIO(response.content)
                    context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False, title="Messaggio vocale", performer="ScemoPezzente",  filename=get_random_string(12)+ "audio.wav")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:

                text = "se vuoi che ripeto qualcosa devi scrivere una frase dopo /speak (massimo 500 caratteri).\n\n\n"
                text = text + "PS: se vuoi customizzare la voce aggiungi:\n"
                text = text + "'- modello vocale' al fondo della frase.\n\n"
                text = text + "Esempio: '/speak ciao - gerry scotti'.\n\n"
                text = text + "Usa /listvoices per una lista dei modelli disponibili."
                context.bot.send_message(chat_id=update.effective_chat.id, text=text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
dispatcher.add_handler(CommandHandler('speak', speak))



def curseaudio(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:

            url = API_URL + API_PATH_AUDIO + "curse/google/" + urllib.parse.quote(strid) 

            response = requests.get(url)
            if (response.status_code == 200):
                audio = BytesIO(response.content)
                context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False, title="Messaggio vocale", performer="ScemoPezzente",  filename=get_random_string(12)+ "audio.wav")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
dispatcher.add_handler(CommandHandler('curseaudio', curseaudio))

def listvoices(update: Update, context: CallbackContext):

    text = "lista dei modelli vocali disponibili:\n"
    text = text + "- google\n"


    
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
       # else:
       #     strid = chatid
        if strid:
            url = API_URL + API_PATH_UTILS + "/fakeyou/listvoices/it/0"

            response = requests.get(url)
            if (response.status_code == 200):
                data = response.json()
                for voice in data:   
                    text = text + "- "+voice+"\n"
                context.bot.send_message(chat_id=update.effective_chat.id, text=text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
                         
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
           
dispatcher.add_handler(CommandHandler('listvoices', listvoices))

def image(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            message = update.message.text[7:].strip();
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):

                img_url = API_URL + API_PATH_IMAGES + "search/" + urllib.parse.quote(message)

                response = requests.get(img_url, stream=True)
                if (response.status_code == 200):
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=response.content, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False, filename=get_random_string(12)+ "image.jpeg")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
                                      
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="se vuoi che cerco un immagine devi scrivere qualcosa dopo /image (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="nessun risultato trovato", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

          
dispatcher.add_handler(CommandHandler('image', image))




def search(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            message = update.message.text[8:].strip();
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_TEXT + "search/" + urllib.parse.quote(message)

                response = requests.get(url)
                if (response.status_code == 200):
                    context.bot.send_message(chat_id=update.effective_chat.id, text=response.text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="se vuoi che cerco qualcosa devi scrivere qualcosa dopo /search (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                    
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

dispatcher.add_handler(CommandHandler('search', search))

def searchaudio(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            message = update.message.text[13:].strip();
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_AUDIO + "search/" + urllib.parse.quote(message)

                response = requests.get(url)
                if (response.status_code == 200):
                    audio = BytesIO(response.content)
                    context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False, title="Ricerca: " + message, performer="ScemoPezzente", filename=get_random_string(12)+ "audio.wav")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="se vuoi che cerco qualcosa devi scrivere qualcosa dopo /search (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                    
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

dispatcher.add_handler(CommandHandler('searchaudio', searchaudio))



def insult(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            message = update.message.text[8:].strip();
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_TEXT + "insult?text=" + urllib.parse.quote(message) + "&chatid=" + urllib.parse.quote(strid)
            else:
                url = API_URL + API_PATH_TEXT + "insult?chatid=" + urllib.parse.quote(strid)

            response = requests.get(url)
            if (response.status_code == 200):
                text = response.text.replace('"','')
                context.bot.send_message(chat_id=update.effective_chat.id, text=text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

dispatcher.add_handler(CommandHandler('insult', insult))


def text2image(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            try:
                r = requests.get(os.environ.get("STABLE_DIFFUSION_API_URL"))
                r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                context.bot.send_message(chat_id=update.effective_chat.id, text="Le API remote sono offline", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            else:
                text = update.message.text[12:].strip();
                if(text != "" and len(text) <= 500  and not text.endswith('bot')):
                    payload = {
                        "prompt": text,
                        "steps": 50,
                        "width": 512,
                        "height": 512,
                        "batch_size": 1,
                        "sampler_index": "Euler",
                    }
                    url = os.environ.get("STABLE_DIFFUSION_API_URL") + os.environ.get("STABLE_DIFFUSION_API_TEXT_2_IMG")
                    response = requests.post(url, json=payload)
                    if (response.status_code == 200 and response.text != "Internal Server Error"):
                        r = response.json()
                        for i in r['images']:
                            image = Image.open(BytesIO(base64.b64decode(i.split(",",1)[0])))
                        with BytesIO() as image_binary:
                            image.save(image_binary, 'PNG')
                            image_binary.seek(0)
                            context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_binary, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="se vuoi che genero un immagine devi scrivere qualcosa dopo /text2image (massimo 500 caratteri)", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
               
                        
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

dispatcher.add_handler(CommandHandler('text2image', text2image))

def insultaudio(update: Update, context: CallbackContext):
    try:
        chatid = str(update.effective_chat.id)
        if((CHAT_ID == chatid or GROUP_CHAT_ID == chatid)):
            strid = "000000"
        #else:
        #    strid = chatid
        if strid:
            message = update.message.text[13:].strip();
            if(message != "" and len(message) <= 500  and not message.endswith('bot')):
                url = API_URL + API_PATH_TEXT + "insult?text=" + urllib.parse.quote(message) + "&chatid=" + urllib.parse.quote(strid)
            else:
                url = API_URL + API_PATH_TEXT + "insult?chatid=" + urllib.parse.quote(strid)

            response = requests.get(url)
            if (response.status_code == 200):
                audio = BytesIO(response.content)
                context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False, title="Messaggio vocale", performer="ScemoPezzente", filename=get_random_string(12)+ "audio.wav")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="si è verificato un errore stronzo", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
                
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

dispatcher.add_handler(CommandHandler('insultaudio', insultaudio))


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    text = " ⏰ " +  context.job.name + " ⏰"
    context.bot.send_message(job.context, text="⏰ RING RING RING ⏰")
    context.bot.send_message(job.context, text=text)

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        text = ""

        for i in range(len(context.args)):
            if i > 1:
                text = text + " " + context.args[i]

        text = text.strip()

        if text == "":
            update.message.reply_text('Usage: /setalarm <dd-mm> <HH:MM> <text>', disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            return

        tz = timezone('Europe/Rome')
        now = datetime.now(tz = tz).replace(second=0, microsecond=0)
        time = now.strftime("%Y") + "-" + context.args[0] +  " " + context.args[1] + ":00"


        alarm_time = datetime.strptime(time, "%Y-%d-%m %H:%M:%S")
        current_time = datetime.strptime(now.strftime("%Y-%d-%m %H:%M:%S"), "%Y-%d-%m %H:%M:%S")

        due = alarm_time - current_time
        
        if due.seconds <= 0 or due.days <=-1:
            update.message.reply_text('Devi impostare una data futura.', disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            return

        job_removed = remove_job_if_exists(text, context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=text)

        text = 'Allarme impostato correttamente!'
        if job_removed:
            text += ' Vecchio allarme rimosso.'
        update.message.reply_text(text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /setalarm <dd-mm> <HH:MM> <text>', disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    try:
        text = ""
        
        for i in range(len(context.args)):
            text = text + " " + context.args[i]
        text = text.strip()

        if text == "":
            update.message.reply_text('Usage: /unsetalarm <text>', disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            return

        job_removed = remove_job_if_exists(text, context)
        text = 'Allarme rimosso correttamente!' if job_removed else 'Nessun allarme attivo.'
        update.message.reply_text(text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /unsetalarm <text>', disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)



dispatcher.add_handler(CommandHandler("setalarm", set_timer))
dispatcher.add_handler(CommandHandler("unsetalarm", unset))



def set_timer_daily(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        text = ""

        for i in range(len(context.args)):
            if i > 0:
                text = text + " " + context.args[i]

        text = text.strip()

        if text == "":
            update.message.reply_text('Usage: /setalarm <HH:MM> <text>', disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
            return

        splitted =  context.args[0].split(":")

        hour = int(splitted[0])
        minute = int(splitted[1])

        tz = timezone('Europe/Rome')
        alarmtime = datetime.now(tz = tz).replace(hour=hour, minute=minute, second=0, microsecond=0)

        job_removed = remove_job_if_exists(text, context)
        context.job_queue.run_daily(alarm, time=alarmtime, context=chat_id, name=text)

        text = 'Allarme impostato correttamente!'
        if job_removed:
            text += ' Vecchio allarme rimosso.'
        update.message.reply_text(text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /setalarm <HH:MM> <text>', disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

dispatcher.add_handler(CommandHandler("setalarmdaily", set_timer_daily))

def restart(update: Update, context: CallbackContext):
    try:


        text = "Riavvio in corso... (Tutti gli allarmi verranno rimossi)"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)

        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Errore!", disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)


dispatcher.add_handler(CommandHandler('restart', restart))

def help(update: Update, context: CallbackContext):

    text = "ask - chiedi qualcosa (text)\n"
    text = text + "askaudio - chiedi qualcosa (audio)\n"
    text = text + "curse - Curse. (audio)\n"
    text = text + "curseaudio - Curse. (audio)\n"
    text = text + "generate - genera frasi casuali\n"
    text = text + "image - ricerca immagini\n"
    text = text + "insult - genera insulti (text)\n"
    text = text + "insultaudio - genera insulti (audio)\n"
    text = text + "help - visualizza i comandi\n"
    text = text + "listvoices - elenca i modelli vocali\n"
    text = text + "restart - riavvia il bot\n"
    text = text + "search - ricerca wikipedia (text)\n"
    text = text + "searchaudio - ricerca wikipedia (audio)\n"
    text = text + "setalarm - allarme singolo\n"
    text = text + "setalarmdaily - allarme giornaliero\n"
    text = text + "speak - ripete il messaggio via audio\n"
    text = text + "story - genera storie casuali\n"
    text = text + "text2image - genera immagini da un testo\n"
    text = text + "unsetalarm - rimuove un allarme\n";

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, disable_notification=True, reply_to_message_id=update.message.message_id, protect_content=False)
           
dispatcher.add_handler(CommandHandler('help', help))


updater.start_polling()
