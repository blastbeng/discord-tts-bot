import re
import shutil
import random
import wikipedia
import json
import requests
import sys
import threading
import os
import urllib
import pymongo
import yt_dlp
from functools import lru_cache
import string
import fakeyou
import time
import logging
import audiodb
import hashlib
import dotenv
import custom_mongo_adapter
from chatterbot import ChatBot
from chatterbot import languages
from chatterbot.conversation import Statement
from custom_trainer import CustomListTrainer
from custom_trainer import CustomTrainer
#from chatterbot.comparisons import LevenshteinDistance
from chatterbot.comparisons import SpacySimilarity
#from chatterbot.comparisons import JaccardSimilarity
#from chatterbot.response_selection import get_random_response
from chatterbot.response_selection import get_most_frequent_response
from gtts import gTTS
from io import BytesIO
from pathlib import Path
from faker import Faker
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv
from fakeyou.objects import *
from fakeyou.exception import *
from pydub import AudioSegment
from essential_generators import DocumentGenerator, MarkovTextGenerator, MarkovWordGenerator
from bs4 import BeautifulSoup
from exceptions import AudioLimitException
from exceptions import TimeExceededException
import multiprocessing
from functools import wraps
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by  import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support    import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from random import randint
from boto3 import client


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

polly = client('polly', aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"), 
                        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"), 
                        region_name='eu-central-1')

try:
  fy.login(FAKEYOU_USER,FAKEYOU_PASS)
except Exception as e:
  exc_type, exc_obj, exc_tb = sys.exc_info()
  fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
  logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno)

fake = Faker()

class SentenceToLearn():
  def __init__(self, chatid, language, text):
        self.chatid = chatid
        self.language = language
        self.text = text

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

def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer

def function_runner(*args, **kwargs):
    """Used as a wrapper function to handle
    returning results on the multiprocessing side"""

    send_end = kwargs.pop("__send_end")
    function = kwargs.pop("__function")
    try:
        result = function(*args, **kwargs)
    except Exception as e:
        send_end.send(e)
        return
    send_end.send(result)


@parametrized
def run_with_timer(func, max_execution_time):
    @wraps(func)
    def wrapper(*args, **kwargs):
        recv_end, send_end = multiprocessing.Pipe(False)
        kwargs["__send_end"] = send_end
        kwargs["__function"] = func
        
        ## PART 2
        p = multiprocessing.Process(target=function_runner, args=args, kwargs=kwargs)
        p.start()
        p.join(max_execution_time)
        if p.is_alive():
            p.terminate()
            p.join()
            raise TimeExceededException("Exceeded Execution Time")
        result = recv_end.recv()

        if isinstance(result, Exception):
            raise result

        return result

    return wrapper


def wiki_summary(testo: str, lang: str):
  try:
    wikipedia.set_lang(lang)
    definition = wikipedia.summary(testo, sentences=1, auto_suggest=True, redirect=True)
    return testo + ": " + definition
  except:
    return None


def generate(filename: str):
  with open(filename, "rb") as fmp3:
      data = fmp3.read(1024)
      while data:
          yield data
          data = fmp3.read(1024)

def get_tts_aws(text: str, chatid="000000", language="it", save=True, limit=True, user=None):
  data = audiodb.select_by_name_chatid_voice_language(text, chatid, "aws", language)
  if data is not None:
    return data
  else:
    response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Giorgio')

    stream = response.get('AudioStream')
    mp3_bytes = stream.read()
    mp3_fp = BytesIO(mp3_bytes)
    mp3_fp.seek(0)
    stream.close()
    
    if save:      
      #threading.Thread(target=lambda: thread_save_aws(text, mp3_fp, chatid=chatid, language=language, user=user)).start()
      audiodb.insert_or_update(text.strip(), chatid, None, "aws", language, is_correct=1, user=user)
    return mp3_fp

