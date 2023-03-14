import os
import sys
import time
import utils
import signal
import urllib
import typing
import logging
import requests
import database
import functools
from contextlib import contextmanager
from typing import Optional
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

from translate import Translator

import discord
from discord import app_commands
from discord.ext import commands




dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

GUILD_ID = discord.Object(id=os.environ.get("GUILD_ID"))

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)


intents = discord.Intents.default()
client = MyClient(intents=intents)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

def function_timeout(seconds: int):
    """Wrapper of Decorator to pass arguments"""

    def decorator(func):
        @contextmanager
        def time_limit(seconds_):
            def signal_handler(signum, frame):  # noqa
                raise TimeoutException(f"Timed out in {seconds_} seconds!")

            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(seconds_)
            try:
                yield
            finally:
                signal.alarm(0)

        @wraps(func)
        def wrapper(*args, **kwargs):
            with time_limit(seconds):
                return func(*args, **kwargs)

        return wrapper

    return decorator

def listvoices():
    try:
        voices = []
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/fakeyou/get_voices_by_cat/Italiano"
        response = requests.get(url)
        if (response.text != "Internal Server Error"):
            data = response.json()
            for voice in data:   
                voices.append(voice)
        if len(voices) == 0:
            raise Exception("API Error! No voices available.")
        else:
            return voices
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        raise Exception(e)

def get_voice_code(voice: str):
    try:
        voices = []
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/fakeyou/get_voices_by_cat/Italiano"
        response = requests.get(url)
        if (response.text != "Internal Server Error"):
            data = response.json()
            return data[voice]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        raise Exception(e)

def get_voices_menu():

    voices = listvoices()
    #options = [
    #    app_commands.Choice(name="ASIX", value="ASIX"),
    #    app_commands.Choice(name="DAM", value="DAM")
    #    ]
    options = []
    for voice in voices:
        options.append(app_commands.Choice(name=voice, value=voice))

    return options

optionsvoices = get_voices_menu()

def get_languages_menu():

    voices = listvoices()
    #options = [
    #    app_commands.Choice(name="ASIX", value="ASIX"),
    #    app_commands.Choice(name="DAM", value="DAM")
    #    ]
    options = []    
    options.append(app_commands.Choice(name="Chinese", value="zh"))
    options.append(app_commands.Choice(name="Italian", value="it"))
    options.append(app_commands.Choice(name="English", value="en"))
    options.append(app_commands.Choice(name="French", value="fr"))
    options.append(app_commands.Choice(name="German", value="de"))
    options.append(app_commands.Choice(name="Italian", value="it"))
    options.append(app_commands.Choice(name="Japanese", value="ja"))
    options.append(app_commands.Choice(name="Korean", value="ko"))
    options.append(app_commands.Choice(name="Portuguese", value="pt"))
    options.append(app_commands.Choice(name="Romanian", value="ro"))
    options.append(app_commands.Choice(name="Russian", value="ru"))
    options.append(app_commands.Choice(name="Spanish", value="es"))

    return options

optionslanguages = get_languages_menu()


#@function_timeout(seconds=5)
#def play_fakeyou_tts(text: str, voice: str, message: str, voice_client):
    

def get_voice_client_by_guildid(voice_clients):
    for vc in voice_clients:
        if vc.guild.id == int(os.environ.get("GUILD_ID")):
            return vc
    return None

def get_current_guild_id(guildid):
    if str(guildid) == str(os.environ.get("GUILD_ID")):
        return '000000' 
    else:
        return str(guildid)

@client.event
async def on_ready():
    try:
        utils.check_exists_guild(str("000000"))
        lang = utils.get_guild_language("000000")
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/init/000000"
        response = requests.get(url)
        if (response.text == "Internal Server Error"):
            raise Exception("Initializing chatterbot on chatid 000000 failed.")

        logging.info(f'Logged in as {client.user} (ID: {client.user.id})')
        logging.info('------')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        raise Exception(e)

