import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy import create_engine, insert, select, update, delete, Table, Column, Integer, String, MetaData

SQLITE          = 'sqlite'
GUILDCONFIG     = 'guildconfig'
TRANSLATIONS    = 'translations'
SUBITO          = 'subito'
#TRACKEDUSERS    = 'trackedusers'

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
                Column('language', String(50), nullable=False),
                Column('nsfw', Integer, nullable=False)
                )

  translations = Table(TRANSLATIONS, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('from_lang', String(50), nullable=False),
                Column('dest_lang', String(50), nullable=False),
                Column('key', String(500), nullable=False),
                Column('value', String(500), nullable=False)
                )

  subito = Table(SUBITO, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('guildid', String(50), nullable=False),
                Column('url', String(500), nullable=False),
                Column('title', String(500), nullable=False),
                Column('link', String(500), nullable=False),
                Column('price', String(500), nullable=True),
                Column('location', String(500), nullable=True),
                Column('date', String(500), nullable=True),
                Column('image', String(500), nullable=True),
                Column('channel', String(500), nullable=True)
                )

  #trackedusers = Table(TRACKEDUSERS, metadata,
  #             Column('id', Integer, primary_key=True),
  #             Column('memberid', String(50), nullable=False),
  #             Column('name', String(500), nullable=False),
  #             Column('guildid', String(50), nullable=False),
  #             Column('whatsapp', Integer, nullable=False),
  #             Column('istracked', Integer, nullable=False)
  #             )

def create_db_tables(self):
  try:
    self.metadata.create_all(self.db_engine)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def insert_guildconfig(self, guildid: str, language: str, nsfw: int):
  try:
    stmt = insert(self.guildconfig).values(guildid=guildid, language=language, nsfw=0).prefix_with('OR IGNORE')
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      result = conn.execute(stmt)
      conn.commit()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def update_guildconfig_lang(self, guildid: str, language: str):
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

def update_guildconfig_nsfw(self, guildid: str, nsfw: int):
  try:
    stmt = update(self.guildconfig).where(self.guildconfig.c.guildid==guildid).values(nsfw=nsfw)
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      result = conn.execute(stmt)
      conn.commit()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def select_guildconfig_lang(self, guildid: str, value="it"):
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

def select_guildconfig_nsfw(self, guildid: str, value=0):
  try:
    value = value
    stmt = select(self.guildconfig.c.nsfw).where(self.guildconfig.c.guildid==guildid)
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

def insert_subito(self, guildid: str, url: str, title: str, link: str, price: str, location: str, date: str, image: str, channel: str):
  try:
    stmt = insert(self.subito).values(guildid=guildid, url=url, title=title, link=link, price=price, location=location, date=date, image=image, channel=channel).prefix_with('OR IGNORE')
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      result = conn.execute(stmt)
      conn.commit()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def delete_subito_url(self, guildid: str, url: str):
  try:
    stmt = delete(self.subito).where(self.subito.c.guildid==guildid, self.subito.c.url==url,self.subito.c.title=='',self.subito.c.link=='',self.subito.c.price=='',self.subito.c.location=='')
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      result = conn.execute(stmt)
      conn.commit()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def select_subito(self,guildid: str,  url: str, title: str, link: str, price: str, location: str):
  try:
    value = None
    stmt = select(self.subito.c.id).where(self.subito.c.guildid==guildid, self.subito.c.url==url,self.subito.c.title==title,self.subito.c.link==link,self.subito.c.price==price,self.subito.c.location==location)
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


def select_subito_urls(self, guildid: str):
  try:
    value = []
    stmt = select(self.subito.c.url).where(self.subito.c.guildid==guildid, self.subito.c.title=='',self.subito.c.link=='',self.subito.c.price=='',self.subito.c.location=='').distinct()
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      cursor = conn.execute(stmt)
      records = cursor.fetchall()

      for row in records:
        value.append(str(row[0]))
        cursor.close()
      
      return value
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return None


def select_subito_channel(self, guildid: str, url: str):
  try:
    value = None
    stmt = select(self.subito.c.channel).where(self.subito.c.guildid==guildid, self.subito.c.url==url,self.subito.c.title=='',self.subito.c.link=='',self.subito.c.price=='',self.subito.c.location=='').distinct()
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      cursor = conn.execute(stmt)
      records = cursor.fetchall()

      for row in records:
        value = (str(row[0]))
        cursor.close()
      
      return value
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return None

#def insert_trackedusers(self, memberid: str, name: str, guildid: str, whatsapp: str, istracked=istracked):
#  try:
#    stmt = insert(self.trackedusers).values(memberid=memberid, name=name, guildid=guildid, whatsapp=whatsapp, istracked=istracked).prefix_with('OR IGNORE')
#    compiled = stmt.compile()
#    with self.db_engine.connect() as conn:
#      result = conn.execute(stmt)
#      conn.commit()
#  except Exception as e:
#    exc_type, exc_obj, exc_tb = sys.exc_info()
#    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)