def thread_save_aws(text: str, mp3_fp, chatid="000000", language="it", user=None):
  hashtext = hashlib.md5((text+"_aws").encode('utf-8')).hexdigest()
  dirsave = "." + get_slashes() + 'audios'
  if not os.path.exists(dirsave):
    os.makedirs(dirsave)
  filesave = dirsave + get_slashes() + hashtext + ".mp3"  
  sound = AudioSegment.from_mp3(mp3_fp)
  sound.export(filesave, format='mp3', bitrate="256k")
  duration = (len(sound) / 1000.0)
  audiodb.insert_or_update(text, chatid, filesave, "aws", language, duration=duration, user=user)

def get_tts_google(text: str, chatid="000000", language="it", save=True, limit=True, user=None):
  data = audiodb.select_by_name_chatid_voice_language(text, chatid, "google", language)
  if data is not None:
    return data
  else:
    mp3_fp = BytesIO()
    tts = gTTS(text=text, lang=language, slow=False)
    if save:      
      #threading.Thread(target=lambda: thread_save_google(text, tts, chatid=chatid, language=language, user=user)).start()
      audiodb.insert_or_update(text.strip(), chatid, None, "google", language, is_correct=1, user=user)
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

def thread_save_google(text: str, tts, chatid="000000", language="it", user=None):
    hashtext = hashlib.md5((text+"_google").encode('utf-8')).hexdigest()
    dirsave = "." + get_slashes() + 'audios'
    if not os.path.exists(dirsave):
      os.makedirs(dirsave)
    filesave = dirsave + get_slashes() + hashtext + ".mp3"
    tts.save(filesave)
    sound = AudioSegment.from_mp3(filesave)
    duration = (len(sound) / 1000.0)
    audiodb.insert_or_update(text, chatid, filesave, "google", language, duration=duration, user=user)

def populate_tts_aws(text: str, chatid="000000", language="it"):
  data = audiodb.select_by_name_chatid_voice_language(text, chatid, "aws", language)
  if data is not None:
    return False
  else:
    response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Giorgio')

    stream = response.get('AudioStream')
    hashtext = hashlib.md5((text+"_aws").encode('utf-8')).hexdigest()
    dirsave = "." + get_slashes() + 'audios'
    if not os.path.exists(dirsave):
      os.makedirs(dirsave)
    filesave = dirsave + get_slashes() + hashtext + ".mp3"    
    sound = AudioSegment.from_mp3(BytesIO(stream.read()))
    sound.export(filesave, format='mp3', bitrate="256k")
    duration = (len(sound) / 1000.0)
    if duration > int(os.environ.get("MAX_TTS_DURATION")):
      audiodb.insert_or_update(text, chatid, None, "aws", language, is_correct=0, duration=duration)
      return None
    else:
      #sound.duration_seconds == duration
      memoryBuff = BytesIO()
      sound.export(memoryBuff, format='mp3', bitrate="256k")
      memoryBuff.seek(0)
      audiodb.insert_or_update(text, chatid, filesave, "aws", language, duration=duration)
      return True
    #return memoryBuff
    #return fp

def populate_tts_google(text: str, chatid="000000", language="it"):
  data = audiodb.select_by_name_chatid_voice_language(text, chatid, "google", language)
  if data is not None:
    return False
  else:
    tts = gTTS(text=text, lang="it", slow=False)
    hashtext = hashlib.md5((text+"_google").encode('utf-8')).hexdigest()
    dirsave = "." + get_slashes() + 'audios'
    if not os.path.exists(dirsave):
      os.makedirs(dirsave)
    filesave = dirsave + get_slashes() + hashtext + ".mp3"
    tts.save(filesave)
    sound = AudioSegment.from_mp3(filesave)
    duration = (len(sound) / 1000.0)
    if duration > int(os.environ.get("MAX_TTS_DURATION")):
      audiodb.insert_or_update(text, chatid, None, "google", language, is_correct=0, duration=duration)
      return None
    else:
      #sound.duration_seconds == duration
      memoryBuff = BytesIO()
      sound.export(memoryBuff, format='mp3', bitrate="256k")
      memoryBuff.seek(0)
      audiodb.insert_or_update(text, chatid, filesave, "google", language, duration=duration)
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

