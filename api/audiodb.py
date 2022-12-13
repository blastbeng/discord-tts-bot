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
            UNIQUE(name,chatid,voice)
        ); """

    cursor.execute(sqlite_create_audio_query)

  except sqlite3.Error as error:
    logging.error("Failed to create tables: %s %s %s", exc_info=1)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def insert(name: str, chatid: str, data: BytesIO, voice: str):
  try:
    sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_insert_audio_query = """INSERT INTO Audio
                          (name, chatid, data, voice) 
                           VALUES 
                          (?, ?, ?, ?)"""

    data_audio_tuple = (name, 
                        chatid, 
                        data.read(),
                        voice)

    cursor.execute(sqlite_insert_audio_query, data_audio_tuple)


    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    logging.error("Failed to insert data into sqlite", exc_info=1)
  finally:
    if sqliteConnection:
        sqliteConnection.close()


def select(name: str, chatid: str, voice: str):
  if chatid == "X":
    return None
  else:
    audio = None
    try:
      sqliteConnection = sqlite3.connect("./config/audiodb.sqlite3")
      cursor = sqliteConnection.cursor()

      sqlite_select_query = """SELECT data from Audio WHERE name = ? AND chatid = ? AND voice = ? """
      cursor.execute(sqlite_select_query, (name, chatid, voice))
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