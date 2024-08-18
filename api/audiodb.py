import os
import random
import pymongo
import datetime
import logging
import sys
import re
import requests

from io import BytesIO
from dotenv import load_dotenv
from os.path import dirname
from os.path import join
from pathlib import Path
from exceptions import AudioLimitException
from pydub import AudioSegment
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))

GUILD_ID = os.environ.get("GUILD_ID") 


#sqlite_create_audio_query = """ CREATE TABLE IF NOT EXISTS Audio(
#            id INTEGER PRIMARY KEY,
#            name VARCHAR(500) NOT NULL,
#            chatid VARCHAR(50) NOT NULL,
#            data BLOB NULL,
#            voice VARCHAR(50) NOT NULL,
#            is_correct INTEGER DEFAULT 1 NOT NULL,
#            language VARCHAR(2) NOT NULL,
#            counter INTEGER DEFAULT 1 NOT NULL,
#            duration INTEGER DEFAULT 0 NOT NULL,
#            user VARCHAR(500) NULL,
#            tms_insert DATETIME DEFAULT CURRENT_TIMESTAMP,
#            tms_update DATETIME DEFAULT CURRENT_TIMESTAMP,
#            UNIQUE(name,chatid,voice,language)
#        ); """

def insert(name: str, chatid: str, filesave, voice: str, language: str, is_correct=1, duration=0):
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]

    record = { "name": name, 
               "chatid": chatid, 
               "file": filesave,
               "voice": voice,
               "is_correct": is_correct,
               "language": language,
               "counter": 0,
               "duration": duration,
               "user": None,
               "tms_insert": datetime.datetime.now(),
               "tms_update": datetime.datetime.now() }
    
    audiotable.insert_one(record)

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)



def select_count_by_name_chatid_voice_language(name: str, chatid: str, voice: str, language: str):
  count = 0
  try:
    
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]


    count = len(list(audiotable.find({
                        "chatid": chatid,
                        "voice": voice,
                        "name": name,
                        "language": language                        
                      })))

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
  return count
  

def insert_or_update(name: str, chatid: str, filesave: str, voice: str, language: str, is_correct=1, duration=0, user=None):
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]

    count = select_count_by_name_chatid_voice_language(name, chatid, voice, language)

    if count > 0:

      query = { "chatid": chatid,
                "voice": voice,
                "name": name,
                "language": language
              }

      record = { "$set": {"name": name, 
                          "chatid": chatid, 
                          "file": filesave,
                          "voice": voice,
                          "is_correct": is_correct,
                          "language": language,
                          "counter": 0,
                          "duration": duration,
                          "user": user,
                          "tms_update": datetime.datetime.now() }
                  }
      audiotable.update_one(query, record)
      logging.debug("Audiodb - Updating: %s -> %s", str(query), str(record))

    else:

      record = {"name": name, 
                "chatid": chatid, 
                "file": filesave,
                "voice": voice,
                "is_correct": is_correct,
                "language": language,
                "counter": 0,
                "duration": duration,
                "user": user,
                "tms_insert": datetime.datetime.now(),
                "tms_update": datetime.datetime.now() }
      
      audiotable.insert_one(record)
      logging.debug("Audiodb - Inserting: %s",str(record))

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)



def select_by_name_chatid_voice_language(name: str, chatid: str, voice: str, language: str):
  memoryBuff = None
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]
    
    query = { "chatid": chatid,
              "voice": voice,
              "name": name,
              "language": language,
              "is_correct": 1,
              "file": {
                "$nin": [None, ""]
              }
            }

    records = audiotable.find(query)

    for row in records:
      duration = row["duration"]
      if duration > int(os.environ.get("MAX_TTS_DURATION")):
        raise AudioLimitException
      file = row["file"]
      if os.path.isfile(file):
        memoryBuff = file
      else:
        delquery = { "_id": row["_id"] }
        audiotable.delete_one(delquery)


  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

  return memoryBuff

def update_is_correct(name: str, chatid: str, voice: str, language: str, is_correct=1):
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]   

    query = { "chatid": chatid,
              "voice": voice,
              "name": name,
              "language": language
            }

    record = { "$set": {"is_correct": is_correct } }

    audiotable.update_one(query, record)
              
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)