def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

def get_chatterbot(chatid: str, train: False, lang = "it"):

  dbfile=chatid+"-db"

  spacymodel = lang+"_core_news_sm"

  language = None

  classes = languages.get_language_classes()
  for clazz in classes:
    langclazz = get_class("chatterbot.languages." + clazz[0])
    if langclazz.ISO_639_1 == lang:
      language = langclazz
      break

  chatbot = ChatBot(
      'PezzenteCapo',
      storage_adapter='custom_mongo_adapter.CustomMongoAdapter',
      database_uri='mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/',
      database_name=dbfile,
      statement_comparison_function = SpacySimilarity,
      response_selection_method = get_most_frequent_response,
      tagger_language=language,
      logic_adapters=[
          {
              'import_path': 'chatterbot.logic.BestMatch',
              'maximum_similarity_threshold': 0.90
          }
      ]
  )

  if train:
    trainer = CustomTrainer(chatbot, translator_provider=TRANSLATOR_PROVIDER, translator_baseurl=TRANSLATOR_BASEURL, translator_email=MYMEMORY_TRANSLATOR_EMAIL)
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


def get_random_date():
  offset = '-' + str(random.randint(1, 4)) + 'y'
  date = fake.date_time_between(start_date=offset, end_date='now').strftime("%Y-%m-%d")
  return date


def extract_sentences_from_chatbot(filename, chatid="000000"):
  try:    

    dbfile = chatid + "-db"
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    statements = chatbotdb["statements"]

    with open(filename, 'a', encoding="utf8") as sentence_file:      
      for row in statements.distinct('text'): 
        logging.debug('extract_sentences_from_chatbot - [chatid:' + chatid + '] - "' + row + '"')
        sentence_file.write(row)
        sentence_file.write("\n")


    lines = open(filename, 'r', encoding="utf8").readlines()
    lines_set = set(lines)
    out  = open(filename, 'w', encoding="utf8")
    for line in lines_set:
        out.write(line)

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return False
  return True

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str



def allowed_file(filename, extension="txt"):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extension

def train_txt(trainfile, chatbot: ChatBot, lang: str, chatid: str):
  try:
      logging.info("Loading: %s", trainfile)
      trainer = CustomListTrainer(chatbot)
      trainfile_array = []
      with open(trainfile, encoding="utf-8") as file:
          for line in file:
              trainfile_array.append(line.strip())
      if len(trainfile_array) > 0:
        random.shuffle(trainfile_array)
        trainer.train(trainfile_array)
      logging.info("Done. Deleting: " + trainfile)
      os.remove(trainfile)

      clean_duplicates(chatid)

      
      for text in trainfile_array:
        audiodb.update_is_correct_by_word(text, chatid, 1, False)
      

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def clean_duplicates(chatid: str):
  try:
    
    dbfile = chatid + "-db"
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    statements = chatbotdb["statements"]

    statements.aggregate(
      [ 
          { "$sort": { "_id": 1 } }, 
          { "$group": { 
              "_id": "$text", 
              "doc": { "$first": "$$ROOT" } 
          }}, 
          { "$replaceRoot": { "newRoot": "$doc" } },
          { "$out": "collection" }
      ]

    )
    logging.info("clean_duplicates - Done!")

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return("Errore!")