async def on_guild_join(self, guild):
    logging.info(f'Guild joined (ID: {guild.id})')
    utils.insert_new_guild(str(guild.id), "it")

@client.tree.command()
async def join(interaction: discord.Interaction):
    """Join channel."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients)
            if voice_client and voice_client.channel.id != interaction.user.voice.channel.id:
                await voice_client.disconnect()
                await interaction.user.voice.channel.connect()
            elif not voice_client:
                await interaction.user.voice.channel.connect()
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm joining the voice channel"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message("Errore!", ephemeral = True)

@client.tree.command()
async def leave(interaction: discord.Interaction):
    """Leave channel"""
    try:
        if interaction.user.guild_permissions.administrator:
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients)
                if voice_client and voice_client.channel.id == interaction.user.voice.channel.id:
                    await voice_client.disconnect()
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm leaving the voice channel"), ephemeral = True)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm not connected to any voice channel"), ephemeral = True)       
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:        
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to repeat")
@app_commands.rename(language='language')
@app_commands.describe(language="The language to convert to")
@app_commands.choices(language=optionslanguages)
async def speak(interaction: discord.Interaction, text: str, language: app_commands.Choice[str] = "Italian"):
    """Repeat a sentence"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients)
            if voice_client and voice_client.channel.id != interaction.user.voice.channel.id:
                await voice_client.disconnect()
                await interaction.user.voice.channel.connect()
            elif not voice_client:
                await interaction.user.voice.channel.connect()

            message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm repeating") +' "' + text + '"'

            currentguildid = get_current_guild_id(interaction.guild.id)

            lang_to_use = ""
            if hasattr(language, 'name'):
                lang_to_use = language.value
            else:
                lang_to_use = utils.get_guild_language(currentguildid)


            voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(lang_to_use)), after=lambda e: logging.info(message))
            await interaction.response.send_message(message, ephemeral = True)
            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"please wait a moment"), ephemeral = True)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="the sentence to ask")
async def ask(interaction: discord.Interaction, text: str):
    """Ask something."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients)
                if voice_client and voice_client.channel.id != interaction.user.voice.channel.id:
                    await voice_client.disconnect()
                    await interaction.user.voice.channel.connect()
                elif not voice_client:
                    await interaction.user.voice.channel.connect()

                
                currentguildid = get_current_guild_id(interaction.guild.id)
                message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm saying an answer to") + ' "' + text + '"'

                
                voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"ask/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))), after=lambda e: logging.info(message))
                await interaction.response.send_message(message, ephemeral = True)
                
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"please wait a moment"), ephemeral = True)

@client.tree.command()
@app_commands.describe(member="The user to insult")
async def insult(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Insult someone"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients)
            if voice_client and voice_client.channel.id != interaction.user.voice.channel.id:
                await voice_client.disconnect()
                await interaction.user.voice.channel.connect()
            elif not voice_client:
                await interaction.user.voice.channel.connect()

            insulturl=os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult"
            insultresponse=""
            currentguildid = get_current_guild_id(interaction.guild.id)
            if member:
                insulturl=insulturl +"?text="+urllib.parse.quote(str(member.name)) + "&chatid="+urllib.parse.quote(get_current_guild_id(interaction.guild.id)) + "&language=" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                insultresponse=utils.translate(get_current_guild_id(interaction.guild.id),"I'm insulting") + ' "' + str(member.name) +'"'
            else:
                insulturl=insulturl +"?chatid="+urllib.parse.quote(get_current_guild_id(interaction.guild.id)) + "&language=" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                insultresponse=utils.translate(get_current_guild_id(interaction.guild.id),"I'm saying an insult")

            
            voice_client.play(discord.FFmpegPCMAudio(insulturl), after=lambda e: logging.info('Ho insultato: ' + str(member.name)))

            await interaction.response.send_message(insultresponse, ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"please wait a moment"), ephemeral = True)

@client.tree.context_menu(name="Insult him!")
async def insult_tree(interaction: discord.Interaction, member: discord.Member):
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients)
            if voice_client and voice_client.channel.id != interaction.user.voice.channel.id:
                await voice_client.disconnect()
                await interaction.user.voice.channel.connect()
            elif not voice_client:
                await interaction.user.voice.channel.connect()
            currentguildid = get_current_guild_id(interaction.guild.id)
            voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult?text="+urllib.parse.quote(str(member.name))+ "&chatid="+urllib.parse.quote(currentguildid) + "&language=" + urllib.parse.quote(utils.get_guild_language(currentguildid))), after=lambda e: logging.info('Insulto ' + member.name))

            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I have insulted") + " " + member.name, ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"please wait a moment"), ephemeral = True)

@client.tree.command()
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.choices(voice=optionsvoices)
async def random(interaction: discord.Interaction, voice: Optional[app_commands.Choice[str]] = "random"):
    """Say a random sentence."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients)
                if voice_client and voice_client.channel.id != interaction.user.voice.channel.id:
                    await voice_client.disconnect()
                    await interaction.user.voice.channel.connect()
                elif not voice_client:
                    await interaction.user.voice.channel.connect()

                voicename = None

                if hasattr(voice, 'name'):
                    voicename = str(get_voice_code(voice.name))
                else:
                    voicename = voice
                currentguildid = get_current_guild_id(interaction.guild.id)
                message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm saying a random sentence.")
                voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/"+urllib.parse.quote(voicename)+"/"+urllib.parse.quote(currentguildid)), after=lambda e: logging.info(message))
                await interaction.response.send_message(message, ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"please wait a moment"), ephemeral = True)

