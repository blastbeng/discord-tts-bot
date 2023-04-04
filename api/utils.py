import re
import shutil
import chatterbot
import spacy
import zipfile
import random
import wikipedia
import sqlite3
import json
import insults
import requests
import sys
import os
import io
import urllib
import yt_dlp
from datetime import datetime
import string
import fakeyou
import time
import wave
import audioop
import logging
import audiodb
from tqdm import tqdm
from uuid import uuid4
from chatterbot import ChatBot
from chatterbot.conversation import Statement
from custom_trainer import TranslatedListTrainer
from custom_trainer import CustomTrainer
from chatterbot.comparisons import LevenshteinDistance
#from chatterbot.comparisons import SpacySimilarity
#from chatterbot.comparisons import JaccardSimilarity
from chatterbot.response_selection import get_random_response
#from chatterbot.response_selection import get_most_frequent_response
from gtts import gTTS
from io import BytesIO
from pathlib import Path
from faker import Faker
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv
from fakeyou.objects import *
from fakeyou.exception import *
from sqlitedict import SqliteDict
from pydub import AudioSegment
from essential_generators import DocumentGenerator, MarkovTextGenerator, MarkovWordGenerator
from libretranslator import LibreTranslator
from bs4 import BeautifulSoup
from glob import glob
from zipfile import ZipFile

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")
TRANSLATOR_PROVIDER = os.environ.get("TRANSLATOR_PROVIDER")
TRANSLATOR_BASEURL = os.environ.get("TRANSLATOR_BASEURL")
MYMEMORY_TRANSLATOR_EMAIL = os.environ.get("MYMEMORY_TRANSLATOR_EMAIL")
FAKEYOU_USER = os.environ.get("FAKEYOU_USER")
FAKEYOU_PASS = os.environ.get("FAKEYOU_PASS")

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))

fy=fakeyou.FakeYou()

fake = Faker()

wikipedia.set_lang("it")

class TqdmToLogger(io.StringIO):
    """
        Output stream for TQDM which will output to logger module instead of
        the StdOut.
    """
    logger = None
    level = None
    buf = ''
    def __init__(self,logger,level=None):
        super(TqdmToLogger, self).__init__()
        self.logger = logger
        self.level = level or logging.INFO
    def write(self,buf):
        self.buf = buf.strip('\r\n\t ')
    def flush(self):
        self.logger.log(self.level, self.buf)

class TrainJson():
  def __init__(self, info, language, sentences):
        self.info = info
        self.language = language
        self.sentences = sentences

class BaseClass(object):
    def __init__(self, classtype):
        self._type = classtype