def delete_by_text(chatid: str, text: str, force = False):
  try:
    filename = os.path.dirname(os.path.realpath(__file__)) + get_slashes() + 'config' + get_slashes() + chatid + '-db.txt'
    if extract_sentences_from_chatbot(filename, chatid=chatid):
      backupdb(chatid, "txt")
    
    
    dbfile = chatid + "-db"
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    statements = chatbotdb["statements"]

    rgx = re.compile('.*' + text + '.*', re.IGNORECASE)  # compile the regex
    statements.delete_many({'text':rgx})

    rgx_2 = re.compile('.*' + text + '.*', re.IGNORECASE)  # compile the regex
    statements.delete_many({'in_response_to':rgx_2})

    logging.info("delete_by_text - Deleting: %s", text)

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return("Errore!")
  if force:
    #delete_from_audiodb_by_text(chatid, text)
    audiodb.update_is_correct_by_word(text, chatid, 0, True)
    return('Frasi con parola chiave "' + text + '" cancellate dal db chatbot e dal db audio!')
  else:
    return('Frasi con parola chiave "' + text + '" cancellate dal db chatbot!')

def save_mp3(mp3, name):
  filesave = None
  try:
    sound = AudioSegment.from_mp3(mp3)
    sound.export(name, format='mp3', bitrate="256k")
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
  return filesave

def get_tts(text: str, chatid="000000", voice=None, israndom=False, language="it", save=True, call_fy=True, limit=True, user=None):
  try:
    if voice is None or voice == "null" or voice == "random":
      voice_to_use = get_random_voice(lang=language)
    else:
      voice_to_use = voice
    if voice_to_use != "google" and voice_to_use != "aws":
      datafy = audiodb.select_by_name_chatid_voice_language(text.strip(), chatid, voice_to_use, language)
      if datafy is not None:
        return datafy
      elif call_fy:
        wav=None
        for x in range(6):
          try:
            fy.login(FAKEYOU_USER,FAKEYOU_PASS)
            wav = fy.say(text.strip(), voice_to_use)
          except:
            logging.error("get_tts - FAKEYOU ERROR \n         CHATID: %s\n         VOICE: %s\n         SENTENCE: %s\n         SLEEPING 120 SECONDS, COUNTER IS AT: %s", chatid, voice_to_use, text, str(x))
            time.sleep(120)
        if wav is not None:
          sound = AudioSegment.from_wav(BytesIO(bytes(wav.content)))
          out = BytesIO()
          sound.export(out, format='mp3', bitrate="256k")
          out.seek(0)
          if save:
            audiodb.insert_or_update(text.strip(), chatid, None, voice_to_use, language, is_correct=1, user=user)
            #threading.Thread(target=lambda: thread_save_fakeyou(text, sound, voice_to_use, chatid=chatid, language=language, user=user)).start()
          return out
        elif voice == "random" or voice == "google":
          return get_tts_google(text.strip(), chatid=chatid, language="it", save=save, limit=limit, user=user)
        elif voice == "aws":
          return get_tts_aws(text.strip(), chatid=chatid, language="it", save=save, limit=limit, user=user)
        else:
          return None
      else:
        return get_tts_google(text.strip(), chatid=chatid, language="it", save=save, limit=limit, user=user)
    elif voice == "aws":
      return get_tts_aws(text.strip(), chatid=chatid, language="it", save=save, limit=limit, user=user)
    else:
      return get_tts_google(text.strip(), chatid=chatid, language=language, save=save, limit=limit, user=user)
  except AudioLimitException as el:
    raise(el)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    if voice == "random" or israndom:
      return get_tts_google(text.strip(), chatid=chatid, language=language, save=save, limit=limit, user=user)
    else:
      audiodb.insert_or_update(text.strip(), chatid, None, voice_to_use, language, is_correct=1, user=user)
      raise Exception(e)

def thread_save_fakeyou(text: str, sound, voice_to_use, chatid="000000", language="it", user=None): 
  duration = (len(sound) / 1000.0)
  hashtext = hashlib.md5((text+"_"+voice_to_use).encode('utf-8')).hexdigest()
  dirsave = "." + get_slashes() + 'audios'
  if not os.path.exists(dirsave):
    os.makedirs(dirsave)
  filesave = dirsave + get_slashes() + hashtext + ".mp3"
  sound.export(filesave, format='mp3', bitrate="256k")
  audiodb.insert_or_update(text.strip(), chatid, filesave, voice_to_use, language, duration=duration, user=user)