@client.tree.command()
async def restart(interaction: discord.Interaction):
    """Restart bot."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Restarting bot."), ephemeral = True)
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
async def stop(interaction: discord.Interaction):
    """Stop talking."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients)
            if voice_client and voice_client.channel.id != interaction.user.voice.channel.id:
                await voice_client.disconnect()
                await interaction.user.voice.channel.connect()
            elif not voice_client:
                await interaction.user.voice.channel.connect()

            voice_client.stop()
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm interrupting the bot"), ephemeral = True)
            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.rename(name='name')
@app_commands.describe(name="New bot nickname (25 chars limit)")
async def rename(interaction: discord.Interaction, name: str):
    """Rename bot."""
    try:
        if len(name) < 25:
            for guild in client.guilds:
                await guild.me.edit(nick=name)
            await interaction.response.send_message(interaction.user.name + " " + utils.translate(get_current_guild_id(interaction.guild.id)," renamed me to") + ' "'+name+'"')
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"My name can't be that longer (25 chars limit)"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.rename(language='language')
@app_commands.describe(language="New bot language")
@app_commands.choices(language=optionslanguages)
async def changelanguage(interaction: discord.Interaction, language: app_commands.Choice[str]):
    """Change bot language."""
    try:
        if interaction.user.guild_permissions.administrator:
            utils.update_guild(get_current_guild_id(interaction.guild.id), language.value)
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Bot language changed to ") + ' "'+language.name+'"', ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to convert")
@app_commands.rename(language='language')
@app_commands.describe(language="The language to convert to")
@app_commands.choices(language=optionslanguages)
async def translate(interaction: discord.Interaction, text: str, language: app_commands.Choice[str]):
    """Translate a sentence and repeat it"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients)
            if voice_client and voice_client.channel.id != interaction.user.voice.channel.id:
                await voice_client.disconnect()
                await interaction.user.voice.channel.connect()
            elif not voice_client:
                await interaction.user.voice.channel.connect()

            currentguildid = get_current_guild_id(interaction.guild.id)


            translated_text = Translator(from_lang=utils.get_guild_language(currentguildid), to_lang=language.value).translate(text)

            

            message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm repeating") +' "' + text + '" (' + language.name + ')'

            
            voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(translated_text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(language.value)), after=lambda e: logging.info(message))
            await interaction.response.send_message(message, ephemeral = True)
            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"please wait a moment"), ephemeral = True)

client.run(os.environ.get("BOT_TOKEN"))

