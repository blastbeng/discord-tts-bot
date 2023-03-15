import os
import database
from translate import Translator

dbms = database.Database(database.SQLITE, dbname='client.sqlite3')
database.create_db_tables(dbms)

def translate(guildid: str, text: str):
  tolang=database.select_guildconfig(dbms, guildid, value = "en")
  fromlang='en'
  if tolang == fromlang:
    return text
  cached = database.select_translation(dbms, fromlang, tolang, text)
  if cached is not None:
    return cached
  else:
    translation = Translator(from_lang=fromlang, to_lang=tolang).translate(text)
    database.insert_translation(dbms, fromlang, tolang, text, translation)
    return translation

def insert_new_guild(guildid: str, language: str):
    database.insert_guildconfig(dbms, guildid, language)

def update_guild(guildid: str, language: str):
    database.update_guildconfig(dbms, guildid, language)

def get_guild_language(guildid: str):
    return database.select_guildconfig(dbms, guildid, value = "en")

def check_exists_guild(guildid: str):
    value = database.select_guildconfig(dbms, guildid, value = None)
    if value is None:
      database.insert_guildconfig(dbms, guildid, "en")