@run_with_timer(max_execution_time=300)
def populate_tts(text: str, chatid="000000", voice=None, israndom=False, language="it"):
  try:  
    if voice is None or voice == "null" or voice == "random":
      voice_to_use = get_random_voice(lang=language)
    else:
      voice_to_use = voice
    if voice_to_use != "google" and voice_to_use != "aws": 
      datafy = audiodb.select_by_name_chatid_voice_language(text.strip(), chatid, voice_to_use, language)
      if datafy is not None:
        return False
      else:
        #if bool(random.getrandbits(1)):
        #  proxies = {'http': 'http://192.168.1.160:9058'}
        #  fy.session.proxies.update(proxies)
        #else:
        #  proxies = {}
        #  fy.session.proxies.update(proxies)
        fy.login(FAKEYOU_USER,FAKEYOU_PASS)
        wav = fy.say(text.strip(), voice_to_use)
        if wav is not None:
          sound = AudioSegment.from_wav(BytesIO(bytes(wav.content)))
          duration = (len(sound) / 1000.0)
          if duration > int(os.environ.get("MAX_TTS_DURATION")):
            audiodb.insert_or_update(text.strip(), chatid, None, voice_to_use, language, is_correct=0, duration=duration)
            return None
          else:
            #sound.duration_seconds == duration
            hashtext = hashlib.md5((text+"_"+voice_to_use).encode('utf-8')).hexdigest()
            dirsave = "." + get_slashes() + 'audios'
            if not os.path.exists(dirsave):
              os.makedirs(dirsave)
            filesave = dirsave + get_slashes() + hashtext + ".mp3"
            sound.export(filesave, format='mp3', bitrate="256k")
            audiodb.insert_or_update(text.strip(), chatid, filesave, voice_to_use, language, duration=duration)
            return True
        raise Exception("FakeYou Generation KO")
    elif voice == "aws":
      return populate_tts_aws(text.strip(), chatid=chatid, language=language)
    else:
      return populate_tts_google(text.strip(), chatid=chatid, language=language)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno)
    raise Exception(e)

def get_random_voice(lang="it"):
  localvoices = list_fakeyou_voices(lang)
  title, token = random.choice(list(localvoices.items()))
  return token

@lru_cache(maxsize=128)
def list_fakeyou_voices(lang:str):
  foundvoices = None
  try:

    file_path = "./config/voices_"+lang+".json"
    
    #if bool(random.getrandbits(1)):
    #  proxies = {'http': 'http://192.168.1.160:9058'}
    #  fy.session.proxies.update(proxies)
    #else:
    #  proxies = {}
    #  fy.session.proxies.update(proxies)
    
    voices = None
    try:
      fy.login(FAKEYOU_USER,FAKEYOU_PASS)
      voices=fy.list_voices(size=0)
    except Exception as e:
      pass
      
    if voices is not None:
      foundvoices = {}


      inclusion_file_path = "./config/voices_inclusions_"+lang+".json"

      if os.path.exists(inclusion_file_path):
        with open(inclusion_file_path) as inclusion_file:
          inclusion_file_content = inclusion_file.read()
          inclusion_file_content_parsed = json.loads(inclusion_file_content)
          for langTag,voiceJson in zip(voices.langTag,voices.json):
            if lang.lower() in langTag.lower():
              skip = True
              for inclusion in inclusion_file_content_parsed:
                if inclusion == voiceJson["title"]:
                  skip = False
                  break
              if not skip:
                foundvoices[voiceJson["title"]] = voiceJson["model_token"]
      else:
        for langTag,voiceJson in zip(voices.langTag,voices.json):
          if lang.lower() in langTag.lower():
            foundvoices[voiceJson["title"]] = voiceJson["model_token"]


      
      foundvoices["google"] = "google"
      foundvoices["Giorgio"] = "aws"
      
      with open(file_path, "w") as write_file:
        json_string = json.dumps(foundvoices, ensure_ascii=False, indent=4).encode('utf-8').decode('utf-8')
        write_file.write(json_string)

    elif os.path.isfile(file_path):

      with open(file_path) as f:
        data = f.read()

      foundvoices = json.loads(data)

    else:
      
      foundvoices = {}
      foundvoices["google"] = "google"
      foundvoices["Giorgio"] = "aws"

    return foundvoices
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    list_fakeyou_voices.cache_clear()
    raise Exception(e)

