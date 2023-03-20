import os
import re
import sys
import time
import utils
import signal
import random
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
from discord.ext import commands, tasks
from discord.ext.commands import Greedy, Context


from io import BytesIO
from utils import FFmpegPCMAudioBytesIO

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

GUILD_ID = discord.Object(id=os.environ.get("GUILD_ID"))

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


intents = discord.Intents.default()
client = MyClient(intents=intents)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger('discord')
logger.setLevel(int(os.environ.get("LOG_LEVEL")))

discord.utils.setup_logging(level=int(os.environ.get("LOG_LEVEL")), root=False)



def listvoices():
    try:
        voices = []
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/fakeyou/get_voices_by_cat/Italiano"
        response = requests.get(url)
        if (response.text != "Internal Server Error") and response.status_code == 200:
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
        if (response.text != "Internal Server Error") and response.status_code == 200:
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
    options = []
    for voice in voices:
        options.append(app_commands.Choice(name=voice, value=voice))

    return options

optionsvoices = get_voices_menu()

def get_languages_menu():

    options = []    
    options.append(app_commands.Choice(name="Afrikaans (South Africa)", value="za"))
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
    options.append(app_commands.Choice(name="Hindi", value="hi"))
    options.append(app_commands.Choice(name="Italian", value="it"))
    options.append(app_commands.Choice(name="Japanese", value="ja"))
    options.append(app_commands.Choice(name="Korean", value="ko"))
    options.append(app_commands.Choice(name="Norwegian (Bokmål)", value="no"))
    options.append(app_commands.Choice(name="Polish", value="pl"))
    options.append(app_commands.Choice(name="Portuguese", value="pt"))
    options.append(app_commands.Choice(name="Romanian", value="ro"))
    options.append(app_commands.Choice(name="Russian", value="ru"))
    options.append(app_commands.Choice(name="Spanish", value="es"))
    options.append(app_commands.Choice(name="Swedish", value="sv"))
    options.append(app_commands.Choice(name="Turkish", value="tr"))
    options.append(app_commands.Choice(name="Ukrainian", value="uk"))
    options.append(app_commands.Choice(name="Vietnamese", value="vn"))

    return options

optionslanguages = get_languages_menu()

async def send_error(e, interaction):
    if isinstance(e, app_commands.CommandOnCooldown):
        currentguildid=get_current_guild_id(interaction.guild.id)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Please! Do not spam!"), ephemeral=True)
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)
    

def get_voice_client_by_guildid(voice_clients, guildid):
    for vc in voice_clients:
        if vc.guild.id == guildid:
            return vc
    return None

async def connect_bot_by_voice_client(voice_client, channel, guild):    
    if voice_client and not voice_client.is_playing() and voice_client.channel and voice_client.channel.id != channel.id:
        await voice_client.disconnect()
        await channel.connect()
        if guild is not None:
            await guild.change_voice_state(channel=channel, self_deaf=True)
    elif not voice_client or not voice_client.channel:
        await channel.connect()
        if guild is not None:
            await guild.change_voice_state(channel=channel, self_deaf=True)

def get_current_guild_id(guildid):
    if str(guildid) == str(os.environ.get("GUILD_ID")):
        return '000000' 
    else:
        return str(guildid)

