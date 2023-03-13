import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy import create_engine, insert, select, update, Table, Column, Integer, String, MetaData

SQLITE          = 'sqlite'
GUILDCONFIG     = 'guildconfig'
TRANSLATIONS    = 'translations'

class Database:
  DB_ENGINE = {
      SQLITE: 'sqlite:///config/{DB}'
  }

  # Main DB Connection Ref Obj
  db_engine = None
  def __init__(self, dbtype, username='', password='', dbname=''):
    dbtype = dbtype.lower()
    engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
    self.db_engine = create_engine(engine_url)

  metadata = MetaData()

  guildconfig = Table(GUILDCONFIG, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('guildid', String(50), nullable=False),
                Column('language', String(50), nullable=False)
                )

  translations = Table(TRANSLATIONS, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('from_lang', String(50), nullable=False),
                Column('dest_lang', String(50), nullable=False),
                Column('key', String(500), nullable=False),
                Column('value', String(500), nullable=False)
                )

def create_db_tables(self):
  try:
    self.metadata.create_all(self.db_engine)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def insert_guildconfig(self, guildid: str, language: str):
  try:
    stmt = insert(self.guildconfig).values(guildid=guildid, language=language).prefix_with('OR IGNORE')
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      result = conn.execute(stmt)
      conn.commit()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def update_guildconfig(self, guildid: str, language: str):
  try:
    stmt = update(self.guildconfig).where(self.guildconfig.c.guildid==guildid).values(language=language)
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      result = conn.execute(stmt)
      conn.commit()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def select_guildconfig(self, guildid: str, value="en"):
  try:
    value = value
    stmt = select(self.guildconfig.c.language).where(self.guildconfig.c.guildid==guildid)
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      cursor = conn.execute(stmt)
      records = cursor.fetchall()

      for row in records:
        value   =  row[0]
        cursor.close()
      
      return value
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return value

def insert_translation(self, from_lang: str, dest_lang: str, key: str, value: str):
  try:
    stmt = insert(self.translations).values(from_lang=from_lang, dest_lang=dest_lang, key=key, value=value).prefix_with('OR IGNORE')
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      result = conn.execute(stmt)
      conn.commit()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def select_translation(self, from_lang: str, dest_lang: str, key: str):
  try:
    value = None
    stmt = select(self.translations.c.value).where(self.translations.c.from_lang==from_lang,self.translations.c.dest_lang==dest_lang,self.translations.c.key==key)
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      cursor = conn.execute(stmt)
      records = cursor.fetchall()

      for row in records:
        value   =  row[0]
        cursor.close()
      
      return value
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return None