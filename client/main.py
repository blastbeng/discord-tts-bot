import os
import sys
import time
import utils
import time
import signal
import urllib
import typing
import asyncio
import logging
import pathlib
import requests
import database
import functools
import urllib.request
from PIL import Image
from contextlib import contextmanager
from typing import Literal, Optional
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

from translate import Translator

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Greedy, Context




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
            raise Exception("API Error! No voices available")
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

def check_image_with_pil(path):
    try:
        Image.open(path)
    except IOError:
        return False
    return True

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
    options.append(app_commands.Choice(name="Albanian", value="al"))
    options.append(app_commands.Choice(name="Arabic", value="ar"))
    options.append(app_commands.Choice(name="Croatian", value="hr"))
    options.append(app_commands.Choice(name="Chinese", value="zh"))
    options.append(app_commands.Choice(name="Danish", value="da"))
    options.append(app_commands.Choice(name="Dutch", value="nl"))
    options.append(app_commands.Choice(name="English", value="en"))
    options.append(app_commands.Choice(name="Finnish", value="fi"))
    options.append(app_commands.Choice(name="French", value="fr"))
    options.append(app_commands.Choice(name="German", value="de"))
    options.append(app_commands.Choice(name="Greek", value="el"))
    options.append(app_commands.Choice(name="Jewish", value="he"))
    options.append(app_commands.Choice(name="Hindi", value="hi"))
    options.append(app_commands.Choice(name="Italian", value="it"))
    options.append(app_commands.Choice(name="Japanese", value="ja"))
    options.append(app_commands.Choice(name="Korean", value="ko"))
    options.append(app_commands.Choice(name="Norwegian Bokmål", value="nb"))
    options.append(app_commands.Choice(name="Polish", value="pl"))
    options.append(app_commands.Choice(name="Portuguese", value="pt"))
    options.append(app_commands.Choice(name="Romanian", value="ro"))
    options.append(app_commands.Choice(name="Russian", value="ru"))
    options.append(app_commands.Choice(name="Spanish", value="es"))
    options.append(app_commands.Choice(name="Swedish", value="sv"))
    options.append(app_commands.Choice(name="Turkish", value="tr"))
    options.append(app_commands.Choice(name="Ukrainian", value="uk"))

    return options

optionslanguages = get_languages_menu()


#@function_timeout(seconds=5)
#def play_fakeyou_tts(text: str, voice: str, message: str, voice_client):
    

def get_voice_client_by_guildid(voice_clients, guildid):
    for vc in voice_clients:
        if vc.guild.id == guildid:
            return vc
    return None

async def connect_bot_by_voice_client(voice_client, channel):    
    if voice_client and voice_client.channel.id != channel.id:
        await voice_client.disconnect()
        await channel.connect()
    elif not voice_client:
        await channel.connect()

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
            raise Exception("Initializing chatterbot on chatid 000000 failed")

        logging.info(f'Logged in as {client.user} (ID: {client.user.id})')

        for guild in client.guilds:
            utils.insert_new_guild(str(guild.id), "en")
            client.tree.copy_global_to(guild=guild)
            await client.tree.sync(guild=guild)
            logging.info(f'Syncing commands to Guild (ID: {guild.id})')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        raise Exception(e)

@client.event
async def on_guild_join(guild):
    logging.info(f'Guild joined (ID: {guild.id})')
    utils.insert_new_guild(str(guild.id), "en")
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)
    logging.info(f'Syncing commands to Guild (ID: {guild.id})')
    name = client.user.name + " [en]"
    await guild.me.edit(nick=name)
    logging.info(f'Renaming bot to {name} to Guild (ID: {guild.id})')

@client.tree.command()
async def join(interaction: discord.Interaction):
    """Join channel."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)

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
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
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
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)

            if not hasattr(voice_client, 'play'):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():
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
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use /stop command"), ephemeral = True)


            
            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(text='text')
@app_commands.describe(text="the sentence to ask")
async def ask(interaction: discord.Interaction, text: str):
    """Ask something."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)

                
                if not hasattr(voice_client, 'play'):
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm saying an answer to") + ' "' + text + '"'

                    
                    voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"ask/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))), after=lambda e: logging.info(message))
                    await interaction.response.send_message(message, ephemeral = True)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use /stop command"), ephemeral = True)

                
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.describe(member="The user to insult")
async def insult(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Insult someone"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)

            if not hasattr(voice_client, 'play'):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():
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
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use /stop command"), ephemeral = True)

        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.context_menu(name="Insult")
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def insult_tree(interaction: discord.Interaction, member: discord.Member):
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)

            if not hasattr(voice_client, 'play'):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():
                currentguildid = get_current_guild_id(interaction.guild.id)
                voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult?text="+urllib.parse.quote(str(member.name))+ "&chatid="+urllib.parse.quote(currentguildid) + "&language=" + urllib.parse.quote(utils.get_guild_language(currentguildid))), after=lambda e: logging.info('Insulto ' + member.name))

                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I have insulted") + " " + member.name, ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use /stop command"), ephemeral = True)

        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.choices(voice=optionsvoices)