async def do_play(voice_client, url: str, interaction: discord.Interaction, currentguildid: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    response = requests.get(url)
    if (response.status_code == 200 and response.content):
        message = response.headers["X-Generated-Text"]
        voice_client.play(FFmpegPCMAudioBytesIO(response.content, pipe=True), after=lambda e: logging.info("do_play - " + message))
        await interaction.followup.send(message, ephemeral = True)
    else:
        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Error!"), ephemeral = True)

@tasks.loop(seconds=180)
async def play_audio_loop():
    try:
        for guild in client.guilds:
            if str(guild.id) == str(os.environ.get("GUILD_ID")):
                channelfound = None
                channeluserfound = None
                voice_client = get_voice_client_by_guildid(client.voice_clients, guild.id)                
                for channel in guild.voice_channels:
                    for member in channel.members:
                        if not member.bot:
                            channeluserfound = channel
                            break
                if voice_client is None or voice_client.channel is None:
                    channelfound = channeluserfound
                else:
                    channelfound = voice_client.channel
                if channelfound is not None and channeluserfound is not None:
                    await connect_bot_by_voice_client(voice_client, channelfound, None)
                    if hasattr(voice_client, 'play') and not voice_client.is_playing():
                        #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/random/000000"))
                        if utils.random_boolean():
                            response = requests.get(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/random/000000")
                            if (response.status_code == 200 and response.content):
                                message = 'play_audio_loop - random - ' + response.headers["X-Generated-Text"]
                                voice_client.play(FFmpegPCMAudioBytesIO(response.content, pipe=True), after=lambda e: logging.info(message))
                        else:
                            response_gen = requests.get(os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/sentences/generate/000000/0")
                            if (response_gen.text != "Internal Server Error" and response_gen.status_code == 200):
                                response = requests.get(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(response_gen.text))+"/google/000000/it")
                                if (response.status_code == 200 and response.content):
                                    message = 'play_audio_loop - generate - ' + response.headers["X-Generated-Text"]
                                    voice_client.play(FFmpegPCMAudioBytesIO(response.content, pipe=True), after=lambda e: logging.info(message))
                break
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

@client.event
async def on_ready():
    try:
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/init/000000"
        response = requests.get(url)
        if (response.text == "Internal Server Error"):
            raise Exception("Initializing chatterbot on chatid 000000 failed")

        logging.info(f'Logged in as {client.user} (ID: {client.user.id})')

        for guild in client.guilds:
            utils.check_exists_guild('000000' if str(guild.id) == str(os.environ.get("GUILD_ID")) else str(guild.id))
            client.tree.copy_global_to(guild=guild)
            await client.tree.sync(guild=guild)
            logging.info(f'Syncing commands to Guild (ID: {guild.id})')
            nick = None
            if guild.me.nick is None:
                nick = client.user.name + " [" + utils.get_guild_language('000000' if str(guild.id) == str(os.environ.get("GUILD_ID")) else str(guild.id)) + "]"
            elif re.search(r'\[[a-z][a-z]\]', guild.me.nick) is None:
                if len(guild.me.nick) > 20:
                    nick = client.user.name + " [" + utils.get_guild_language('000000' if str(guild.id) == str(os.environ.get("GUILD_ID")) else str(guild.id)) + "]"
                else:
                    nick = guild.me.nick[:len(guild.me.nick) - 5] + " [" + utils.get_guild_language('000000' if str(guild.id) == str(os.environ.get("GUILD_ID")) else str(guild.id)) + "]"
            if nick is not None:
                await guild.me.edit(nick=nick)
                logging.info(f'Renaming bot to {nick} for Guild (ID: {guild.id})')

        await play_audio_loop.start()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        raise Exception(e)


@client.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        voice_client = get_voice_client_by_guildid(client.voice_clients, member.guild.id)
        await connect_bot_by_voice_client(voice_client, after.channel, None)

@client.event
async def on_guild_join(guild):
    logging.info(f'Guild joined (ID: {guild.id})')
    utils.check_exists_guild('000000' if str(guild.id) == str(os.environ.get("GUILD_ID")) else str(guild.id))
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)
    logging.info(f'Syncing commands to Guild (ID: {guild.id})')
    name = client.user.name + " [en]"
    await guild.me.edit(nick=name)
    logging.info(f'Renaming bot to {name} to Guild (ID: {guild.id})')

@client.tree.command()
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def join(interaction: discord.Interaction):
    """Join channel."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm joining the voice channel"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
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
        await send_error(e, interaction)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to repeat")
@app_commands.rename(language='language')
@app_commands.describe(language="The language to convert to")
@app_commands.choices(language=optionslanguages)
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def speak(interaction: discord.Interaction, text: str, language: app_commands.Choice[str] = "Italian"):
    """Repeat a sentence"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if not hasattr(voice_client, 'play'):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():

                currentguildid = get_current_guild_id(interaction.guild.id)

                lang_to_use = ""
                if hasattr(language, 'name'):
                    lang_to_use = language.value
                else:
                    lang_to_use = utils.get_guild_language(currentguildid)
                #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(lang_to_use)), after=lambda e: logging.info(message))
                
                url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(lang_to_use)
                #message =utils.translate(currentguildid,"I'm repeating") +' "' + text + '" (' + lang_to_use + ')'
                await do_play(voice_client, url, interaction, currentguildid)


            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(text='text')
@app_commands.describe(text="the sentence to ask")
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def ask(interaction: discord.Interaction, text: str):
    """Ask something."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                
                if not hasattr(voice_client, 'play'):
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    #message =utils.translate(get_current_guild_id(interaction.guild.id),"I'm saying an answer to") + ' "' + text + '" '

                    
                    #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"ask/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))), after=lambda e: logging.info(message))
                    #await interaction.response.send_message(message, ephemeral = True)
                    
                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"ask/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                    await do_play(voice_client, url, interaction, currentguildid)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

                
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)



@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def generate(interaction: discord.Interaction):
    """Generate a random sentence."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                
                if not hasattr(voice_client, 'play'):
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    currentguildid = get_current_guild_id(interaction.guild.id)

                    url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/sentences/generate/" + urllib.parse.quote(currentguildid) + "/0"
                    response = requests.get(url)
                    if (response.text != "Internal Server Error" and response.status_code == 200):
                        #message =utils.translate(get_current_guild_id(interaction.guild.id),"I have generated the sentence ") + ' "' + response.text + '"'
                        #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(response.text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))), after=lambda e: logging.info(message))
                        #await interaction.response.send_message(message, ephemeral = True)
                        url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(response.text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                        await do_play(voice_client, url, interaction, currentguildid)
                    else:
                        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)     
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)


