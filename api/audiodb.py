import os
import sqlite3
import logging

from io import BytesIO
from dotenv import load_dotenv
from os.path import dirname
from os.path import join
from pathlib import Path
from datetime import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))

GUILD_ID = os.environ.get("GUILD_ID")

def check_db_exists(): 
  fle = Path("./config/audiodb.sqlite3")
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def create_empty_tables():
  check_db_exists()
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_create_audio_query = """ CREATE TABLE IF NOT EXISTS Audio(
            id INTEGER PRIMARY KEY,
            name VARCHAR(500) NOT NULL,
            chatid VARCHAR(50) NOT NULL,
            data BLOB NOT NULL,
            voice VARCHAR(50) NOT NULL,
            is_correct INTEGER DEFAULT 0 NOT NULL,
            language VARCHAR(2) NOT NULL,
            UNIQUE(name,chatid,voice)
        ); """

    cursor.execute(sqlite_create_audio_query)

  except sqlite3.Error as error:
    logging.error("Failed to create tables: %s %s %s", exc_info=1)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def insert(name: str, chatid: str, data: BytesIO, voice: str, language: str, is_correct=1):
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_insert_audio_query = """INSERT INTO Audio
                          (name, chatid, data, voice, is_correct, language) 
                           VALUES 
                          (?, ?, ?, ?, ?, ?)"""

    data_audio_tuple = (name, 
                        chatid, 
                        data.read(),
                        voice,
                        is_correct,
                        language)

    cursor.execute(sqlite_insert_audio_query, data_audio_tuple)


    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    logging.error("Failed to insert data into sqlite", exc_info=1)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def update_is_correct(name: str, chatid: str, data: BytesIO, voice: str, language: str, is_correct=1):
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_insert_audio_query = """UPDATE Audio
                          SET is_correct = ? 
                           WHERE 
                          name = ? and chatid = ? and voice = ? and language = ? """

    data_audio_tuple = (is_correct,
                        name, 
                        chatid, 
                        data.read(),
                        voice,
                        language)

    cursor.execute(sqlite_insert_audio_query, data_audio_tuple)


    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    logging.error("Failed to update data into sqlite", exc_info=1)
  finally:
    if sqliteConnection:
        sqliteConnection.close()


def select_list_by_chatid(chatid=GUILD_ID):
  records = None
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()
    sqlite_select_query = " SELECT DISTINCT * from Audio WHERE chatid = ? AND is_correct = 1 ORDER BY name, voice"
    cursor.execute(sqlite_select_query, (chatid,))
    records = cursor.fetchall()

  except sqlite3.Error as error:
    logging.error("Failed to read data from sqlite table", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return records

def select_by_chatid(chatid=GUILD_ID):
  records = None
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()
    sqlite_select_query = " SELECT DISTINCT * from Audio WHERE chatid = ?"
    cursor.execute(sqlite_select_query, (chatid,))
    records = cursor.fetchall()

  except sqlite3.Error as error:
    logging.error("Failed to read data from sqlite table", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return records

def select_data_name_voice_by_chatid(chatid: str):
  records = None
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()
    sqlite_select_query = " SELECT DISTINCT data, name, voice from Audio WHERE chatid = ? AND is_correct = 1 "
    cursor.execute(sqlite_select_query, (chatid,))
    records = cursor.fetchall()

  except sqlite3.Error as error:
    logging.error("Failed to read data from sqlite table", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return records

def select_by_name_chatid_voice_language(name: str, chatid: str, voice: str, language: str):
  if chatid == "X":
    return None
  else:
    audio = None
    try:
      sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
      cursor = sqliteConnection.cursor()

      sqlite_select_query = """SELECT data from Audio WHERE name = ? AND chatid = ? AND voice = ? AND language = ? AND is_correct = 1 """
      cursor.execute(sqlite_select_query, (name, chatid, voice, language,))
      records = cursor.fetchall()

      for row in records:
        data   =  row[0]
        cursor.close()
        audio = BytesIO(data)
        audio.seek(0)

    except sqlite3.Error as error:
      logging.error("Failed to read data from sqlite table", exc_info=1)
    finally:
      if sqliteConnection:
        sqliteConnection.close()
    return audio

def select_by_chatid_voice_random(chatid: str, voice:str):
  if chatid == "X":
    return None
  else:
    audio = None
    name = None
    try:
      sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
      cursor = sqliteConnection.cursor()

      sqlite_select_query=""
      params=None

      if voice == "random":
        sqlite_select_query = """SELECT data, name from Audio WHERE chatid = ?  AND is_correct = 1 ORDER BY RANDOM() LIMIT 1; """
        params=(chatid,)
      else:
        sqlite_select_query = """SELECT data, name from Audio WHERE chatid = ? and voice = ?  AND is_correct = 1 ORDER BY RANDOM() LIMIT 1; """
        params=(chatid,voice,)

      cursor.execute(sqlite_select_query, params)
      records = cursor.fetchall()

      for row in records:
        data   =  row[0]
        cursor.close()
        audio = BytesIO(data)
        audio.seek(0)
        name = row[1]

    except sqlite3.Error as error:
      logging.error("Failed to read data from sqlite table", exc_info=1)
    finally:
      if sqliteConnection:
        sqliteConnection.close()
    return audio, name

def select_audio_by_id(id: int):
  audio = None
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_select_query = """SELECT data from Audio WHERE id = ? """
    cursor.execute(sqlite_select_query, (id,))
    records = cursor.fetchall()

    for row in records:
      data   =  row[0]
      cursor.close()
      audio = BytesIO(data)
      audio.seek(0)

  except sqlite3.Error as error:
    logging.error("Failed to read data from sqlite table", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  if audio is None:
    raise Exception("Audio not found")
  else:
    return audio

def select_count_by_text_chatid_voice(text: str, chatid: str, voice: str):
  count = 0
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_select_query = """SELECT count(id) from Audio WHERE name = ? and chatid = ? and voice = ?"""
    cursor.execute(sqlite_select_query, (text, chatid, voice,))
    records = cursor.fetchall()

    for row in records:
      count = count + 1
  except sqlite3.Error as error:
    logging.error("Failed to read data from sqlite table", exc_info=1)
    return count
  finally:
    if sqliteConnection:
      sqliteConnection.close()
    return count



def delete_by_name(name: str, chatid: str):
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_delete_query = """DELETE from Audio 
                          WHERE chatid = ?
                          AND (name like ?
                          OR name like ?
                          OR name = ?)"""


    data_tuple = (chatid,
                  name+'%', 
                  '%'+name, 
                  name) 
    cursor.execute(sqlite_delete_query, data_tuple)

    sqliteConnection.commit()
    cursor.close()

  except Exception as e:
    logging.error("Failed to read data from sqlite table", exc_info=1)
    raise Exception(e)
  finally:
    if sqliteConnection:
      sqliteConnection.close()