def get_random_from_bot(chatid: str, text: str):
  try:
    dbfile = chatid + "-db"
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    statements = chatbotdb["statements"]

    sentence = None

    if text is not None:
      rgx = re.compile('.*' + text + '.*', re.IGNORECASE)  # compile the regex
      cursor = statements.find({"text": rgx})
      textlist = list(cursor)
      sizel = len(textlist)
      if sizel > 0:
        random_index = int(random.random() * sizel)
        sentence = textlist[random_index]['text']
    else:
      cursor = statements.aggregate([
        {
          "$sample": {
            "size": 1
          }
        }
      ])
      for row in cursor:    
        sentence = row['text']

    return sentence
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    raise Exception(e)
    

def populate_audiodb_unlimited(limit: int, chatid: str, lang: str):  
  populate_audiodb_internal(limit, chatid, lang)
  delete_tts(limit=limit)

def populate_audiodb_limited(limit: int, chatid: str, lang: str):  
  try:
    populate_audiodb(limit, chatid, lang)
  except TimeExceededException as et:
    logging.debug("populate_audiodb - ENDED POPULATION\n         REACHED UP MAX EXECUTION TIME\n         CHATID: %s\n         LIMIT: %s", chatid, str(limit))
  finally:
    delete_tts(limit=limit)

@run_with_timer(max_execution_time=600)
def populate_audiodb(limit: int, chatid: str, lang: str):  
  populate_audiodb_internal(limit, chatid, lang)

def populate_audiodb_internal(limit: int, chatid: str, lang: str):  

  try:
    logging.debug("populate_audiodb - STARTED POPULATION\n         CHATID: %s\n         LIMIT: %s", chatid, str(limit))

    voices = list_fakeyou_voices(lang)
    listvoices = list(voices.items())
    #random.shuffle(listvoices)

    process_population(limit, chatid, lang, listvoices)    
    
    logging.debug("populate_audiodb - ENDED POPULATION\n         CHATID: %s\n         LIMIT: %s", chatid, str(limit))
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    logging.error("populate_audiodb - ENDED POPULATION WITH ERROR\n         CHATID: %s\n         LIMIT: %s", chatid, str(limit))
    raise Exception(e)