@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.user.id))
async def story(interaction: discord.Interaction):
    """Generate a random story."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                
                if not hasattr(voice_client, 'play'):
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    currentguildid = get_current_guild_id(interaction.guild.id)

                    url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/paragraph/generate/" + urllib.parse.quote(currentguildid)
                    response = requests.get(url)
                    if (response.text != "Internal Server Error" and response.status_code == 200):
                        #message =utils.translate(get_current_guild_id(interaction.guild.id),"I have generated the paragraph ") + ' "' + response.text + '"'
                        #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(response.text))+"/google/"+urllib.parse.quote(currentguildid)), after=lambda e: logging.info(message))
                        #await interaction.response.send_message(message, ephemeral = True)
                        url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(response.text))+"/google/"+urllib.parse.quote(currentguildid)
                        await do_play(voice_client, url, interaction, currentguildid)
                    else:
                        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error")+"!", ephemeral = True)     
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.describe(member="The user to insult")
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def insult(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Insult someone"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

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

                
                #voice_client.play(discord.FFmpegPCMAudio(insulturl), after=lambda e: logging.info('Ho insultato: ' + str(member.name)))
                #await interaction.response.send_message(insultresponse, ephemeral = True)

                await do_play(voice_client, insulturl, interaction, currentguildid)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.context_menu(name="Insult")
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def insult_tree(interaction: discord.Interaction, member: discord.Member):
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if not hasattr(voice_client, 'play'):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():
                currentguildid = get_current_guild_id(interaction.guild.id)
                #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult?text="+urllib.parse.quote(str(member.name))+ "&chatid="+urllib.parse.quote(currentguildid) + "&language=" + urllib.parse.quote(utils.get_guild_language(currentguildid))), after=lambda e: logging.info('Insulto ' + member.name))

                #await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I have insulted") + " " + member.name, ephemeral = True)
                #message =utils.translate(get_current_guild_id(interaction.guild.id),"I have insulted") + " " + member.name
                url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult?text="+urllib.parse.quote(str(member.name))+ "&chatid="+urllib.parse.quote(currentguildid) + "&language=" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                await do_play(voice_client, url, interaction, currentguildid)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.choices(voice=optionsvoices)
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def random(interaction: discord.Interaction, voice: Optional[app_commands.Choice[str]] = "random"):
    """Say a random sentence."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                if not hasattr(voice_client, 'play'):
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    voicename = None

                    if hasattr(voice, 'name'):
                        voicename = str(get_voice_code(voice.name))
                    else:
                        voicename = voice
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    #message = utils.translate(get_current_guild_id(interaction.guild.id),"I'm saying a random sentence")
                    #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/"+urllib.parse.quote(voicename)+"/"+urllib.parse.quote(currentguildid)), after=lambda e: logging.info(message))
                    #await interaction.response.send_message(message, ephemeral = True)

                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/"+urllib.parse.quote(voicename)+"/"+urllib.parse.quote(currentguildid)
                    await do_play(voice_client, url, interaction, currentguildid)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
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
        await send_error(e, interaction)

