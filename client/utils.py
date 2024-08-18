import os
import database
import subprocess
import shlex
import urllib
import io
import random
import logging
from discord.opus import Encoder
import discord
import aiohttp
from io import BytesIO
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))

class FFmpegPCMAudioBytesIO(discord.AudioSource):
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        stdin = None if not pipe else source
        args = [executable]
        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))
        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'panic'))
        #args.extend(('-af', 'loudnorm=I=-14:LRA=11:TP=-1', '-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'error'))
        #args.extend(('-af', 'dynaudnorm=p=1/sqrt(2):m=100:s=12:g=15', '-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'error'))
        if isinstance(options, str):
            args.extend(shlex.split(options))
        args.append('pipe:1')
        self._process = None
        try:
            self._process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
            self._stdout = io.BytesIO(
                self._process.communicate(input=stdin)[0]
            )
        except FileNotFoundError:
            raise discord.ClientException(executable + ' was not found.') from None
        except subprocess.SubprocessError as exc:
            raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(exc)) from exc
    def read(self):
        ret = self._stdout.read(Encoder.FRAME_SIZE)
        if len(ret) != Encoder.FRAME_SIZE:
            return b''
        return ret
    def cleanup(self):
        proc = self._process
        if proc is None:
            return
        proc.kill()
        if proc.poll() is None:
            proc.communicate()

        self._process = None



dbms = database.Database(database.SQLITE, dbname='client.sqlite3')
database.create_db_tables(dbms)


async def search_subito_db(guildid: str, url: str, title: str, link: str, price: str, location: str):
    return database.select_subito(dbms, guildid, url, title, link, price, location)

async def delete_subito_url(guildid: str, url: str):
    return database.delete_subito_url(dbms, guildid, url)

async def select_subito_urls(guildid: str):
    return database.select_subito_urls(dbms, guildid)

async def select_subito_channel(guildid: str, channel: str):
    return database.select_subito_channel(dbms, guildid, channel)

async def insert_subito_db(guildid: str, url: str, title: str, link: str, price: str, location: str, date: str, image: str, channel: str):
    if database.select_subito(dbms, guildid, url, title, link, price, location) is None:
        database.insert_subito(dbms, guildid, url, title, link, price, location, date, image, channel)

async def translate(guildid: str, text: str):
    tolang=database.select_guildconfig_lang(dbms, guildid, value = "it")
    fromlang='en'
    if tolang == fromlang:
        return text
    cached = database.select_translation(dbms, fromlang, tolang, text)
    if cached is not None:
        return cached
    else:
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_TEXT") + "translate/" + urllib.parse.quote(fromlang) + "/" + urllib.parse.quote(tolang) + "/" + urllib.parse.quote(text) + "/" + urllib.parse.quote(guildid)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if (response.status == 200):
                    translation_text = await response.text()
                    database.insert_translation(dbms, fromlang, tolang, text, translation_text)
                    return translation_text
                else:
                    return text

def insert_new_guild(guildid: str, language: str):
    database.insert_guildconfig(dbms, guildid, language, 0)

def update_guild_lang(guildid: str, language: str):
    database.update_guildconfig_lang(dbms, guildid, language)

def update_guild_nsfw(guildid: str, nswf: int):
    database.update_guildconfig_nsfw(dbms, guildid, nswf)

def get_guild_language(guildid: str):
    return database.select_guildconfig_lang(dbms, guildid, value = "it")

def get_guild_nsfw(guildid: str):
    return database.select_guildconfig_nsfw(dbms, guildid, value = 0)    

def check_exists_guild(guildid: str):
    value = database.select_guildconfig_lang(dbms, guildid, value = None)
    if value is None:
      database.insert_guildconfig(dbms, guildid, "it", 0)

def random_boolean():
    return bool(random.getrandbits(1))

def get_random_from_array(array):
    size = len(array)
    n = random.randint(0,size-1)
    return array[n]

def random_choice(text: str):
    return random.choice(text)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in "txt"