def process_population(limit, chatid, lang, listvoices):

  
  result = False

  counter_inserted = 0
  counter_skipped_failed = 0
  while counter_inserted < limit or counter_skipped_failed < (limit*10):
    try:
      key, voice = random.choice(listvoices)
      sentence = ""
      dbfile = chatid + "-db"
      myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
      chatbotdb = myclient[dbfile]
      statement = chatbotdb["statements"]     
      cursor = statement.aggregate(
          [ { "$sample": { "size" : 1 } } ]
      )
      for row in cursor:
        sentence = row['text']
      if sentence == "":
        logging.debug("populate_audiodb - NO RECORDS FOUND!\n         CHATID: %s\n         LIMIT: %s", chatid, str(limit))
        break

      language = audiodb.select_distinct_language_by_name_chatid(sentence, chatid)
      if language is None:
        language = lang
      inserted = ""

      counter = audiodb.select_count_by_name_chatid_voice_language(sentence, chatid, voice, language)
      
      if counter >= int(os.environ.get("COUNTER_LIMIT")):
          inserted="Skipped (Counter Limit)"
          logging.debug("populate_audiodb - SKIPPED  \n         CHATID: %s\n         VOICE: %s (%s)\n         SENTENCE: %s\n         RESULT: %s", chatid, voice, key, sentence, inserted)
      else:
        result = populate_tts(sentence, chatid=chatid, voice=voice, language=language)
        if result is None:
          inserted="Skipped (TTS lenght limit exceeded)"
          counter_skipped_failed = counter_skipped_failed + 1
          logging.warning("populate_audiodb - SUCCESS ELAB  \n         CHATID: %s\n         VOICE: %s (%s)\n         SENTENCE: %s\n         RESULT: %s", chatid, voice, key, sentence, inserted)
          time.sleep(randint(5,120))
        elif result is True:
          inserted="Done (Inserted in DB)"
          counter_inserted = counter_inserted + 1
          logging.debug("populate_audiodb - SUCCESS ELAB  \n         CHATID: %s\n         VOICE: %s (%s)\n         SENTENCE: %s\n         RESULT: %s", chatid, voice, key, sentence, inserted)
          time.sleep(randint(5,120))
        elif result is False:
          counter_skipped_failed = counter_skipped_failed + 1
          inserted="Skipped (Already in DB)"
          logging.debug("populate_audiodb - SUCCESS ELAB  \n         CHATID: %s\n         VOICE: %s (%s)\n         SENTENCE: %s\n         RESULT: %s", chatid, voice, key, sentence, inserted)
    except Exception as e:
      counter = audiodb.select_count_by_name_chatid_voice_language(sentence, chatid, voice, language)
      if counter > 0:
        audiodb.increment_counter(sentence, chatid, voice, language, int(os.environ.get("COUNTER_LIMIT")))
      else:
        audiodb.insert(sentence, chatid, None, voice, language, is_correct=1)
      inserted="Failed (" + str(e) + ")"
      logging.error("populate_audiodb - ERROR ELAB\n         CHATID: %s\n         VOICE: %s (%s)\n         SENTENCE: %s\n         RESULT: %s", chatid, voice, key, sentence, inserted)
      counter_skipped_failed = counter_skipped_failed + 1
      time.sleep(randint(5,120))



def backupdb(chatid: str, extension: str):  
  try:
    dbfile=os.path.dirname(os.path.realpath(__file__)) + get_slashes() + "config" + get_slashes() + chatid + "-db." + extension
    dst=os.path.dirname(os.path.realpath(__file__)) + get_slashes() + "backups" + get_slashes() + chatid + "-db_backup_" + str(time.time()) + "." + extension
    shutil.copyfile(dbfile, dst)

    current_time = time.time()

    bakdir = "backups"
    N = 30
    os.chdir(os.path.join(os.getcwd(), bakdir)) 
    list_of_files = os.listdir() 
    current_time = time.time() 
    day = 86400
    for i in list_of_files: 
      file_location = os.path.join(os.getcwd(), i) 
      file_time = os.stat(file_location).st_mtime 
      if(file_time < current_time - day*N): 
        os.remove(file_location) 
    
    os.chdir("../")      
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    raise Exception(e)

def init_generator_models(chatid, language):

  logging.info("START -- essential_generators - [chatid:" + chatid + ",lang:" + language + "] - Models Generator")

  dir_path = os.path.dirname(os.path.realpath(__file__))

  filename = dir_path + '/config/sentences_'+chatid+'.txt'
  
  if audiodb.extract_sentences_from_audiodb(filename, language=language, chatid=chatid):

    text_model_path = dir_path + '/config/markov_textgen_'+chatid+'.json'
    word_model_path = dir_path + '/config/markov_wordgen_'+chatid+'.json'

    init_text_generator(corpus=filename, output=text_model_path)
    init_word_generator(corpus=filename, output=word_model_path)

    logging.info("END -- essential_generators - [chatid:" + chatid + ",lang:" + language + "] - Models Generator")

def init_text_generator(corpus=None, output=None):

    with open(corpus, 'r', encoding='utf-8') as fp:
      set4 = fp.read()

    gen = MarkovTextGenerator(load_model=False)
    gen.train(set4)
    gen.save_model(output)

