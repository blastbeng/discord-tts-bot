import os
import sqlite3

from io import BytesIO
from os.path import dirname
from os.path import join
from pathlib import Path

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
    print(datetime.now() + " - ","Failed to create tables", error)
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
    print(datetime.now() + " - ","Failed to insert data into sqlite", error)
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
      print(datetime.now() + " - ","Failed to read data from sqlite table", error)
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
    print(datetime.now() + " - ","Failed to read data from sqlite table", e)
    raise Exception(e)
  finally:
    if sqliteConnection:
      sqliteConnection.close()