def ClassFactory(name, argnames, BaseClass=BaseClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # here, the argnames variable is the one passed to the
            # ClassFactory call
            if key not in argnames:
                raise TypeError("Argument %s not valid for %s" 
                    % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseClass.__init__(self, name[:-len("Class")])
    newclass = type(name, (BaseClass,),{"__init__": __init__})
    return newclass



def wiki_summary(testo: str):
  try:
    definition = wikipedia.summary(testo, sentences=1, auto_suggest=True, redirect=True)
    return testo + ": " + definition
  except:
    return EXCEPTION_WIKIPEDIA + testo


def generate(filename: str):
  with open(filename, "rb") as fmp3:
      data = fmp3.read(1024)
      while data:
          yield data
          data = fmp3.read(1024)

def get_tts_google(text: str, chatid="000000", language="it", save=True):
  data = None
  if save:
    data = audiodb.select_by_name_chatid_voice_language(text, chatid, "google", language)
  if data is not None:
    return data
  else:
    tts = gTTS(text=text, lang=language, slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    sound = AudioSegment.from_mp3(fp)
    memoryBuff = BytesIO()
    sound.export(memoryBuff, format='mp3', bitrate="256")
    memoryBuff.seek(0)
    #if chatid == "000000" and save:
    if chatid == "000000" and save:
      audiodb.insert(text, chatid, memoryBuff, "google", language)
      return audiodb.select_by_name_chatid_voice_language(text, chatid, "google", language)
    else:
      return memoryBuff
    #return memoryBuff
    #return fp

def populate_tts_google(text: str, chatid="000000", language="it"):
  data = audiodb.select_by_name_chatid_voice_language(text, chatid, "google")
  if data is not None:
    return False
  else:
    tts = gTTS(text=text, lang="it", slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    sound = AudioSegment.from_mp3(fp)
    memoryBuff = BytesIO()
    sound.export(memoryBuff, format='mp3', bitrate="256")
    memoryBuff.seek(0)
    audiodb.insert(text, chatid, memoryBuff, "google", language)
    return True
    #return memoryBuff
    #return fp

def clean_input(testo: str):
  re_equ = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
  ck_url = re.findall(re_equ, testo)
  if(ck_url):
    return False
  else:
    return True

def get_chatterbot(chatid: str, train: False, lang = "it"):

  dbfile=chatid+"-db.sqlite3"

  spacymodel = lang+"_core_news_sm"

  fle = Path('./config/'+dbfile)
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

  nlp = spacy.load(spacymodel)
  chatbot = ChatBot(
      'PezzenteCapo',
      storage_adapter='chatterbot.storage.SQLStorageAdapter',
      database_uri='sqlite:///config/'+dbfile,
      statement_comparison_function = LevenshteinDistance,
      response_selection_method = get_random_response,
      logic_adapters=[
          {
              'import_path': 'chatterbot.logic.BestMatch',
              'maximum_similarity_threshold': 0.90
          }
      ]
  )

  with sqlite3.connect("./config/"+dbfile) as db:
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) from STATEMENT ''')
    result=cursor.fetchall()
    if result == 0 :
      learn('ciao', 'ciao', chatbot)
      if train:
        trainer = CustomTrainer(chatbot, translator_baseurl=TRANSLATOR_BASEURL, translator_email=MYMEMORY_TRANSLATOR_EMAIL)
        trainer.train()      
  return chatbot


def learn(testo: str, risposta: str, chatbot: ChatBot):
  input_statement = Statement(text=testo)
  correct_response = Statement(text=risposta)
  chatbot.learn_response(correct_response, previous_statement=input_statement)

def recreate_file(filename: str):
  if os.path.exists(filename):
    os.remove(filename)
    fle = Path(filename)
    fle.touch(exist_ok=True)  

def get_youtube_audio(link: str, chatid: str):
  try:
    youtubefile = os.environ.get("TMP_DIR")+'/song_guild_'+str(chatid)
    ydl_opts = {
        'outtmpl': youtubefile,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    url = "https://www.youtube.com/watch?v=" + link

    logging.info("Trying to download YouTube link: "+url)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

    with open(youtubefile+".mp3", "rb") as fh:
      fp = BytesIO(fh.read())
    fp.seek(0)
    os.remove(youtubefile+".mp3")
    return fp, url  
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return None


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;'),
            ('', '“'),
            ('', '"'),
        )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s.strip()

def get_joke(cat: str):
  try:
    url="http://192.168.1.160:3050/v1/jokes"
    if cat != "":
      params="category="+cat
      url=url+"?"+params
    r = requests.get(url)
    if r.status_code != 200:
      return "API barzellette non raggiungibile..."
    else:
#      full_json = r.text
      full = json.loads(r.text)
      text = html_decode(full['data']['text'])
      return text
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return "Riprova tra qualche secondo..."


def scrape_jokes():
  scrape_internal("LAPECORASCLERA", "0")
  scrape_internal("FUORIDITESTA", "0")

def scrape_internal(scraper: str, page: str):
  try:
    url="http://192.168.1.160:3050/v1/mngmnt/scrape"
    params="scraper="+scraper
    if page != 0:
      params = params+"&pageNum="+page
    url=url+"?"+params
    r = requests.get(url)
    if r.status_code != 200:
      pass
    else:
      full_json = r.text
      full = json.loads(full_json)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def get_random_date():
  offset = '-' + str(random.randint(1, 4)) + 'y'
  date = fake.date_time_between(start_date=offset, end_date='now').strftime("%Y-%m-%d")
  return date

def extract_sentences_from_chatbot(filename, chatid="000000", distinct=True, randomize=True):
  try:

    if os.path.exists(filename):
      os.remove(filename)
      
    dbfile=chatid+"-db.sqlite3"
    sqliteConnection = sqlite3.connect('./config/'+dbfile)
    cursor = sqliteConnection.cursor()

    sqlite_select_sentences_query = ""
    if distinct and randomize:
      sqlite_select_sentences_query = """SELECT DISTINCT text FROM statement ORDER BY RANDOM()"""
    elif not distinct and not randomize:
      sqlite_select_sentences_query = """SELECT text FROM statement ORDER BY TEXT"""
    elif distinct and not randomize:
      sqlite_select_sentences_query = """SELECT DISTINCT text FROM statement ORDER BY TEXT"""
    elif not distinct and randomize:
      sqlite_select_sentences_query = """SELECT text FROM statement ORDER BY RANDOM()"""

    data = ()

    cursor.execute(sqlite_select_sentences_query, data)
    records = cursor.fetchall()

    
    records_len = len(records)-1


    with open(filename, 'a') as sentence_file:
      for row in records:
        try:
          if row[0] and row[0] != "":
            sanitized = row[0].strip()
            logging.info('extract_sentences_from_chatbot -- "' + sanitized + '"')
            if sanitized[-1] not in string.punctuation:
              if randomize:
                if bool(random.getrandbits(1)):
                  sanitized = sanitized + "."
                else:
                  sanitized = sanitized + " "
              else:
                sanitized = sanitized + "."
            if records.index(row) != records_len:
              if randomize:
                if bool(random.getrandbits(1)):
                  sanitized = sanitized + "\n"
                else:
                  sanitized = sanitized + " "
              else:
                sanitized = sanitized + "\n"
            sentence_file.write(sanitized)
        except Exception as e:
          exc_type, exc_obj, exc_tb = sys.exc_info()
          fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
          logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

    cursor.close()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return False
  finally:
    if sqliteConnection:
        sqliteConnection.close()
  return True

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def train_json(json_req, chatbot: ChatBot):
  try:
    if not json_req:
      logging.info(empty_template_trainfile_json())
    else:
      content = json_req
      trainer = TranslatedListTrainer(chatbot, lang=content['language'], translator_baseurl=TRANSLATOR_BASEURL, translator_email=MYMEMORY_TRANSLATOR_EMAIL)
      i = 0
      while(i < len(content['sentences'])):
        trainarray=[]
        j = 0
        while (j < len(content['sentences'][i]["message"+str(i)])):
          trainarray.append(content['sentences'][i]["message"+str(i)][j])
          j = j + 1
        
        trainer.train(trainarray)
        i = i + 1

      logging.info(TrainJson("Done.", content['language'], []).__dict__, exc_info=1)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def empty_template_trainfile_json():
  trainJsonSentencesArray=[]

  message0=[]
  message0.append("Hello, How are you?")
  message0.append("I am fine, thanks.")

  Conversation0 = ClassFactory("ConversationClass", "message0")
  conversation0 = Conversation0(message0=message0)

  trainJsonSentencesArray.append(conversation0.__dict__)

  message1=[]
  message1.append("How was your day?")
  message1.append("It was good, thanks.")

  Conversation1 = ClassFactory("ConversationClass", "message1")
  conversation1 = Conversation1(message1=message1)

  trainJsonSentencesArray.append(conversation1.__dict__)

  trainJson = TrainJson("Error! Please use this format.", "en", trainJsonSentencesArray)

  return trainJson.__dict__

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "txt"

def train_txt(trainfile, chatbot: ChatBot, lang: str):
  try:
      logging.info("Loading: %s", trainfile)
      trainer = TranslatedListTrainer(chatbot, lang=lang, translator_baseurl=TRANSLATOR_BASEURL, translator_email=MYMEMORY_TRANSLATOR_EMAIL)
      trainfile_array = []
      with open(trainfile) as file:
          for line in file:
              if line.split():
                trainfile_array.append(line.strip())
              else:
                trainer.train(trainfile_array)
                trainfile_array=[]
      if len(trainfile_array) > 0:
        trainer.train(trainfile_array)
      logging.info("Done. Deleting: " + trainfile)
      os.remove(trainfile)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def delete_by_text(chatid: str, text: str, force = False):
  try:
    dbfile='./config/'+chatid+"-db.sqlite3"
    sqliteConnection = sqlite3.connect(dbfile)
    cursor = sqliteConnection.cursor()

    sqlite_delete_query = "DELETE FROM Statement WHERE text like '" + text + "%' OR text like '%" + text + "' OR text LIKE '%" + text + "%' OR text = '" + text + "' COLLATE NOCASE"

    data_tuple = ()

    logging.info("delete_by_text - Executing: %s", sqlite_delete_query)

    cursor.execute(sqlite_delete_query, data_tuple)
    sqliteConnection.commit()
    cursor.close()

    if force:
      delete_from_audiodb_by_text(chatid, text)
      return('Frasi con parola chiave "' + text + '" cancellate dal db chatbot e dal db audio!')
    else:
      return('Frasi con parola chiave "' + text + '" cancellate dal db chatbot!')
  except sqlite3.Error as error:
    logging.error("Failed to delete data from sqlite", exc_info=1)
    return("Errore!")
  finally:
    if sqliteConnection:
        sqliteConnection.close()



def delete_from_audiodb_by_text(chatid: str, text: str):
  try:
    dbfile="./config/audiodb.sqlite3"
    sqliteConnection = sqlite3.connect(dbfile)
    cursor = sqliteConnection.cursor()

    sqlite_delete_query = "DELETE FROM Audio WHERE chatid = '" + chatid + "' and (name like '" + text + "%' OR name like '%" + text + "' OR name LIKE '%" + text + "%' OR name = '" + text + "') COLLATE NOCASE"

    data_tuple = ()

    logging.info("delete_from_audiodb_by_text - Executing:  %s", sqlite_delete_query, exc_info=1)

    cursor.execute(sqlite_delete_query, data_tuple)
    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    logging.error("Failed to delete data from sqlite", exc_info=1)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def get_tts(text: str, chatid="000000", voice=None, israndom=False, language="it", save=True, call_fy=True):
  try:
    if voice is None or voice == "null" or voice == "random":
      voice_to_use = get_random_voice()
    else:
      voice_to_use = voice
    #if chatid != "000000" or language != "it":
    if chatid != "000000" or language != "it":
      return get_tts_google(text.strip(), chatid=chatid, language=language, save=save)
    elif voice_to_use != "google":
      datafy = None
      if save:
        datafy = audiodb.select_by_name_chatid_voice_language(text.strip(), chatid, voice_to_use, language)
      if datafy is not None:
        return datafy
      elif call_fy:
        if bool(random.getrandbits(1)):
          proxies = {'http': 'http://192.168.1.160:9058'}
          fy.session.proxies.update(proxies)
        else:
          proxies = {}
          fy.session.proxies.update(proxies)
        wav = fy.say(text.strip(), voice_to_use)
        if wav is not None:
          sound = AudioSegment.from_wav(BytesIO(bytes(wav.content)))
          out = BytesIO()
          sound.export(out, format='mp3', bitrate="256")
          out.seek(0)
          if save:
            audiodb.insert(text.strip(), chatid, out, voice_to_use, language)
            return audiodb.select_by_name_chatid_voice_language(text.strip(), chatid, voice_to_use, language)
          else:
            return out
        elif voice == "random" or voice == "google":
          return get_tts_google(text.strip(), chatid=chatid, language="it")
        else:
          return None
      else:
        fyfromdb = audiodb.select_by_name_chatid_voice_language(text.strip(), chatid, voice_to_use, language)
        if fyfromdb is not None:
          return fyfromdb
        else:
          return get_tts_google(text.strip(), chatid=chatid, language="it")
    else:
      return get_tts_google(text.strip(), chatid=chatid, language=language, save=save)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    if voice == "random" or israndom:
      return get_tts_google(text.strip(), chatid=chatid, language=language, save=save)
    else:
      raise Exception(e)

    
def download_tts(id: int):
  try:
    return audiodb.select_audio_by_id(id)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    raise Exception(e)

def populate_tts(text: str, chatid="000000", voice=None, israndom=False, language="it"):
  try:
    if voice is None or voice == "null" or voice == "random":
      voice_to_use = get_random_voice()
    else:
      voice_to_use = voice
    if voice_to_use != "google": 
      datafy = audiodb.select_by_name_chatid_voice_language(text.strip(), chatid, voice_to_use, language)
      if datafy is not None:
        return False
      else:
        if bool(random.getrandbits(1)):
          proxies = {'http': 'http://192.168.1.160:9058'}
          fy.session.proxies.update(proxies)
        else:
          proxies = {}
          fy.session.proxies.update(proxies)
        wav = fy.say(text.strip(), voice_to_use)
        if wav is not None:
          sound = AudioSegment.from_wav(BytesIO(bytes(wav.content)))
          out = BytesIO()
          sound.export(out, format='mp3', bitrate="256")
          out.seek(0)
          audiodb.insert(text.strip(), chatid, out, voice_to_use, language)
          return True
        raise Exception("FakeYou Generation KO")
    else:
      return populate_tts_google(text.strip(), chatid=chatid, language=language)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno)
    raise Exception(e)

def get_random_voice():
  localvoices = get_fakeyou_voices()
  title, token = random.choice(list(localvoices.items()))
  return token

def get_fakeyou_voices(category="Italiano"):
  #fy.login(FAKEYOU_USER,FAKEYOU_PASS)
  localvoices = {}
  with open('voices.json') as filejson:
    loaded = json.load(filejson)
    for iterator in loaded:
      localvoices[iterator] = loaded[iterator]
  return localvoices

def list_fakeyou_voices(lang:str):
  voices=fy.list_voices(size=0)
  foundvoices = {}
		
  for langTag,voiceJson in zip(voices.langTag,voices.json):
    if lang.lower() in langTag.lower():
      foundvoices[voiceJson["title"]] = voiceJson["model_token"]
		
  return foundvoices

def login_fakeyou():
  try:
    fy.login(FAKEYOU_USER,FAKEYOU_PASS)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno)

def get_random_from_bot(chatid: str):
  try:
    dbfile=chatid+"-db.sqlite3"
    sqliteConnection = sqlite3.connect('./config/'+dbfile)
    cursor = sqliteConnection.cursor()

    
    sqlite_select_sentences_query = """SELECT text FROM statement ORDER BY RANDOM() LIMIT 1;"""

    data = ()

    cursor.execute(sqlite_select_sentences_query, data)
    records = cursor.fetchall()

    count = 0

    for row in records:
      sentence = row[0]

    cursor.close()
    return sentence
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    raise Exception(e)
  finally:
    if sqliteConnection:
        sqliteConnection.close()



def populate_audiodb(count: int, chatid: str):  
  try:

    for file in os.listdir('./config/'):
      if file.endswith("-db.sqlite3"):
        
        chatid_internal = file.replace("-db.sqlite3", "")

        if (chatid is not None and chatid == chatid_internal) or chatid is None:

          logging.info("populate_audiodb - STARTED POPULATION\n         CHATID: %s\n         LIMIT: %s", chatid_internal, str(count))

          login_fakeyou()
          voices = get_fakeyou_voices()
          #voices={}
          #voices["google"] = "google"
          listvoices = list(voices.items())


          dbfile=os.path.join('./config/', file)

          sqliteConnection = sqlite3.connect(+dbfile)
          cursor = sqliteConnection.cursor()
          

          cursor.execute("ATTACH DATABASE ? AS audiodb",("./config/audiodb.sqlite3",))

          sqlite_select_sentences_query = "SELECT DISTINCT * FROM ( "
          sqlite_select_sentences_query = sqlite_select_sentences_query + " SELECT * FROM (SELECT DISTINCT statement.text as name FROM statement WHERE statement.text NOT IN (SELECT audiodb.audio.name from audiodb.audio) ORDER BY RANDOM() LIMIT " + str(count) + ")"
          sqlite_select_sentences_query = sqlite_select_sentences_query + " UNION "
          sqlite_select_sentences_query = sqlite_select_sentences_query + " SELECT * FROM (SELECT DISTINCT audiodb.audio.name as name from audiodb.audio WHERE CHATID = ? GROUP BY audio.name HAVING COUNT(audio.name) < " + str(len(listvoices)) + " ORDER BY RANDOM() LIMIT " + str(count) + ")"
          sqlite_select_sentences_query = sqlite_select_sentences_query + ") LIMIT " + str(count);

          log.info("populate_audiodb\n         Executing SQL: %s", sqlite_select_sentences_query)

          data = (chatid_internal)

          cursor.execute(sqlite_select_sentences_query, data)
          records = cursor.fetchall()

          count = 0
          tqdm_out = TqdmToLogger(logging,level=logging.INFO)

          sentences = [] 

          for row in records:
            sentences.append(row[0])

          cursor.close()
          sqliteConnection.close()


          for sentence in tqdm(sentences,file=tqdm_out,desc="populate_audiodb - Progress",mininterval=60,):
            random.shuffle(listvoices)
            for key, voice in listvoices:
            #for key, voice in progressBar(listvoices, prefix = 'populate_audiodb - Progress:', suffix = 'Complete', length = 50):
              result = False
              try:
                logging.info("populate_audiodb - START ELAB\n         CHATID: %s\n         VOICE: %s (%s)\n         SENTENCE: %s", chatid_internal, voice, key, sentence)
                generation = ""
                inserted = ""
                result = populate_tts(sentence, chatid=chatid_internal, voice=voice)
                if result:
                  inserted="Done"
                else:
                  inserted="Skipped (Already in db)"
                logging.info("populate_audiodb - END ELAB  \n         CHATID: %s\n         VOICE: %s (%s)\n         SENTENCE: %s\n         RESULT: %s", chatid_internal, voice, key, sentence, inserted)
              except Exception as e:
                inserted="Failed"
                logging.error("populate_audiodb - ERROR ELAB\n         CHATID: %s\n         VOICE: %s (%s)\n         SENTENCE: %s\n         RESULT: %s", chatid_internal, voice, key, sentence, inserted, exc_info=1)  
                if str(e).startswith("check token and text,"):
                  if utils.select_count_by_text_chatid_voice(sentence,chatid_internal,voice) == 0:
                    audiodb.insert(sentence, chatid_internal, memoryBuff, voice, "it", is_correct=0)
              finally:
                if voice != "google" and (inserted == "Done" or inserted == "Failed"):
                    time.sleep(60)
          logging.info("populate_audiodb - ENDED POPULATION\n         CHATID: %s\n         LIMIT: %s", chatid, str(count))
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    raise Exception(e)
  finally:
    if sqliteConnection:
      sqliteConnection.close()



def backupdb(chatid: str):  
  try:
    dbfile='./config/'+chatid+"-db.sqlite3"
    dst="./config/backups/" + chatid + "-db_backup_" + str(time.time()) + ".sqlite3"
    shutil.copyfile(dbfile, dst)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    raise Exception(e)

def restore(chatid: str, text: str):
  sentences = ""
  try:
    dbfile="./config/audiodb.sqlite3"
    sqliteConnection = sqlite3.connect(dbfile)
    cursor = sqliteConnection.cursor()

    sqlite_select_query = """SELECT DISTINCT name FROM Audio"""
    data_tuple = ()

    if(text is not None):
      
      sqlite_select_query = sqlite_select_query + " WHERE chatid = '" + chatid + "' and (name like '" + text + "%' OR name like '%" + text + "' OR name LIKE '%" + text + "%' OR name = '" + text + "') COLLATE NOCASE"

    cursor.execute(sqlite_select_query, data_tuple)
    records = cursor.fetchall()

    logging.info("restore - Executing: %s", sqlite_select_query)
    
    for row in records:
      sentences = sentences + "\n" + row[0] 

    cursor.close()

  except sqlite3.Error as error:
    logging.error("Failed to select data from sqlite", exc_info=1)
    return("Errore!")
  finally:
    if sqliteConnection:
        sqliteConnection.close()
  return BytesIO(bytes(sentences,'utf-8'))

def get_audios_for_ft():
  voices = get_fakeyou_voices()
  datas = audiodb.select_by_chatid()
  audios = []
  for data in datas:
    key = [k for k, v in voices.items() if v == data[4]][0]
    internal = []
    internal.append(data[0])
    internal.append(data[1])
    #internal.append("https://"+API_USER+":"+API_PASS+"@discord-voicebot.fabiovalentino.it/chatbot_audio/download/"+ str(data[0]))
    internal.append("https://discord-voicebot.fabiovalentino.it/chatbot_audio/download/"+ str(data[0]))
    internal.append(key)
    internal.append(data[5])
    audios.append(internal)
  return audios

def get_audios_list_for_ft():
  voices = get_fakeyou_voices()
  datas = audiodb.select_list_by_chatid()
  audios = []
  for data in datas:
    key = [k for k, v in voices.items() if v == data[4]][0]
    internal = []
    internal.append(data[1])
    #internal.append("https://"+API_USER+":"+API_PASS+"@discord-voicebot.fabiovalentino.it/chatbot_audio/download/"+ str(data[0]))
    internal.append("https://discord-voicebot.fabiovalentino.it/chatbot_audio/download/"+ str(data[0]))
    internal.append(key)
    audios.append(internal)
  return audios

def init_generator_models():
  for file in os.listdir('./config/'):
    if file.endswith("-db.sqlite3"):
      
      chatid = file.replace("-db.sqlite3", "")

      logging.info("START -- essential_generators -- Models Generator")

      filename='./config/sentences_'+chatid+'.txt'
      
      if extract_sentences_from_chatbot(filename, chatid=chatid):

        text_model_path = './config/markov_textgen_'+chatid+'.json'
        word_model_path = './config/markov_wordgen_'+chatid+'.json'

        init_text_generator(corpus=filename, output=text_model_path)
        init_word_generator(corpus=filename, output=word_model_path)

        logging.info("END -- essential_generators -- Models Generator")

def init_text_generator(corpus=None, output=None):

    if os.path.exists(output):
      os.remove(output)

    with open(corpus, 'r', encoding='utf-8') as fp:
      set4 = fp.read()

    gen = MarkovTextGenerator(load_model=False)
    gen.train(set4)
    gen.save_model(output)

def init_word_generator(corpus=None, output=None):
    
    if os.path.exists(output):
      os.remove(output)

    with open(corpus, 'r', encoding='utf-8') as fp:
      set4 = fp.read()

    gen = MarkovWordGenerator(load_model=False)
    gen.train(set4)
    gen.save_model(output)

def generate_sentence(chatid: str):

  text_model_path = './config/markov_textgen_'+chatid+'.json'
  word_model_path = './config/markov_wordgen_'+chatid+'.json'

  text_generator=MarkovTextGenerator(model=text_model_path, load_model=True)
  word_generator=MarkovWordGenerator(model=word_model_path, load_model=True)

  generator = DocumentGenerator(word_generator=word_generator, text_generator=text_generator)

  return generator.sentence()

def generate_paragraph(chatid: str):

  text_model_path = './config/markov_textgen_'+chatid+'.json'
  word_model_path = './config/markov_wordgen_'+chatid+'.json'

  text_generator=MarkovTextGenerator(model=text_model_path, load_model=True)
  word_generator=MarkovWordGenerator(model=word_model_path, load_model=True)

  generator = DocumentGenerator(word_generator=word_generator, text_generator=text_generator)

  return generator.paragraph()

def random_myinstants_sound(query: str):
  try:
    r = None
    if query == "random":
      r = requests.get('https://www.myinstants.com/it/index/it/')
    else:
      r = requests.get('http://www.myinstants.com/search/?name='+urllib.parse.quote(query))
    soup = BeautifulSoup(r.text, 'html.parser')
    founds = soup.find_all("div", class_="instant")
          
    url = None
    name = None
    if len(founds) > 0:
      size = len(founds)
      n = random.randint(0,size-1)
      link = founds[n]

      for content in link.contents:
        if '"small-button"' in str(content):
          url = "http://www.myinstants.com" + content.attrs['onclick'].split("'")[1]
        if '"instant-link link-secondary"' in str(content):
          name = content.contents[0]
        if url is not None and name is not None:
          result = {
            "url": url,
            "name": name
          }
          return result
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return None

def query_myinstants_sound(query: str):
  try:
    r = requests.get('http://www.myinstants.com/search/?name='+urllib.parse.quote(query))
    soup = BeautifulSoup(r.text, 'html.parser')
    founds = soup.find_all("div", class_="instant")
    results = []
    size = len(founds)
    if size > 0:
      if size > 25:
        size = 25
      for n in range(0,size):
        url = None
        name = None
        for content in founds[n].contents:
          if '"small-button"' in str(content):
            url = "http://www.myinstants.com" + content.attrs['onclick'].split("'")[1]
          if '"instant-link link-secondary"' in str(content):
            name = content.contents[0]
          if url is not None and name is not None:
            result = {
              "url": url,
              "name": name
            }
            results.append(result)
            break
    return results
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return []

def clean_audio_zip():
  dirname = "./config/download_audio_zip"
  if os.path.exists(dirname):
    rmdir(dirname)

def download_audio_zip(chatid: str):
  try:
    dirname = "./config/download_audio_zip"
    if not os.path.exists(dirname):
      os.mkdir(dirname)
      voices = get_fakeyou_voices()
      datas = audiodb.select_data_name_voice_by_chatid(chatid)
      audios = []
      for data in datas:
        audio = BytesIO(data[0])
        name  = data[1].replace(" ", "_")
        voice = ([k for k, v in voices.items() if v == data[2]][0]).replace(" ", "_")

        if(len(name) > 40):
          name = name[0:40]

        filename_tmp1 = name + "_" + voice
        filename_tmp2 = ''.join(e for e in filename_tmp1 if e.isalnum() or e == "_")
        filename = dirname + "/" + filename_tmp2 +".mp3"
        with open(filename, "wb") as outfile:
            outfile.write(audio.getbuffer())
    shutil.make_archive(dirname, 'zip', dirname)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return False

def rmdir(directory):
  directory = Path(directory)
  for item in directory.iterdir():
      if item.is_dir():
          rmdir(item)
      else:
          item.unlink()
  directory.rmdir()