@client.tree.command()
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def stop(interaction: discord.Interaction):
    """Stop playback."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            logging.info("stop - voice_client.stop()")
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm interrupting the bot"), ephemeral = True)
            voice_client.stop()
            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.rename(name='name')
@app_commands.describe(name="New bot nickname (20 chars limit)")
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
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
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"My name can't be that longer (20 chars limit)"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(image='image')
@app_commands.describe(image="New bot avatar")
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
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
        await send_error(e, interaction)

@client.tree.command()
@app_commands.rename(language='language')
@app_commands.describe(language="New bot language")
@app_commands.choices(language=optionslanguages)
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def language(interaction: discord.Interaction, language: app_commands.Choice[str]):
    """Change bot language."""
    try:
        currentguildid = get_current_guild_id(interaction.guild.id)
        if interaction.user.guild_permissions.administrator:

            utils.update_guild(currentguildid, language.value)

            nick = interaction.guild.me.nick
            if nick is None:
                nick = client.user.name
            else:
                x = re.search(r'\[[a-z][a-z]\]', nick)
                if x is not None:
                    nick = interaction.guild.me.nick[:len(interaction.guild.me.nick) - 5]
                elif len(nick) > 20:
                    nick = client.user.name
                else:
                    nick = interaction.guild.me.nick[:len(interaction.guild.me.nick) - 5]

            name = nick + " [" + utils.get_guild_language(currentguildid) + "]"
            await interaction.guild.me.edit(nick=name)
            await interaction.response.send_message(utils.translate(currentguildid,"Bot language changed to ") + ' "'+language.name+'"', ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(currentguildid,"Only administrators can use this command"), ephemeral = True)
        
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to convert")
@app_commands.rename(language_to='language_to')
@app_commands.describe(language_to="The language to convert to")
@app_commands.choices(language_to=optionslanguages)
@app_commands.rename(language_from='language_from')
@app_commands.describe(language_from="The language to convert from")
@app_commands.choices(language_from=optionslanguages)
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def translate(interaction: discord.Interaction, text: str, language_to: app_commands.Choice[str], language_from: app_commands.Choice[str] = "xx"):
    """Translate a sentence and repeat it"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

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

                #message =utils.translate(get_current_guild_id(interaction.guild.id),"I have translated") + ' "' + text + '" ' + '(' + lang_to_use_from + ') => "' + translated_text + '" (' + language_to.value + ')'

                
                #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(translated_text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(language_to.value)), after=lambda e: logging.info(message))
                #await interaction.response.send_message(message, ephemeral = True)
                
                url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(translated_text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(language_to.value)
                await do_play(voice_client, url, interaction, currentguildid)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.rename(url='url')
@app_commands.describe(url="Youtube link (Must match https://www.youtube.com/watch?v=1abcd2efghi)")
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def youtube(interaction: discord.Interaction, url: str):
    """Play a youtube link"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
            
            if not hasattr(voice_client, 'play'):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():

                if "watch?v=" in url:
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    #message =utils.translate(get_current_guild_id(interaction.guild.id),"I'm playing audio from") +' ' + url
                    
                    #voice_client.play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_MUSIC")+"youtube/get/"+(url.split("watch?v=",1)[1])+"/"+urllib.parse.quote(currentguildid)), after=lambda e: logging.info(message))
                    #await interaction.response.send_message(message, ephemeral = True)

                    urlapi = os.environ.get("API_URL")+os.environ.get("API_PATH_MUSIC")+"youtube/get/"+(url.split("watch?v=",1)[1])+"/"+urllib.parse.quote(currentguildid)
                    await do_play(voice_client, urlapi, interaction, currentguildid)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"URL must match something like https://www.youtube.com/watch?v=1abcd2efghi"), ephemeral = True)

            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def enable(interaction: discord.Interaction):
    """Enable auto talking feature."""
    try:
        if not play_audio_loop.is_running():
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Enabling the auto mode"), ephemeral = True)
            play_audio_loop.start()
            logging.info("enable - play_audio_loop.start()")
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Auto mode is already enabled"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def disable(interaction: discord.Interaction):
    """Disable auto talking feature."""

    try:
        if play_audio_loop.is_running():
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Disabling the auto mode"), ephemeral = True)
            play_audio_loop.stop()
            logging.info("disable - play_audio_loop.stop()")
            play_audio_loop.cancel()
            logging.info("disable - play_audio_loop.cancel()")
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Auto mode is already disabled"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(seconds='seconds')
@app_commands.describe(seconds="Timeout seconds (Min 20 - Max 600)")
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.user.id))
async def timer(interaction: discord.Interaction, seconds: int):
    """Change the timer for the auto talking feature."""

    try:
        if seconds < 20 or seconds > 300:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Seconds must be greater than 20 and lower than 600"), ephemeral = True)
        else:
            play_audio_loop.change_interval(seconds=seconds)
            logging.info("timer - play_audio_loop.change_interval(seconds="+str(seconds)+")")
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm setting a " + str(seconds) + " seconds timer for the auto talking feature"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction)




@enable.error
@disable.error
@timer.error
@join.error
@leave.error
@speak.error
@avatar.error
@language.error
@ask.error
@random.error
@story.error
@stop.error
@translate.error
@youtube.error
@rename.error
@insult.error
@insult_tree.error
@generate.error
async def on_generic_error(interaction: discord.Interaction, e: app_commands.AppCommandError):
    await send_error(e, interaction)

client.run(os.environ.get("BOT_TOKEN"))