async def random(interaction: discord.Interaction, voice: Optional[app_commands.Choice[str]] = "random"):
    """Say a random sentence."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)

                if not hasattr(voice_client, 'play'):
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    voicename = None

                    if hasattr(voice, 'name'):
                        voicename = str(get_voice_code(voice.name))
                    else:
                        voicename = voice
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm saying a random sentence")
                    voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/"+urllib.parse.quote(voicename)+"/"+urllib.parse.quote(currentguildid)), after=lambda e: logging.info(message))
                    await interaction.response.send_message(message, ephemeral = True)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use /stop command"), ephemeral = True)

            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
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
    """Stop playback."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)

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
@app_commands.describe(name="New bot nickname (20 chars limit)")
async def rename(interaction: discord.Interaction, name: str):
    """Rename bot."""
    try:
        if len(name) < 20:
            currentguildid = get_current_guild_id(interaction.guild.id)
            
            message = interaction.user.name + " " + utils.translate(currentguildid," renamed me to") + ' "'+name+'"'
            name = name + " [" + utils.get_guild_language(currentguildid) + "]"
            await interaction.guild.me.edit(nick=name)
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(utils.translate(currentguildid,"My name can't be that longer (20 chars limit)"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(image='image')
@app_commands.describe(image="New bot avatar")
async def avatar(interaction: discord.Interaction, image: discord.Attachment):
    """Change bot avatar."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")) and str(interaction.user.id) == str(os.environ.get("ADMIN_ID")):
            if interaction.user.guild_permissions.administrator:
                imgfile=await image.to_file()
                filepath = os.environ.get("TMP_DIR") + "/avatar_guild_" + str(interaction.guild.id) + pathlib.Path(imgfile.filename).suffix
                with open(filepath, 'wb') as file:
                    file.write(imgfile.fp.getbuffer())
                if check_image_with_pil(filepath):
                    with open(filepath, 'rb') as f:
                        image = f.read()
                    await client.user.edit(avatar=image)
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"The image has been changed"), ephemeral = True)
                    os.remove(filepath)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This file type is not supported"), ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Only the bot owner can use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.rename(language='language')
@app_commands.describe(language="New bot language")
@app_commands.choices(language=optionslanguages)
async def language(interaction: discord.Interaction, language: app_commands.Choice[str]):
    """Change bot language."""
    try:
        currentguildid = get_current_guild_id(interaction.guild.id)
        if interaction.user.guild_permissions.administrator:

            utils.update_guild(currentguildid, language.value)
            name = interaction.guild.me.nick[:len(interaction.guild.me.nick) - 5] + " [" + utils.get_guild_language(currentguildid) + "]"
            await interaction.guild.me.edit(nick=name)
            await interaction.response.send_message(utils.translate(currentguildid,"Bot language changed to ") + ' "'+language.name+'"', ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(currentguildid,"Only administrators can use this command"), ephemeral = True)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to convert")
@app_commands.rename(language_to='language_to')
@app_commands.describe(language_to="The language to convert to")
@app_commands.choices(language_to=optionslanguages)
@app_commands.rename(language_from='language_from')
@app_commands.describe(language_from="The language to convert from")
@app_commands.choices(language_from=optionslanguages)
async def translate(interaction: discord.Interaction, text: str, language_to: app_commands.Choice[str], language_from: app_commands.Choice[str] = "xx"):
    """Translate a sentence and repeat it"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)

            if not hasattr(voice_client, 'play'):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():

                currentguildid = get_current_guild_id(interaction.guild.id)

                lang_to_use_from = ""
                if hasattr(language_from, 'name'):
                    lang_to_use_from = language_from.value
                else:
                    lang_to_use_from = utils.get_guild_language(currentguildid)


                translated_text = Translator(from_lang=lang_to_use_from, to_lang=language_to.value).translate(text)

                logging.info('I have translated "' + text + '" ' + '(' + language_to.value + ') to "' + translated_text + '" (' + lang_to_use_from + ')')

                message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm repeating") +' "' + text + '" (' + language_to.name + ')'

                
                voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(translated_text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(language_to.value)), after=lambda e: logging.info(message))
                await interaction.response.send_message(message, ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use /stop command"), ephemeral = True)

            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)

@client.tree.command()
@app_commands.rename(url='url')
@app_commands.describe(url="Youtube link (Must match https://www.youtube.com/watch?v=1abcd2efghi)")
async def youtube(interaction: discord.Interaction, url: str):
    """Play a youtube link"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel)
            
            if not hasattr(voice_client, 'play'):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():

                if "watch?v=" in url:
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm playing audio from") +' ' + url
                    voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_MUSIC")+"youtube/get/"+(url.split("watch?v=",1)[1])+"/"+urllib.parse.quote(currentguildid)), after=lambda e: logging.info(message))
                    await interaction.response.send_message(message, ephemeral = True)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use /stop command"), ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"URL must match something like https://www.youtube.com/watch?v=1abcd2efghi"), ephemeral = True)

            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)


client.run(os.environ.get("BOT_TOKEN"))

