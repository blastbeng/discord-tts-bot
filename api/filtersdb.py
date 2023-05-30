import os
import sqlite3
import logging

from dotenv import load_dotenv
from os.path import dirname
from os.path import join
from pathlib import Path

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
  fle = Path("./config/filters.sqlite3")
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def create_empty_tables():
  check_db_exists()
  try:
    sqliteConnection = sqlite3.connect("./config/filters.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_create_query = """ CREATE TABLE IF NOT EXISTS WordFilters(
            id INTEGER PRIMARY KEY,
            chatid VARCHAR(50) NOT NULL,
            word VARCHAR(500) NOT NULL,
            tms_insert DATETIME DEFAULT CURRENT_TIMESTAMP,
            tms_update DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(word,chatid)
        ); """

    cursor.execute(sqlite_create_query)

  except sqlite3.Error as error:
    logging.error("Failed to create tables: %s %s %s", exc_info=1)
  finally:
    if sqliteConnection:
        sqliteConnection.close()


def insert(chatid: str, word: str):
  try:
    sqliteConnection = sqlite3.connect("./config/filters.sqlite3")
    cursor = sqliteConnection.cursor()

    sqlite_insert_query = """INSERT INTO WordFilters
                          (chatid, word)  
                          SELECT ?, ? 
                          WHERE NOT EXISTS(SELECT 1 FROM WordFilters WHERE chatid = ? AND word = ?)"""

    data_tuple = (chatid, word.lower(), chatid, word.lower(),)

    cursor.execute(sqlite_insert_query, data_tuple)


    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    logging.error("Failed to Execute SQLITE Query", exc_info=1)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def is_blocked(chatid: str, word: str):
  blocked = False
  try:
    sqliteConnection = sqlite3.connect("./config/filters.sqlite3")
    cursor = sqliteConnection.cursor()
    sqlite_select_query = "SELECT DISTINCT word FROM WordFilters WHERE chatid = ? AND word = ?"
    cursor.execute(sqlite_select_query, (chatid,word.lower(),))
    records = cursor.fetchall()

    for row in records:
        blocked = True
        break
    cursor.close()
  except sqlite3.Error as error:
    logging.error("Failed to Execute SQLITE Query", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return blocked

def select_all(chatid: str):
  words = []
  try:
    sqliteConnection = sqlite3.connect("./config/filters.sqlite3")
    cursor = sqliteConnection.cursor()
    sqlite_select_query = "SELECT DISTINCT word FROM WordFilters WHERE chatid = ?"
    cursor.execute(sqlite_select_query, (chatid,))
    records = cursor.fetchall()

    for row in records:
        words.append(row[0])
    cursor.close()

  except sqlite3.Error as error:
    logging.error("Failed to Execute SQLITE Query", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return words

def delete(chatid: str, word: str):
  blocked = False
  try:
    sqliteConnection = sqlite3.connect("./config/filters.sqlite3")
    cursor = sqliteConnection.cursor()
    sqlite_select_query = " DELETE FROM WordFilters WHERE chatid = ? AND word = ?"
    cursor.execute(sqlite_select_query, (chatid,word.lower(),))
    
    sqliteConnection.commit()
    cursor.close()
  except sqlite3.Error as error:
    logging.error("Failed to Execute SQLITE Query", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return blocked

def delete_all(chatid: str):
  blocked = False
  try:
    sqliteConnection = sqlite3.connect("./config/filters.sqlite3")
    cursor = sqliteConnection.cursor()
    sqlite_select_query = " DELETE FROM WordFilters WHERE chatid = ?"
    cursor.execute(sqlite_select_query, (chatid,))
    
    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    logging.error("Failed to Execute SQLITE Query", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return blocked

def vacuum():
  try:
    sqliteConnection = sqlite3.connect("./config/filters.sqlite3")
    cursor = sqliteConnection.cursor()

    cursor.execute("VACUUM")

    cursor.close()
  except sqlite3.Error as error:
    logging.error("Failed to Execute VACUUM", exc_info=1)
  finally:
    if sqliteConnection:
      sqliteConnection.close()