def init_word_generator(corpus=None, output=None):

    with open(corpus, 'r', encoding='utf-8') as fp:
      set4 = fp.read()

    gen = MarkovWordGenerator(load_model=False)
    gen.train(set4)
    gen.save_model(output)

def generate_sentence(chatid: str):

  dir_path = os.path.dirname(os.path.realpath(__file__))

  text_model_path = dir_path + '/config/markov_textgen_'+chatid+'.json'
  word_model_path = dir_path + '/config/markov_wordgen_'+chatid+'.json'

  text_generator=MarkovTextGenerator(model=text_model_path, load_model=True)
  word_generator=MarkovWordGenerator(model=word_model_path, load_model=True)

  generator = DocumentGenerator(word_generator=word_generator, text_generator=text_generator)

  return generator.sentence()

def generate_paragraph(chatid: str):

  dir_path = os.path.dirname(os.path.realpath(__file__))

  text_model_path = dir_path + '/config/markov_textgen_'+chatid+'.json'
  word_model_path = dir_path + '/config/markov_wordgen_'+chatid+'.json'

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

def rmdir(directory):
  directory = Path(directory)
  for item in directory.iterdir():
      if item.is_dir():
          rmdir(item)
      else:
          item.unlink()
  directory.rmdir()


def reset(chatid: str):
  try:
    dbfile = chatid + "-db"
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    statement = chatbotdb["statements"]     

    statement.delete_many()

    logging.info("reset - Executing delete by chatid: %s", chatid)

    audiodb.delete_by_chatid(chatid)    

    folder = "." + get_slashes() + 'audios' + get_slashes()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)


def login_google():
  try:
    email = os.environ.get("BARD_USER")
    password = os.environ.get("BARD_PASS")
    
    chrome_options = ChromeOptions() 
    chrome_options.add_argument("--disable-setuid-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-using") 
    chrome_options.add_argument("--disable-extensions") 
    chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % "640,480")

    driver = Chrome(use_subprocess=True, options=chrome_options)
    driver.get("https://accounts.google.com/ServiceLogin")
    time.sleep(10)
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'identifier'))).send_keys(f'{email}\n')
    time.sleep(10)
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'Passwd'))).send_keys(f'{password}\n')
   
    driver.get("https://bard.google.com/")
    cookies = driver.get_cookies()

    for cookie in cookies:
      if cookie["name"] == "__Secure-1PSID":
        os.environ["__Secure-1PSID"] = cookie["value"]
        dotenv.set_key(dotenv_path, "__Secure-1PSID", cookie["value"])
      elif cookie["name"] == "__Secure-1PSIDTS":
        os.environ["__Secure-1PSIDTS"] = cookie["value"]
        dotenv.set_key(dotenv_path, "__Secure-1PSIDTS", cookie["value"])
      elif cookie["name"] == "__Secure-1PSIDCC":
        os.environ["__Secure-1PSIDCC"] = cookie["value"]
        dotenv.set_key(dotenv_path, "__Secure-1PSIDCC", cookie["value"])
    driver.close()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)



def delete_tts(limit=100):
  try:
    fy.login(FAKEYOU_USER,FAKEYOU_PASS)
    user = fy.get_user(FAKEYOU_USER,limit=limit)
    if user is not None and user.ttsResults is not None and user.ttsResults.json is not None:
      for tokenJson in user.ttsResults.json:
        token = tokenJson['tts_result_token']
        result = fy.delete_tts_result(token)
        if result:
          logging.info("delete_tts - DELETED: %s", token)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def get_mp3(file):
  if os.path.isfile(file):      
    sound = AudioSegment.from_mp3(file)
    memoryBuff = BytesIO()
    sound.export(memoryBuff, format='mp3', bitrate="256k")
    memoryBuff.seek(0)
    return memoryBuff
  else:
    return None

def get_slashes():
  if os.name == "nt": 
    return "\\"
  else:
    return "/"