def update_is_correct_by_word(text: str, chatid: str, is_correct: int, use_like: bool):
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]   

    logging.info('Updating word is_correct to %s for text: "%s"', str(is_correct), text)

    if use_like: 


      rgx = re.compile('.*' + text + '.*', re.IGNORECASE)  # compile the regex
      
      query = { "chatid": chatid,
                "name": rgx,
                "file": {
                  "$nin": [None, ""]
                },
                "duration": {"$lt": int(os.environ.get("MAX_TTS_DURATION"))}
              }

      record = { "$set": {"is_correct": is_correct } }

      audiotable.update_one(query, record)

    else: 

      
      query = { "chatid": chatid,
                "name": text,
                "file": {
                  "$nin": [None, ""]
                },
                "duration": {"$lt": int(os.environ.get("MAX_TTS_DURATION"))}
              }

      record = { "$set": {"is_correct": is_correct } }

      audiotable.update_one(query, record)

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def update_is_correct_if_not_none(chatid: str, is_correct: int):
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]  

    query = { "chatid": chatid,
              "file": {
                "$nin": [None, ""]
              },
              "duration": {"$lt": int(os.environ.get("MAX_TTS_DURATION"))}
            }

    record = { "$set": {"is_correct": is_correct } }

    audiotable.update_one(query, record)


  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def increment_counter(name: str, chatid: str, voice: str, language: str, counter_limit: int):
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]   

    counter = select_counter_by_name_chatid_voice_language(name, chatid, voice, language)
    
    query = { "chatid": chatid,
              "name": name,
              "voice": voice,
              "language": language,
              "is_correct": 1 if counter < counter_limit else 0
            }

    record = { "$set": {"counter": counter + 1,
                        "tms_update": datetime.datetime.now() } 
                        }

    audiotable.update_one(query, record)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def select_counter_by_name_chatid_voice_language(name: str, chatid: str, voice: str, language: str):
  counter = 0
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]   

    records = audiotable.find({
                        "chatid": chatid,
                        "voice": voice,
                        "name": name,
                        "language": language                        
                      })


    for row in records:
      counter = row['counter']

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
  return counter

def select_voice_by_name_chatid_language(name: str, chatid: str, language: str):
  voice = None
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]   
    voice = None
    
    records = audiotable.find({
                        "chatid": chatid,
                        "name": name,
                        "language": language                        
                      })


    for row in records:
      voice = row['voice']

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
  return voice



def select_distinct_language_by_name_chatid(name: str, chatid: str):
  lang = None
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]   
    
    records = audiotable.find({
                        "chatid": chatid,
                        "name": name                    
                      })


    for row in records:
      lang = row['language']

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
  return lang

def select_by_chatid_voice_language_random(chatid: str, voice:str, language:str, text:str):
  audio = None
  name = None
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]       
    
    params={
           "chatid": chatid,
           "language": language,
           "is_correct": 1,
           "counter": {"$gte": 0},   
           "file": {
             "$nin": [None, ""]
           }                
         }

    if voice != "random":
      params["voice"] = voice      

    if text is not None:
      rgx = re.compile('.*' + text + '.*', re.IGNORECASE)
      params["name"] = rgx

    
    records = audiotable.find(params)

    name = False
    recordlist = list(records)
    sizel = len(list(recordlist))

    if sizel > 0:
      random_index = int(random.random() * sizel)
      row = recordlist[random_index]
      duration = row['duration']
      if duration > int(os.environ.get("MAX_TTS_DURATION")):
        raise AudioLimitException
      name = row['name']
      file = row['file']      
      if os.path.isfile(file):
        audio = file
      else:
        delquery = { "_id": row["_id"] }
        audiotable.delete_one(delquery)


  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
  return audio, name


def extract_sentences_from_audiodb(filename, language="it", chatid="000000"):
  try:

    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]     
    
    params={
           "chatid": chatid,
           "language": language              
         }     

    records = audiotable.find(params)

    if os.path.exists(filename):
      os.remove(filename)

    with open(filename, 'w') as sentence_file:
      for row in records:
        logging.debug('extract_sentences_from_audiodb - [chatid:' + chatid + ',lang:' + language + '] - "' + row['name'] + '"')
        sentence_file.write(row['name'])
        sentence_file.write("\n")
        
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return False
  return True

def delete_by_chatid(chatid: str):
  try:
    dbfile = chatid + "-db"
    #myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_USER")+':'+os.environ.get("MONGO_PASS")+'@'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    myclient = pymongo.MongoClient('mongodb://'+os.environ.get("MONGO_HOST")+':'+os.environ.get("MONGO_PORT")+'/')
    chatbotdb = myclient[dbfile]
    audiotable = chatbotdb["audio"]    

    params = { "chatid": chatid }

    audiotable.delete_many(params)

    logging.info("delete_from_audiodb - Executing delete by chatid: %s", chatid)


  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)