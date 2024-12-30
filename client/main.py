
import os
import sys
import json
import time
import utils
import socket
import random as randompy
import urllib
import logging
import pathlib
import constants
import urllib.request
from PIL import Image
from typing import Optional
from os.path import join, dirname
from dotenv import load_dotenv, set_key
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.errors import ClientException
from datetime import datetime
from typing import List
import asyncio
import requests
import aiohttp
import io
from random import randint
import requests.exceptions
import psutil
import json
#from discord.ext import listening


from utils import FFmpegPCMAudioBytesIO

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

login_audios = None
def get_login_audios():
    global login_audios
    if login_audios is None:
        path_login_audios = os.path.join(dirname(__file__) + '/config/login_audios.json')
        if os.path.isfile(path_login_audios):
            with open(path_login_audios, 'r') as file_login_audios:
                login_audios = json.load(file_login_audios)
    return login_audios

logout_audios = None
def get_logout_audios():
    global logout_audios
    if logout_audios is None:
        path_logout_audios = os.path.join(dirname(__file__) + '/config/logout_audios.json')
        if os.path.isfile(path_logout_audios):
            with open(path_logout_audios, 'r') as file_logout_audios:
                logout_audios = json.load(file_logout_audios)
    return logout_audios

#process_pool = listening.AudioProcessPool(1)


GUILD_ID = discord.Object(id=os.environ.get("GUILD_ID"))

def get_api_url():
    return os.environ.get("API_URL")

def get_voiceclone_api_url():
    return os.environ.get("API_VOICECLONE_URL")

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

class AdminPermissionError(Exception):
    pass

class ExcludedPermissionError(Exception):
    pass

class PermissionError(Exception):
    pass

class NoChannelError(Exception):
    pass

class CustomTextInput(discord.ui.TextInput):
        
    def __init__(self, style, name):
        super().__init__(style=style, label=name, value="")

class SoundBoardButton(discord.ui.Button["InteractionRoles"]):

    audiourl = ""

    def __init__(self, name: str, audiourl: str):
        super().__init__(style=discord.ButtonStyle.primary, label=name)
        self.name = name
        self.audiourl = audiourl
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            check_permissions(interaction)
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:
                currentguildid = get_current_guild_id(interaction.guild.id)
                await do_play(self.audiourl, interaction, currentguildid, name = self.name)
            else:
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The bot is not ready yet or another user is already using another command.") +"\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)            
            
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

class SlashCommandButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, style, name):
        super().__init__(style=style, label="/"+name)
        self.name = name
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            if self.name == constants.CURSE:
                await interaction.followup.send("/curse -> curse.", ephemeral = True)
            elif self.name == constants.INSULT:
                await interaction.followup.send("/insult <member> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Insult someone"), ephemeral = True)
            elif self.name == constants.RANDOM:
                await interaction.followup.send("/random -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Random sentence"), ephemeral = True)
            elif self.name == constants.TIMER:
                await interaction.followup.send("/timer <seconds> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"This is used to set the timer for the auto talking feature"), ephemeral = True)
            elif self.name == constants.SPEAK:
                await interaction.followup.send("/speak <text> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot repeats something"), ephemeral = True)
            elif self.name == constants.TRANSLATE:
                await interaction.followup.send("/translate <text> <language_to> <language_from[Optional]> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot translates a text"), ephemeral = True)
            elif self.name == constants.GENERATE:
                await interaction.followup.send("/generate -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Generate a random sentence"), ephemeral = True)
            elif self.name == constants.STORY:
                await interaction.followup.send("/story -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Generate a random story"), ephemeral = True)
            elif self.name == constants.ENABLE:
                await interaction.followup.send("/enable -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Enable auto talking feature"), ephemeral = True)
            elif self.name == constants.DISABLE:
                await interaction.followup.send("/disable -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Disable auto talking feature"), ephemeral = True)
            elif self.name == constants.JOIN:
                await interaction.followup.send("/join -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot joins the voice channel"), ephemeral = True)
            elif self.name == constants.LEAVE:
                await interaction.followup.send("/leave -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot leaves the voice channel"), ephemeral = True)
            elif self.name == constants.RENAME:
                await interaction.followup.send("/rename <name> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its name"), ephemeral = True)
            elif self.name == constants.SOUNDRANDOM:
                await interaction.followup.send("/soundrandom <text> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot searches and plays an audio results"), ephemeral = True)
            elif self.name == constants.SOUNDSEARCH:
                await interaction.followup.send("/soundsearch <text> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot searches and displays audio results, allowing you to play them"), ephemeral = True)
            elif self.name == constants.YOUTUBE:
                await interaction.followup.send("/youtube <url> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Listen to a youtube song"), ephemeral = True)
            elif self.name == constants.STOP:
                await interaction.followup.send("/stop -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot stops talking"), ephemeral = True)
            elif self.name == constants.DISCLAIMER:
                await interaction.followup.send("/disclaimer -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Show disclaimer"), ephemeral = True)
            elif self.name == constants.TRAIN:
                await interaction.followup.send("/train <file> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot inserts in its database the sentencess present in the TXT file"), ephemeral = True)
            elif self.name == constants.WIKIPEDIA:
                await interaction.followup.send("/wikipedia <text> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot searches something on wikipedia"), ephemeral = True)
            elif self.name == constants.AUDIO:
                await interaction.followup.send("/audio <audio> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Audio playback") + " " + await utils.translate(get_current_guild_id(interaction.guild.id),"from an audio file"), ephemeral = True)
            #elif self.name == constants.BARD:
            #    await interaction.followup.send("/bard <text> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot asks something to") + " Google Bard APIs", ephemeral = True)
            else:
                await interaction.followup.send("Work in progress", ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)



class AdminCommandButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, style, name):
        super().__init__(style=style, label="/"+name)
        self.name = name
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:            
            await interaction.response.defer(thinking=True, ephemeral=True)
            if self.name == constants.LANGUAGE:
                await interaction.followup.send("/language <language> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its main language"), ephemeral = True)
            elif self.name == constants.AVATAR:
                await interaction.followup.send("/avatar <image> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its avatar"), ephemeral = True)
            elif self.name == constants.DELETE:
                await interaction.followup.send("/delete <text> -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot deletes all the sentences containing the given text"), ephemeral = True)
            elif self.name == constants.DOWNLOAD:
                await interaction.followup.send("/download -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"Downloads a copy of the BOT's database"), ephemeral = True)           
            elif self.name == constants.RESET:
                await interaction.followup.send("/reset -> " + await utils.translate(get_current_guild_id(interaction.guild.id),"The bot resets its database and deletes all the saved sentences"), ephemeral = True)         
            else:
                await interaction.followup.send("Work in progress", ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

class SaveButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, message):
        super().__init__(style=discord.ButtonStyle.primary, label="Save")
        self.message = message
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            currentguildid = get_current_guild_id(interaction.guild.id)
            url = get_api_url() + os.environ.get("API_PATH_TEXT") + "repeat/learn/" + urllib.parse.quote(self.message) + "/" + currentguildid + "/" + utils.get_guild_language(currentguildid) + "/"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),'This sentence has been saved.'), ephemeral = True)  
                    else:
                        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),'Error detected while saving this sentence.'), ephemeral = True)
                await session.close()  
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred) 
            
        
class PlayButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, content, message):
        super().__init__(style=discord.ButtonStyle.green, label="Play")
        self.content = content
        self.message = message
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
                    
            check_permissions(interaction)

            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            #view = discord.ui.View()
            #view.add_item(PlayButton(self.content, self.message))
            #view.add_item(StopButton())
            if voice_client:
                if not voice_client.is_connected():
                    await voice_client.channel.connect()
                    time.sleep(5)

                if voice_client is not None and voice_client.is_playing():
                    await voice_client.stop()

            #voice_client.play(FFmpegPCMAudioBytesIO(content, pipe=True), after=lambda e: logging.info(message))
            #await self.interaction.followup.edit_message(message_id=self.message.id,content=text, view = view)
            if voice_client is not None:
                voice_client.play(FFmpegPCMAudioBytesIO(self.content, pipe=True), after=lambda e: logging.info("play_button - " + self.message))
                await interaction.followup.send(self.message, ephemeral = True)
                
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)
            
class StopButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Stop")
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            check_permissions(interaction)
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            logging.info("stop - StopButton.callback.stop()")
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm interrupting the bot"), ephemeral = True)
            voice_client.stop()
                
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)
            
class AcceptButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Accept")
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            utils.update_guild_nsfw(get_current_guild_id(interaction.guild.id), 1)
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"You have enabled NSFW content."), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)
            
class DeclineButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Decline")
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            utils.update_guild_nsfw(get_current_guild_id(interaction.guild.id), 0)
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"You have disabled NSFW content."), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


intents = discord.Intents.all()
client = MyClient(intents=intents)


logging.info("Starting Discord Client...")

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

logging.getLogger('discord').setLevel(int(os.environ.get("LOG_LEVEL")))
logging.getLogger('discord.client').setLevel(int(os.environ.get("LOG_LEVEL")))
logging.getLogger('discord.gateway').setLevel(int(os.environ.get("LOG_LEVEL")))
logging.getLogger('discord.voice_client').setLevel(int(os.environ.get("LOG_LEVEL")))

discord.utils.setup_logging(level=int(os.environ.get("LOG_LEVEL")), root=False)

loops_dict = {}
kick_loops_dict = {}
populator_loops_dict = {}
generator_loops_dict = {}
#subito_loops_dict = {}
cvc_loops_dict = {}
available_voices = {}
#voiceclone_voices = {}
fakeyou_voices = {}
track_users_dict = {}

#async def display_loader(interaction, currentguildid, additional_msg=None):
#    with open('loading.gif', 'rb') as f:
#        picture = discord.File(f)
#        name = interaction.guild.me.nick if interaction.guild.me.nick else interaction.guild.me.name 
#        message = await utils.translate(currentguildid,"Someone used") + " **/" + interaction.command.name + "**\n"
#        message = "*" + message + await utils.translate(currentguildid,name+"'s working on it") + "*"
#        if additional_msg is not None:
#            message = message + additional_msg
#        load_message = await interaction.channel.send(message, file=picture)
#        return load_message

async def listvoices_api(language="it", filter=None):
    try:
        #global voiceclone_voices
        global fakeyou_voices
        global available_voices
        available_voices = {}
        #if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
        #    if voiceclone_voices is None or len(voiceclone_voices) == 0 or len(voiceclone_voices) == 2:
        #        url = get_voiceclone_api_url() + os.environ.get("API_VOICECLONE_PATH") + "/listvoices"
        #        try:
        #            async with aiohttp.ClientSession() as session:
        #                async with session.get(url) as response:
        #                    if (response.status == 200):
        #                        text = await response.text()
        #                        voiceclone_voices = json.loads(text)
        #                        available_voices.update(voiceclone_voices)
        #                await session.close()         
        #        except aiohttp.ClientConnectionError as e:
        #            pass
        #    else:
        #        available_voices.update(voiceclone_voices)
        if fakeyou_voices is None or len(fakeyou_voices) == 0 or len(fakeyou_voices) == 2:
            url = get_api_url() + os.environ.get("API_PATH_UTILS") + "/fakeyou/listvoices/" + language
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as response:
                        if (response.status == 200):
                            text = await response.text()
                            fakeyou_voices = json.loads(text)
                            available_voices.update(fakeyou_voices)
                    await session.close()
                except aiohttp.ClientConnectionError as e:
                    pass
        else:
            available_voices.update(fakeyou_voices)
        if (available_voices is not None and len(available_voices) > 0):
            if filter is not None:
                voice = None
                for key in available_voices:
                    if filter.lower() in key.lower():
                        voice = available_voices[key]
                return voice
            else:
                return available_voices
        else:
            available_voices = {}
            available_voices ["google"] = "google"
            available_voices ["Giorgio"] = "aws"
            return available_voices
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        return None

#def is_voiceclone_voice(voice_name):
#    global voiceclone_voices
#    for voice in voiceclone_voices:
#        if voice == voice_name:
#            return True
#    return False

async def rps_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    currentguildid=get_current_guild_id(interaction.guild.id)
    choices = await listvoices_api(language=utils.get_guild_language(currentguildid))
    choices = [app_commands.Choice(name=choice, value=choice) for choice in choices if current.lower() in choice.lower()][:25]
    return choices

async def rps_autocomplete_nofakeyou(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    currentguildid=get_current_guild_id(interaction.guild.id)
    choices = {}
    choices ["google"] = "google"
    choices ["Giorgio"] = "aws"
    choices = [app_commands.Choice(name=choice, value=choice) for choice in choices if current.lower() in choice.lower()][:25]
    return choices

def check_image_with_pil(path):
    try:
        Image.open(path)
    except IOError:
        return False
    return True


def get_languages_menu():

    options = []    
    options.append(app_commands.Choice(name="English",      value="en"))
    options.append(app_commands.Choice(name="French",       value="fr"))
    options.append(app_commands.Choice(name="German",       value="de"))
    options.append(app_commands.Choice(name="Italian",      value="it"))
    options.append(app_commands.Choice(name="Portuguese",   value="pt"))
    options.append(app_commands.Choice(name="Spanish",      value="es"))

    return options

optionslanguages = get_languages_menu()

def get_true_false_menu():

    options = []    
    options.append(app_commands.Choice(name="False", value="0"))
    options.append(app_commands.Choice(name="True",  value="1"))

    return options

truefalsemenu = get_true_false_menu()

audio_count_queue = 0

async def send_error(e, interaction, from_generic=False, is_deferred=False):
    logging.error(e)
    currentguildid=get_current_guild_id(interaction.guild.id)
    if isinstance(e, app_commands.CommandOnCooldown):
        try:
            dtc = "Spam " + await utils.translate(currentguildid,"detected.")
            spamarray=[]
            spamarray.append(dtc + " " + interaction.user.mention + " " + await utils.translate(currentguildid,"I am watching you."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + await utils.translate(currentguildid,"This doesn't make you a good person."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + await utils.translate(currentguildid,"I'm stupid but not annoying."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + await utils.translate(currentguildid,"Take your time."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + await utils.translate(currentguildid,"Keep calm."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + await utils.translate(currentguildid,"Do you also do this at your home?"))
            spamarray.append(dtc + " " + interaction.user.mention + " " + await utils.translate(currentguildid,"Why are you so anxious?"))
            spamarray.append(dtc + " " + interaction.user.mention + " " + await utils.translate(currentguildid,"I'll add you to the blacklist."))
            command = str(interaction.data['name'])
            cooldown = command + ' -> Cooldown: ' + str(e.cooldown.per) + '[' + str(round(e.retry_after, 2)) + ']s'

            spaminteractionmsg = utils.get_random_from_array(spamarray) + '\n' + cooldown
            if is_deferred:
                await interaction.followup.send(spaminteractionmsg, ephemeral = True)
            else:
                await interaction.response.send_message(spaminteractionmsg, ephemeral = True)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("[GUILDID : %s] %s %s %s", currentguildid, exc_type, fname, exc_tb.tb_lineno, exc_info=1)
            if is_deferred:
                await interaction.followup.send("Discord API Error, " + await utils.translate(currentguildid,"please try again later"), ephemeral = True)
            else:
                await interaction.response.send_message("Discord API Error, " + await utils.translate(currentguildid,"please try again later"), ephemeral = True)
    elif isinstance(e, ExcludedPermissionError):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("[GUILDID : %s] %s %s %s - %s", currentguildid, exc_type, fname, exc_tb.tb_lineno, e.args[0])
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
        lang_to_use = utils.get_guild_language(currentguildid)
        #url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"repeat/Vaffanculo%20Valeriu/google/"
        url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"repeat/learn/Disagio/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(lang_to_use) + "/"
                
        await do_play(url, interaction, currentguildid)

        if is_deferred:
            await interaction.followup.send(await utils.translate(currentguildid,"Disagio."), ephemeral = True)
        else:
            await interaction.response.send_message(await utils.translate(currentguildid,"Disagio."), ephemeral = True)
    elif isinstance(e, AdminPermissionError):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("[GUILDID : %s] %s %s %s - %s", currentguildid, exc_type, fname, exc_tb.tb_lineno, e.args[0])
        if is_deferred:
            await interaction.followup.send(await utils.translate(currentguildid,"You do not have permission to use this command."), ephemeral = True)
        else:
            await interaction.response.send_message(await utils.translate(currentguildid,"You do not have permission to use this command."), ephemeral = True)
    elif isinstance(e, PermissionError):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("[GUILDID : %s] %s %s %s - %s", currentguildid, exc_type, fname, exc_tb.tb_lineno, e.args[0])
        if is_deferred:
            await interaction.followup.send(await utils.translate(currentguildid,"You do not have permission to use this bot in this voice channel."), ephemeral = True)
        else:
            await interaction.response.send_message(await utils.translate(currentguildid,"You do not have permission to use this bot in this voice channel."), ephemeral = True)
    elif isinstance(e, NoChannelError):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("[GUILDID : %s] %s %s %s - %s", currentguildid, exc_type, fname, exc_tb.tb_lineno, e.args[0])
        if is_deferred:
            await interaction.followup.send(await utils.translate(currentguildid,"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(await utils.translate(currentguildid,"You must be connected to a voice channel to use this command"), ephemeral = True)
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("[GUILDID : %s] %s %s %s", currentguildid, exc_type, fname, exc_tb.tb_lineno, e.args[0])
        if is_deferred:
            await interaction.followup.send("Discord API Error, " + await utils.translate(currentguildid,"please try again later"), ephemeral = True)
        else:
            await interaction.response.send_message("Discord API Error, " + await utils.translate(currentguildid,"please try again later"), ephemeral = True)
    

def get_voice_client_by_guildid(voice_clients, guildid):
    for vc in voice_clients:
        if vc.guild.id == guildid:
            return vc
    return None

def check_permissions(interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        raise NoChannelError("NO CHANNEL ERROR - User [ NAME: " + str(interaction.user.name) + " - ID: " + str(interaction.user.id) + "] tried to use a command without being connected to a voice channel")

    perms = interaction.user.voice.channel.permissions_for(interaction.user.voice.channel.guild.me)
    if (not perms.speak):
        raise PermissionError("PERMISSION ERROR - User [NAME: " + str(interaction.user.name) + " - ID: " + str(interaction.user.id) + "] some excluded user tried to use a command")

    excluded_ids = json.loads(os.environ['EXCLUDED_IDS'])
    for excluded_id in excluded_ids:
        if (str(interaction.user.id) == str(excluded_id)):
            raise ExcludedPermissionError("EXCLUDED PERMISSION ERROR - User [NAME: " + str(interaction.user.name) + " - ID: " + str(interaction.user.id) + "] some excluded user tried to use a command")


def check_admin_permissions(interaction):
    if (not str(interaction.user.id) == str(os.environ.get("ADMIN_ID"))):
        raise AdminPermissionError("ADMIN PERMISSION ERROR - User [NAME: " + str(interaction.user.name) + " - ID: " + str(interaction.user.id) + "] tried to use a command who requires admin grants")
        

async def connect_bot_by_voice_client(voice_client, channel, guild, member=None):
    try:  
        if (voice_client and not voice_client.is_playing() and voice_client.channel and voice_client.channel.id != channel.id) or (not voice_client or not voice_client.channel):
            if member is not None and member.id is not None:
                if voice_client and voice_client.channel:
                    for memberSearch in voice_client.channel.members:
                        if member.id == memberSearch.id:
                            channel = voice_client.channel
                            break
            perms = channel.permissions_for(channel.guild.me)
            if (perms.administrator or perms.speak):
                if voice_client and voice_client.channel and voice_client.is_connected():
                    await voice_client.disconnect()
                    time.sleep(5)
                await channel.connect()
    except TimeoutError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    except ClientException as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def get_current_guild_id(guildid):
    if str(guildid) == str(os.environ.get("GUILD_ID")):
        return '000000' 
    else:
        return str(guildid)


async def do_play(url: str, interaction: discord.Interaction, currentguildid: str, ephermeal = True, name = None, show_save=False):
    try:
        #if defer:
        #    await interaction.response.defer(thinking=True, ephemeral = ephermeal)
        
        message = None
        voice = None
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if name is not None:
                    message = name
                elif "X-Generated-Text" in response.headers:
                    message = response.headers["X-Generated-Text"]
                if "X-Generated-Voice" in response.headers:
                    voice_code = response.headers["X-Generated-Voice"]
                    voice = {i for i in dic if dic[i]==available_voices}
                if (response.status == 200):
                    content = await response.content.read()
                    voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                    if not voice_client:
                        raise ClientException("voice_client is None")
                    if voice_client.is_playing():
                        voice_client.stop()
                        
                    voice_client.play(FFmpegPCMAudioBytesIO(content, pipe=True), after=lambda e: logging.info("do_play - " + message))
                    #voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=float(os.environ.get("BOT_VOLUME")))

                    view = discord.ui.View()
                    view.add_item(PlayButton(content, message))
                    view.add_item(StopButton())
                        
                    if "X-Generated-Response-Text" in response.headers:
                        message = response.headers["X-Generated-Response-Text"]
                    await interaction.followup.send(message, view = view, ephemeral = ephermeal)
                elif response.status == 204:
                    logging.info("[GUILDID : %s] do_play - Audio not found", str(get_current_guild_id(interaction.guild.id)))
                    message = await utils.translate(get_current_guild_id(interaction.guild.id),"I haven't found any audio for this text: " + message + ".")
                    await interaction.followup.send(message, ephemeral = ephermeal)
                elif response.status == 400:
                    logging.error("[GUILDID : %s] do_play - TTS Limit exceeded detected from APIs", str(get_current_guild_id(interaction.guild.id)))
                    message = message + "\n\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Error. Can't reproduce audio. The Generated TTS is longer than the maximum limit. ("+ str(int(os.environ.get("MAX_TTS_DURATION"))) +" seconds)")
                    await interaction.followup.send(message, ephemeral = ephermeal)
                elif response.status == 406:
                    logging.error("[GUILDID : %s] do_play - Blocked by filters detected from APIs", str(get_current_guild_id(interaction.guild.id)))
                    message = await utils.translate(get_current_guild_id(interaction.guild.id),"Error. The sentence contains a word that is blocked by filters.") + " ["+ str(message) +"]"
                    await interaction.followup.send(message, ephemeral = ephermeal)
                elif response.status == 424:
                    logging.error("[GUILDID : %s] do_play - FakeYou APIs are offline", str(get_current_guild_id(interaction.guild.id)))
                    message = ""
                    message = message + "\n" + await utils.translate(currentguildid,"I can't reproduce this audio because FakeYou isn't available at the moment. Please try again later.")
                    message = message + "\n" + await utils.translate(currentguildid,"Alternatively you can use one of these voices:") + " google, Giorgio"
                    message = message + "\n" + await utils.translate(currentguildid,"You can check the status of the FakeYou.com service and the TTS queue here:") + "https://fakeyou.com/"
                    await interaction.followup.send(message, ephemeral = ephermeal)
                else:
                    logging.error("[GUILDID : %s] do_play - Received bad response from APIs.", str(get_current_guild_id(interaction.guild.id)))
                    raise Exception("do_play - Error! - " + text)
            await session.close()  
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        exceptmsg = ""
        if message is not None:
            exceptmsg = exceptmsg + "\n- " + message
            exceptmsg = exceptmsg + "\n"
            exceptmsg = exceptmsg + "\n " + await utils.translate(currentguildid,"I can't reproduce this audio, the reasons can be:")
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"If you used a modified voice and an error occurred, could be that FakeYou APIs aren't available at the moment.")
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"Depending on the voice you choosed,") + " Permaban " + await utils.translate(currentguildid,"or ") + " Semiban " + await utils.translate(currentguildid,"from one of these services:") + " FakeYou TTS, Amazon Polly, Google TTS."
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"The generated TTS is longer than the maximum limit allowed ("+ str(int(os.environ.get("MAX_TTS_DURATION"))) +" seconds)")
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"The sentence contains a word blocked by filters")
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"An audio generation error occurred")
            exceptmsg = exceptmsg + "\n\n" + await utils.translate(currentguildid,"Remember that with too much spam the bot may be blocked for some minutes.") 
            exceptmsg = exceptmsg + "\n\n" + await utils.translate(currentguildid,"You can check the status of the FakeYou.com service and the TTS queue here:") + "https://fakeyou.com/"
            await self.interaction.followup.edit_message(message_id=self.message.id,content=self.exceptmsg)

class PlayAudioLoop:
    
    def __init__(self, guildid):
        for guild in client.guilds:
            if guild.id == guildid:
                self.guild = guild

    @tasks.loop(seconds=300)
    async def play_audio_loop(self):
        try:
            currentguildid = get_current_guild_id(str(self.guild.id))
            channelfound = None
            channeluserfound = None
            voice_client = get_voice_client_by_guildid(client.voice_clients, self.guild.id)                
            for channel in self.guild.voice_channels:
                perms = channel.permissions_for(channel.guild.me)
                if (perms.administrator or perms.speak):
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
                if voice_client and hasattr(voice_client, 'play') and voice_client.is_connected() and not voice_client.is_playing():
                    url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"random/random/" + currentguildid + "/" + utils.get_guild_language(currentguildid) + "/"
                    connector = aiohttp.TCPConnector(force_close=True)
                    async with aiohttp.ClientSession(connector=connector) as session:
                        async with session.get(url) as response:
                            if (response.status == 200):
                                content = await response.content.read()
                                text = response.headers["X-Generated-Text"]
                                message = 'play_audio_loop - random - ' + text
                                voice_client.play(FFmpegPCMAudioBytesIO(content, pipe=True), after=lambda e: logging.info(message))
                                #voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=float(os.environ.get("BOT_VOLUME")))
                        await session.close()  
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)


class KickMutedDeafenLoop:
    
    def __init__(self, guildid):
        for guild in client.guilds:
            if guild.id == guildid:
                self.guild = guild

    @tasks.loop(seconds=300)
    async def kick_muted_deafen_loop(self):
        try:         
            for channel in self.guild.voice_channels:
                perms = channel.permissions_for(channel.guild.me)
                #if (perms.administrator or perms.speak):
                for member in channel.members:
                    if not member.bot and (member.voice.self_deaf is True):
                        await member.move_to(None)
                            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

async def direct_play(voice_client, url):
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            if (response.status == 200):
                content = await response.content.read()
                message = 'direct_play - playing audio from url: ' + url
                voice_client.play(FFmpegPCMAudioBytesIO(content, pipe=True), after=lambda e: logging.info(message))
                #voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=float(os.environ.get("BOT_VOLUME")))
        await session.close()  

class PlayAudioWorker:
    
    def __init__(self, url, interaction, message, ephermeal = True, show_save = False):
        global audio_count_queue
        audio_count_queue = audio_count_queue + 1
        self.interaction = interaction
        self.url = url
        self.ephermeal = ephermeal
        self.show_save = show_save
        self.message = message

    @tasks.loop(seconds=0.1, count=1)
    async def play_audio_worker(self):
        global audio_count_queue
        currentguildid = get_current_guild_id(str(self.interaction.guild.id))
        try:   
            text = None
            voice = None
            connector = aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.url, timeout=7400) as response:
                    if "X-Generated-Text" in response.headers:
                        text = response.headers["X-Generated-Text"]
                    if "X-Generated-Voice" in response.headers:
                        voice_code = response.headers["X-Generated-Voice"]
                        voice = {i for i in dic if dic[i]==available_voices}
                    if (response.status == 200):
                        content = await response.content.read()

                        voice_client = get_voice_client_by_guildid(client.voice_clients, self.interaction.guild.id)            
                        if not voice_client:
                            raise ClientException("voice_client is None")
                        if voice_client.is_playing():
                            voice_client.stop()                               

                        view = discord.ui.View()
                        view.add_item(PlayButton(content, text))
                        view.add_item(StopButton())
                            
                        if not voice_client.is_connected():
                            await voice_client.channel.connect()
                            time.sleep(5)   

                        logmessage = 'play_audio_worker - ' + text
                        voice_client.play(FFmpegPCMAudioBytesIO(content, pipe=True), after=lambda e: logging.info(logmessage))
                        #voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=float(os.environ.get("BOT_VOLUME")))
                        await self.interaction.followup.edit_message(message_id=self.message.id,content=text, view = view)
                    
                    elif response.status == 204:
                        logging.info("[GUILDID : %s] do_play - Audio not found", str(get_current_guild_id(self.interaction.guild.id)))
                        exceptmsg = await utils.translate(get_current_guild_id(self.interaction.guild.id),"I haven't found any audio containing the requested text.")
                        await self.interaction.followup.edit_message(message_id=self.message.id,content=exceptmsg)
                    #elif response.status == 206:
                    #    logging.info("[GUILDID : %s] do_play - Other processes running in voice clone APIs", str(get_current_guild_id(self.interaction.guild.id)))
                    #    exceptmsg = await utils.translate(get_current_guild_id(self.interaction.guild.id),"The server GPU is busy processing other requests and AI Voices are not available at the moment, please try again later.")
                    #    await self.interaction.followup.edit_message(message_id=self.message.id,content=exceptmsg)
                    elif response.status == 400:
                        logging.error("[GUILDID : %s] do_play - TTS Limit exceeded detected from APIs", str(get_current_guild_id(self.interaction.guild.id)))
                        exceptmsg = text + "\n\n" + await utils.translate(get_current_guild_id(self.interaction.guild.id),"Error. Can't reproduce audio. The Generated TTS is longer than the maximum limit. ("+ str(int(os.environ.get("MAX_TTS_DURATION"))) +" seconds)")
                        await self.interaction.followup.edit_message(message_id=self.message.id,content=exceptmsg)
                    elif response.status == 406:
                        logging.error("[GUILDID : %s] do_play - Blocked by filters detected from APIs", str(get_current_guild_id(self.interaction.guild.id)))
                        exceptmsg = await utils.translate(get_current_guild_id(self.interaction.guild.id),"Error. The sentence contains a word that is blocked by filters.") + " ["+ str(text) +"]"
                        await self.interaction.followup.edit_message(message_id=self.message.id,content=exceptmsg)
                    elif response.status == 424:
                        logging.error("[GUILDID : %s] do_play - FakeYou APIs are offline", str(get_current_guild_id(self.interaction.guild.id)))
                        exceptmsg = ""
                        if text is not None:
                            exceptmsg = exceptmsg + "\n" + await utils.translate(currentguildid,"text") + ": " + text
                        if voice is not None: 
                            exceptmsg = exceptmsg + "\n" + await utils.translate(currentguildid,"Voice") + ": " + voice
                        exceptmsg = exceptmsg + "\n\n" + await utils.translate(currentguildid,"I can't reproduce this audio because FakeYou isn't available at the moment. Please try again later.")
                        exceptmsg = exceptmsg + "\n" + await utils.translate(currentguildid,"Alternatively you can use one of these voices:") + " google, Giorgio"
                        exceptmsg = exceptmsg + "\n" + await utils.translate(currentguildid,"You can check the status of the FakeYou.com service and the TTS queue here:") + "https://fakeyou.com/"
                        await self.interaction.followup.edit_message(message_id=self.message.id,content=exceptmsg)
                    else:
                        logging.error("[GUILDID : %s] do_play - Received bad response from APIs.", str(get_current_guild_id(self.interaction.guild.id)))
                        raise Exception("play_audio_worker - Error! - ")
                await session.close()

            
            #await self.interaction.followup.send(self.text, view = view, ephemeral = True)
            
        #    connector = aiohttp.TCPConnector(force_close=True)
        #    async with aiohttp.ClientSession(connector=connector) as session:
        #        async with session.get(self.url) as response:
        #            message = ""
        #            if "X-Generated-Text" in response.headers:
        #                message = response.headers["X-Generated-Text"]
        #            if (response.status == 200):
        #                content = await response.content.read()
        #                if not voice_client:
        #                    raise ClientException("voice_client is None")
        #                if voice_client.is_playing():
        #                    voice_client.stop()            
        #                view = discord.ui.View()
        #                view.add_item(PlayButton(content, message))
        #                view.add_item(StopButton())
        #                if self.show_save:
        #                    view.add_item(SaveButton(message))
        #                    
        #                if not voice_client.is_connected():
        #                    await voice_client.channel.connect()
        #                    time.sleep(5)
        #                discord.FFmpegPCMAudio(url, executable='C:/programs/ffmpeg.exe')
        #                voice_client.play(FFmpegPCMAudioBytesIO(content, pipe=True), after=lambda e: logging.info("play_audio_worker - " + message))
        #                if "X-Generated-Response-Text" in response.headers:
        #                    message = response.headers["X-Generated-Response-Text"]
        #                await self.interaction.followup.send(message, view = view, ephemeral = True)
        #            elif response.status == 204:
        #                logging.info("[GUILDID : %s] do_play - Audio not found", str(currentguildid))
        #                message = await utils.translate(currentguildid,"I haven't found any audio for this text: " + message + ".")
        #                await self.interaction.followup.send(message, ephemeral = self.ephermeal)
        #            elif response.status == 400:
        #                logging.error("[GUILDID : %s] do_play - TTS Limit exceeded detected from APIs", str(currentguildid))
        #                message = message + "\n\n" + await utils.translate(currentguildid,"Error. Can't reproduce audio. The Generated TTS is longer than the maximum limit. ("+ str(int(os.environ.get("MAX_TTS_DURATION"))) +" seconds)")
        #                await self.interaction.followup.send(message, ephemeral = self.ephermeal)
        #            elif response.status == 406:
        #                logging.error("[GUILDID : %s] do_play - Blocked by filters detected from APIs", str(currentguildid))
        #                message = await utils.translate(currentguildid,"Error. The sentence contains a word that is blocked by filters.") + " ["+ str(message) +"]"
        #                await self.interaction.followup.send(message, ephemeral = self.ephermeal)
        #            else:
        #                logging.error("[GUILDID : %s] do_play - Received bad response from APIs.", str(currentguildid))
        #                await self.interaction.followup.send(await utils.translate(currentguildid,"An audio generation error occurred.") + "\n" + await utils.translate(currentguildid,"If a modified voice has been selected, remember that with too much spam the bot may be blocked from FakeYou.com for some minutes.") + "\n" + await utils.translate(currentguildid,"You can check service status and the TTS queue here:") + "https://fakeyou.com/", ephemeral = self.ephermeal)                    
        #        await session.close()
        #except aiohttp.ClientConnectionError as e:
        #    exc_type, exc_obj, exc_tb = sys.exc_info()
        #    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        #    await self.interaction.followup.send(await utils.translate(currentguildid,"An audio generation error occurred.") + "\n" + await utils.translate(currentguildid,"If a modified voice has been selected, remember that with too much spam the bot may be blocked from FakeYou.com for some minutes.") + "\n" + await utils.translate(currentguildid,"You can check service status and the TTS queue here:") + "https://fakeyou.com/", ephemeral = self.ephermeal)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
            exceptmsg = ""
            if text is not None:
                exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"text") + ": " + text
            if voice is not None:
                exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"Voice") + ": " + voice
            exceptmsg = exceptmsg + "\n"
            exceptmsg = exceptmsg + "\n " + await utils.translate(currentguildid,"I can't reproduce this audio, the reasons can be:")
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"If you used a modified voice and an error occurred, could be that FakeYou APIs aren't available at the moment.")
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"Depending on the voice you choosed,") + " Permaban " + await utils.translate(currentguildid,"or ") + " Semiban " + await utils.translate(currentguildid,"from one of these services:") + " FakeYou TTS, Amazon Polly, Google TTS."
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"The generated TTS is longer than the maximum limit allowed ("+ str(int(os.environ.get("MAX_TTS_DURATION"))) +" seconds)")
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"The sentence contains a word blocked by filters")
            exceptmsg = exceptmsg + "\n- " + await utils.translate(currentguildid,"An audio generation error occurred")
            exceptmsg = exceptmsg + "\n\n" + await utils.translate(currentguildid,"Remember that with too much spam the bot may be blocked for some minutes.") 
            exceptmsg = exceptmsg + "\n\n" + await utils.translate(currentguildid,"You can check the status of the FakeYou.com service and the TTS queue here:") + " https://fakeyou.com/"
            await self.interaction.followup.edit_message(message_id=self.message.id,content=exceptmsg)
            
        if audio_count_queue > 0:
            audio_count_queue = audio_count_queue - 1

class PopulatorLoop:
    
    def __init__(self, guildid):  
        self.guildid = guildid

    @tasks.loop(minutes=int(240))
    async def populator_loop(self):
        try:
            currentguildid = get_current_guild_id(str(self.guildid))
            
            connector = aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(get_api_url()+os.environ.get("API_PATH_DATABASE")+"/audiodb/populate/4/" + currentguildid + "/" + utils.get_guild_language(currentguildid) + "/0" + "/") as response:
                    if (response.status == 200):
                        logging.info("populator_loop - " + str(response.text))
                    else:
                        logging.error("populator_loop - Error calling populator - status_code: " + str(response.status))
                await session.close()  
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)


class GeneratorLoop:
    
    def __init__(self, guildid):    
        self.guildid = guildid

    @tasks.loop(hours=168)
    async def generator_loop(self):
        try:
            currentguildid = get_current_guild_id(str(self.guildid))
            url = get_api_url() + os.environ.get("API_PATH_UTILS") + "/initgenerator/" + urllib.parse.quote(currentguildid) + "/" + utils.get_guild_language(currentguildid)
            
            connector = aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        logging.info(response.text)
                    else:
                        logging.error("Initializing generator on chatid " + currentguildid + " failed")
                await session.close()  
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)



async def get_queue_message(guildid: str):
    global audio_count_queue
    message = "\n\n"
    message = message + await utils.translate(guildid,"If the server is overloaded, it may take some time")
    message = message + "\n"
    message = message + "*CPU: " + str(psutil.cpu_percent()) + "% - RAM: " + str(psutil.virtual_memory()[2]) + "%*"
    message = message + "\n"
    message = message + "**" + await utils.translate(guildid,"TTS in queue:") + " " + str(0 if audio_count_queue == 0 else audio_count_queue - 1) + "**"
    return message

@tasks.loop(hours=6)
async def change_presence_loop():
    try:
        url = "https://steamspy.com/api.php?request=top100in2weeks"
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if (response.status == 200):                
                    text = await response.text()
                    json_games = json.loads(text)
                    game_array = []
                    for key, value in json_games.items():
                        game_array.append(value['name'])
                    game = str(utils.get_random_from_array(game_array))
                    logging.info("change_presence_loop - change_presence - game: " + game)
                    await client.change_presence(activity=discord.Game(name=game))
                else:
                    logging.error("change_presence_loop - steamspy API ERROR - status_code: " + str(response.status))
            await session.close()  
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

#class SubitoCheckLoop:
#    
#    def __init__(self, guildid):
#        logging.info("subito_check_loop - Starting")
#        self.guildid = guildid
#        for guild in client.guilds:
#            if guild.id == guildid:
#                self.guild = guild
#
#    @tasks.loop(seconds=60)
#    async def subito_check_loop(self):
#        try:
#            logging.info("subito_check_loop - Refreshing products")
#            new_prods_dict = {}
#            guildid = get_current_guild_id(self.guildid)
#            urls = await utils.select_subito_urls(guildid)
#            for url in urls:
#                urlapi = get_api_url() + "/subito/search"
#                params = {'url': url}
#                response = requests.post(urlapi, data=params, timeout=60)
#                if (response.status_code == 200):
#                    json_object = response.json()
#                    newquery = json_object['products']
#                    new_prods = []
#                    for newsingle in newquery:
#                        new_prods.append(newsingle)
#                    new_prods_dict[url] = new_prods
#
#            for key in new_prods_dict:
# 
#                keywo = key.replace("https://www.subito.it/", "")
#
#                pattern = r'[-/&?=]'
#                titles = re.split(pattern, keywo)
#
#                finaltitle = await utils.select_subito_channel(guildid, key) 
#
#                if finaltitle is not None:
#
#                    category = discord.utils.get(self.guild.categories, name=str(os.environ.get("SUBITO_IT_CATEGORY_NAME")))
#                    
#
#                    channel = discord.utils.get(self.guild.channels, name=finaltitle)
#                    if channel is None:
#                        channel = await self.guild.create_text_channel(finaltitle, category=category)
#
#                    if channel is not None:
#
#                        for prod in new_prods_dict[key]:
#                            cached = await utils.search_subito_db(guildid, str(key), str(prod['title']), str(prod['link']), str(prod['price']), str(prod['location']))
#                            if cached is None:
#                                await utils.insert_subito_db(guildid, str(key), str(prod['title']), str(prod['link']), str(prod['price']), str(prod['location']), str(prod['date']), str(prod['image']), '')
#                                
#                                message = "-----------------------------------" + "\n"
#                                message = message + str(key) + " - " + await utils.translate(guildid,"New product found") + "!\n" 
#                                message = message + "-----------------------------------" + "\n"
#                                message = message + str(prod['title']) + "\n" 
#                                if prod['price'] is not None:
#                                    message = message + await utils.translate(guildid,"Price") + ": " + str(prod['price']) + " €\n"  
#                                if prod['location'] is not None:
#                                    message = message + await utils.translate(guildid,"Location") + ": " + str(prod['location']) + "\n"  
#                                if prod['date'] is not None:
#                                    message = message + await utils.translate(guildid,"Date") + ": " + str(prod['date']) + "\n"  
#                                message = message + "Link" + ": " + str(prod['link'])
#                                if prod['image'] is not None:
#                                    async with aiohttp.ClientSession() as session:
#                                        async with session.get(prod['image']) as resp:
#                                            img = await resp.read()
#                                            with io.BytesIO(img) as file:
#                                                await channel.send(message, file=discord.File(file, "product.png"))
#                                else:
#                                    await channel.send(message)
#                                logging.info("subito_check_loop - Found new product")
#        except Exception as e:
#            exc_type, exc_obj, exc_tb = sys.exc_info()
#            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

@client.event
async def on_ready():
    try:
        logging.info(f'Logged in as {client.user} (ID: {client.user.id})')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

@client.event
async def on_connect():
    try:
        logging.info(f'Connected as {client.user} (ID: {client.user.id})')
        if not change_presence_loop.is_running():
            change_presence_loop.start()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

@client.event
async def on_guild_available(guild):

    try:

        currentguildid = get_current_guild_id(str(guild.id))                
        utils.check_exists_guild(currentguildid)        
        lang = utils.get_guild_language(currentguildid)
        await listvoices_api(language=lang, filter=None)  

    
        url = get_api_url() + os.environ.get("API_PATH_DATABASE") + "/backup/chatbot/" + urllib.parse.quote(currentguildid)
        
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if (response.status == 200):
                    logging.info(response.text)
                else:
                    logging.error("Backup on chatid " + currentguildid + " failed")
            await session.close()  

        url = get_api_url() + os.environ.get("API_PATH_UTILS") + "/init/" + urllib.parse.quote(currentguildid) + "/" + urllib.parse.quote(lang)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if (response.status != 200):
                    logging.error("Initializing chatterbot on chatid " + currentguildid + " failed")
                else:
                    text = await response.text()
                    logging.info(text)
            await session.close()    
        
        if guild.id not in loops_dict:
            loops_dict[guild.id] = PlayAudioLoop(guild.id)
            loops_dict[guild.id].play_audio_loop.start() 

        if guild.id not in kick_loops_dict:
            kick_loops_dict[guild.id] = KickMutedDeafenLoop(guild.id)
            kick_loops_dict[guild.id].kick_muted_deafen_loop.start() 

        if guild.id not in populator_loops_dict:
            populator_loops_dict[guild.id] = PopulatorLoop(guild.id)      
            populator_loops_dict[guild.id].populator_loop.start()  

        if guild.id not in generator_loops_dict:
            generator_loops_dict[guild.id] = GeneratorLoop(guild.id)
            generator_loops_dict[guild.id].generator_loop.start()


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

    try:
        client.tree.copy_global_to(guild=guild)
        await client.tree.sync(guild=guild)
        logging.info(f'Syncing commands to Guild (ID: {guild.id}) (NAME: {guild.name})')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

#@client.event
#async def on_presence_update(before, after):
#    try:
#        currentguildid = get_current_guild_id(str(after.guild.id))
#        global track_users_dic
#        if after.id in track_users_dict:
#            if str(before.status).lower() == "offline" and str(after.status).lower() != str(before.status).lower():
#                tracked_user = track_users_dict[after.id]
#                if tracked_user.guildid == "000000":
#                    name = str(after.name)   
#                    #if after.nick is not None:
#                    #    name = str(after.nick)
#                    #else:
#                    #    name = str(after.name)      
#                    updatemessage = name + " ha appena cambiato stato da " + str(before.status) + " a " + str(after.status) + "." 
#
#                    channel = client.get_channel(int(os.environ.get("MAIN_CHANNEL_ID")))
#                    await channel.send(updatemessage)
#
#                    updatemessage_wapp = "Discord Tracking: " + updatemessage    
#                    if tracked_user.whatsapp == "1":     
#                        url = "http://" + os.environ.get("WHATSAPP_HOST") + ":" + os.environ.get("WHATSAPP_PORT") + "/message/" + os.environ.get("WHATSAPP_CHATID") + "/" + urllib.parse.quote(updatemessage_wapp)
#
#                        connector = aiohttp.TCPConnector(force_close=True)
#
#                        async with aiohttp.ClientSession(connector=connector) as session:
#                            async with session.get(url) as response:
#                                if (response.status != 200):
#                                    logging.error("[GUILDID : %s] on_presence_update -> reset - Received bad response from APIs", str(guild.id))
#                            await session.close()  
#
#    except Exception as e:
#        exc_type, exc_obj, exc_tb = sys.exc_info()
#        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

@client.event
async def on_voice_state_update(member, before, after):
    try:
        if member.bot and member.id == client.user.id:
            voice_client = get_voice_client_by_guildid(client.voice_clients, member.guild.id)
            if voice_client:
                if voice_client.is_playing():
                    voice_client.stop()
                if before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
                    await voice_client.disconnect()
        elif member.guild.id in loops_dict and loops_dict[member.guild.id].play_audio_loop.is_running():
            if before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
                voice_client = get_voice_client_by_guildid(client.voice_clients, member.guild.id)

                perms = after.channel.permissions_for(after.channel.guild.me)
                if (perms.administrator or perms.speak):
                    #if voice_client:
                    #    await voice_client.disconnect()
                    await connect_bot_by_voice_client(voice_client, after.channel, None, member=member)
                    if voice_client is not None:
                        if not voice_client.is_connected():
                            await voice_client.channel.connect()
                        time.sleep(1)
                        if voice_client.is_playing():
                            voice_client.stop()
                        login_audios = get_login_audios()
                        url_audio = login_audios[str(member.id)] if login_audios is not None and str(member.id) in login_audios else "https://www.myinstants.com/media/sounds/buongiorno-salvini.mp3"
                        await direct_play(voice_client, url_audio)
            elif before.channel is None and after.channel is not None:
                voice_client = get_voice_client_by_guildid(client.voice_clients, member.guild.id)
                perms = after.channel.permissions_for(after.channel.guild.me)
                if (perms.administrator or perms.speak):
                    await connect_bot_by_voice_client(voice_client, after.channel, None, member=member)
                    if voice_client is not None:
                        if not voice_client.is_connected():
                            await voice_client.channel.connect()
                        time.sleep(1)   
                        if voice_client.is_playing():
                            voice_client.stop()
                        login_audios = get_login_audios()
                        url_audio = login_audios[str(member.id)] if login_audios is not None and str(member.id) in login_audios else "https://www.myinstants.com/media/sounds/buongiorno-salvini.mp3"
                        await direct_play(voice_client, url_audio)
            elif after.channel is None and before.channel is not None:
                voice_client = get_voice_client_by_guildid(client.voice_clients, member.guild.id)
                perms = before.channel.permissions_for(before.channel.guild.me)
                if (perms.administrator or perms.speak):
                    await connect_bot_by_voice_client(voice_client, before.channel, None, member=member)
                    if voice_client is not None:
                        if not voice_client.is_connected():
                            await voice_client.channel.connect()
                        time.sleep(1)   
                        if voice_client.is_playing():
                            voice_client.stop()
                        logout_audios = get_logout_audios()
                        url_audio = logout_audios[str(member.id)] if logout_audios is not None and str(member.id) in logout_audios else "https://www.myinstants.com/media/sounds/buonasera-salvini.mp3"
                        await direct_play(voice_client, url_audio)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

async def get_disclaimer(currentguildid):
    message = "**DISCLAIMER**"
    message = message + "\n" + await utils.translate(currentguildid,"This Bot saves data in its encrypted database, used for the auto-talking feature.")
    message = message + "\n" + await utils.translate(currentguildid,"Please don't write sensitive data, you have been warned.")
    message = message + "\n" + await utils.translate(currentguildid,"The developer takes no responsibility of what the bot generates or on what the users write using the bot commands.")
    message = message + "\n\n" + await utils.translate(currentguildid,"I am a dumb Bot and I don't want to cause any problem.")
    message = message + "\n\n" + await utils.translate(currentguildid,"The default language is English, if you want to change language ask an Administrator to do so with the command:") + " /language."
    message = message + "\n\nNSFW => [/insult] [/curse]"        
    message = message + "\n" + await utils.translate(currentguildid,"Two commands delivers NSFW content. An administrator must approve NSFW content using the command") + " /accept."
    return message
    
@client.event
async def on_guild_join(guild):
    logging.info(f'Guild joined (ID: {guild.id})')
    utils.check_exists_guild(get_current_guild_id(str(guild.id)))
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)
    logging.info(f'Syncing commands to Guild (ID: {guild.id}) (NAME: {guild.name})')

    #await guild.system_channel.send(await get_disclaimer(get_current_guild_id(guild.id)))

@client.event
async def on_guild_remove(guild):
    try:
        if str(interaction.guild.id) != str(os.environ.get("GUILD_ID")):
            utils.delete_guild(str(guild.id))
            url = get_api_url() + os.environ.get("API_PATH_DATABASE") + "/reset/" +urllib.parse.quote(str(guild.id)) + "/"
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url) as response:
                    if (response.status != 200):
                        logging.error("[GUILDID : %s] on_guild_remove -> reset - Received bad response from APIs", str(guild.id))
                await session.close()  
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

#async def on_listen_finish(sink: listening.AudioFileSink, exc=None, channel=None):
#    await sink.convert_files(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    if channel is not None:
#        for file in sink.output_files.values():
#            await send_audio_file(channel, file)
#
#    if exc is not None:
#        raise exc

#@client.tree.command()
#@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
#async def listen(interaction: discord.Interaction):
#    """Begin listening to voice."""
#    is_deferred=True
#    try:
#        await interaction.response.defer(thinking=True, ephemeral=True)
#        check_permissions(interaction)
#        file_format = "mp3"
#        
#        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
#        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
#
#        if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
#            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
#        else:   
#            if voice_client.is_listen_receiving():
#                return await interaction.response.send_message("Already recording.", ephemeral = True)
#            if voice_client.is_listen_cleaning():
#                return await interaction.response.send_message("Currently busy cleaning... try again in a second.", ephemeral = True)
#            voice_client.listen(
#                listening.AudioFileSink(FILE_FORMATS[file_format], "/tmp/discord-tts-bot-discord/"),
#                process_pool,
#                after=on_listen_finish,
#                channel=interaction.channel
#            )
#            await interaction.response.send_message("Started recording.", ephemeral = True)
#         
#    except Exception as e:
#        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def join(interaction: discord.Interaction):
    """Join channel."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        if voice_client:       
            await voice_client.disconnect()
            time.sleep(5)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm joining the voice channel"), ephemeral = True)
         
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def leave(interaction: discord.Interaction):
    """Leave channel"""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        if voice_client:       
            await voice_client.disconnect()     
            if loops_dict[interaction.guild.id].play_audio_loop.is_running():
                loops_dict[interaction.guild.id].play_audio_loop.stop()
                logging.info("disable - play_audio_loop.stop()")
                loops_dict[interaction.guild.id].play_audio_loop.cancel()
                logging.info("disable - play_audio_loop.cancel()")
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm leaving the voice channel"), ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm not connected to any voice channel"), ephemeral = True)       
         
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to repeat")
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.autocomplete(voice=rps_autocomplete)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def speak(interaction: discord.Interaction, text: str, voice: str = "random"):
    """Repeat a sentence"""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        else:

            currentguildid = get_current_guild_id(interaction.guild.id)
            
            lang_to_use = utils.get_guild_language(currentguildid)

            if voice != "random":
                voice = await listvoices_api(language=lang_to_use, filter=voice)
            else:
                voice = randompy.choice(['google', 'aws'])

            if voice is not None:
                #if is_voiceclone_voice(voice):
                #    if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")) and str(interaction.user.id) == str(os.environ.get("ADMIN_ID")) and interaction.user.guild_permissions.administrator:
                #        url = get_voiceclone_api_url+os.environ.get("API_VOICECLONE_PATH")+urllib.parse.quote(str(voice))+"/"+urllib.parse.quote(str(text))+"/"
                #    else:
                #        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Users allowed to use this voice:") + " " + str(interaction.user.name), ephemeral = True)
                #else:
                blocked = False
                blocktxt = os.path.join(dirname(__file__) + '/config/blocked.txt')
                if os.path.isfile(blocktxt):
                    with open(blocktxt) as blfile:
                        for line in blfile:
                            if line.strip().lower() in str(text).strip().lower():
                                blocked = True
                                break
                url = None
                if blocked:
                    url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(text))+"/" + urllib.parse.quote(voice) + "/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(lang_to_use)
                else:
                    url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"repeat/learn/user/"+urllib.parse.quote(str(interaction.user.name))+"/"+urllib.parse.quote(str(text))+"/" + urllib.parse.quote(voice) + "/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(lang_to_use) + "/"
                        
                if url is not None:
                    message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm starting to generate the audio for:") + " **" + text + "**" + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
                    worker = PlayAudioWorker(url, interaction, message)
                    worker.play_audio_worker.start()
                else:
                    await interaction.followup.send("Discord API Error, " + await utils.translate(get_current_guild_id(interaction.guild.id),"please try again later"), ephemeral = True)      
            else:
                await interaction.followup.send("Discord API Error, " + await utils.translate(get_current_guild_id(interaction.guild.id),"please try again later"), ephemeral = True)      
                 
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def wikipedia(interaction: discord.Interaction, text: str):
    """Search something on wikipedia"""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        elif voice_client:

            currentguildid = get_current_guild_id(interaction.guild.id)
            url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"search/"+urllib.parse.quote(str(text))+"/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid)) + "/"
            
            message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm searching on wikipedia:"), + " **" + text + "**" + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
            worker = PlayAudioWorker(url, interaction, message)
            worker.play_audio_worker.start()
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The bot is not ready yet or another user is already using another command.") +"\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)            
        
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.rename(audio='audio')
@app_commands.describe(audio="The audio (mp3 or wav)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def audio(interaction: discord.Interaction, audio: discord.Attachment):
    """Audio playback from the input audio"""
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)        
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        elif voice_client:            
            if not utils.allowed_audio(audio.filename):
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The file extension is not valid."), ephemeral = True)     
            else:
                audiofile = await audio.to_file()            
                voice_client.play(FFmpegPCMAudioBytesIO(audiofile.fp.read(), pipe=True), after=lambda e: logging.info(urllib.parse.quote(str(interaction.user.name)) + " requested an audio playback from file"))
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Done! I'm starting the audio playback!"), ephemeral = True)   
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The bot is not ready yet or another user is already using another command.") +"\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)            
        
    except Exception as e:
        await send_error(e, interaction)

#@client.tree.command()
#@app_commands.rename(text='text')
#@app_commands.describe(text="The text to search")
#@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
#async def bard(interaction: discord.Interaction, text: str):
#    """Ask something to Google Bard"""
#    is_deferred=True
#    try:
#        await interaction.response.defer(thinking=True, ephemeral=True)
#        check_permissions(interaction)
#        
#        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
#        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
#
#        
#        if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
#            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
#        elif voice_client:
#            currentguildid = get_current_guild_id(interaction.guild.id)
#
#            url = get_api_url() + os.environ.get("API_PATH_TEXT") + "askgooglebard/" + urllib.parse.quote(str(text)) + "/"
#            async with aiohttp.ClientSession() as session:
#                async with session.get(url) as response:
#                    if (response.status == 200):
#                        message = await response.text()
#                        text = response.headers["X-Generated-Text"].encode('latin-1').decode('utf-8')
#                        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I haven't found any results "), ephemeral = True) 
#                        url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid)) + "/"
#                        await do_play(url, interaction, currentguildid, name=message)      
#                    else:
#                        await interaction.followup.send("Google Bard Error" + "\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later"), ephemeral = True)        
#                await session.close() 
#        else:
#            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The bot is not ready yet or another user is already using another command.") +"\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)
#         
#    except Exception as e:
#        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="the sentence to ask")
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.autocomplete(voice=rps_autocomplete)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def ask(interaction: discord.Interaction, text: str, voice: str = "google"):
    """Ask something."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        
        if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        else:
            currentguildid = get_current_guild_id(interaction.guild.id)

            if voice != "google":
                voice = await listvoices_api(language=lang_to_use, filter=voice)

            if voice is not None:
                url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"ask/user/"+urllib.parse.quote(str(text))+"/"+urllib.parse.quote(str(interaction.user.name))+"/1/" + urllib.parse.quote(voice) + "/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid)) + "/"
                
                message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm looking for an answer to:") + " **" + text + "**" + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
                worker = PlayAudioWorker(url, interaction, message)
                worker.play_audio_worker.start()
            else:
                await interaction.followup.send("Discord API Error, " + await utils.translate(get_current_guild_id(interaction.guild.id),"please try again later"), ephemeral = True) 
                   
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def generate(interaction: discord.Interaction):
    """Generate a random sentence."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        

        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        
        if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        else:
            currentguildid = get_current_guild_id(interaction.guild.id)
            url = get_api_url() + os.environ.get("API_PATH_UTILS") + "/sentences/generate/" + urllib.parse.quote(currentguildid) + "/0"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        text = await response.text()
                        url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                        
                        message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm generating a random text")  + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
                        worker = PlayAudioWorker(url, interaction, message)
                        worker.play_audio_worker.start()
                    else:
                        logging.error("[GUILDID : %s] generate - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)))
                        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),'Error. The generator database is still empty, try again later.\nNOTE: If you just invited the bot, this feature will be available in 12 hours if you continue to use the "speak" command.'), ephemeral = True)     
                await session.close() 
                
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def story(interaction: discord.Interaction):
    """Generate a random story."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)


        if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        else:
            currentguildid = get_current_guild_id(interaction.guild.id)
            url = get_api_url() + os.environ.get("API_PATH_UTILS") + "/paragraph/generate/" + urllib.parse.quote(currentguildid) + "/"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        text = await response.text()
                        url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid) + "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                        
                        message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm generating a random story")  + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
                        worker = PlayAudioWorker(url, interaction, message)
                        worker.play_audio_worker.start()
                    else:
                        logging.error("[GUILDID : %s] story - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)))
                        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),'Error. The generator database is still empty, try again later.\nNOTE: If you just invited the bot, this feature will be available in 12 hours if you continue to use the "speak" command.'), ephemeral = True)         
                await session.close() 
               
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)



@client.tree.command()
@app_commands.rename(member='member')
@app_commands.describe(member="The user to insult")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def insult(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Insult someone"""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        currentguildid = get_current_guild_id(interaction.guild.id)
        if utils.get_guild_nsfw(currentguildid) == 0:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"An Administrator must approve NSFW content on this server. Ask him to use the command:") + " /accept", ephemeral = True)
        else:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
            else:
                insulturl=get_api_url()+os.environ.get("API_PATH_AUDIO")+"insult"
                if member:
                    name = None
                    if member.nick is not None:
                        name = str(member.nick)
                    else:
                        name = str(member.name)
                    insulturl=insulturl +"?text="+urllib.parse.quote(name) + "&chatid="+urllib.parse.quote(get_current_guild_id(interaction.guild.id))
                else:
                    insulturl=insulturl +"?chatid="+urllib.parse.quote(get_current_guild_id(interaction.guild.id)) + "&lang=" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                
                message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm generating a random insult")  + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
                worker = PlayAudioWorker(insulturl, interaction, message)
                worker.play_audio_worker.start()
         
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)



@client.tree.command()
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.autocomplete(voice=rps_autocomplete)
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def random(interaction: discord.Interaction, voice: str = "random", text: str = ""):
    """Say a random sentence"""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        elif voice_client:
            
            currentguildid = get_current_guild_id(interaction.guild.id)                

            if voice != "random":
                voice = await listvoices_api(language=utils.get_guild_language(currentguildid), filter=voice)

            if voice is not None:
                url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"random/" + urllib.parse.quote(voice) + "/" + urllib.parse.quote(currentguildid) + "/" + utils.get_guild_language(currentguildid) + "/"
                if text != "":
                    url = url + text
                message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm searching a random sentence")  + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
                
                worker = PlayAudioWorker(url, interaction, message)
                worker.play_audio_worker.start()
            else:
                await interaction.followup.send("Discord API Error, " + await utils.translate(get_current_guild_id(interaction.guild.id),"please try again later"), ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The bot is not ready yet or another user is already using another command.") +"\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)

         
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)



@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def curse(interaction: discord.Interaction):
    """Curse."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://bestemmie.org') as response:
                if (response.status != 200):
                    await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Impossible to use this command") + ": API 'http://bestemmie.org' Status = OFFLINE", ephemeral = True)
                else:
                    try:
                        currentguildid = get_current_guild_id(interaction.guild.id)
                        if utils.get_guild_nsfw(currentguildid) == 0:
                            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"An Administrator must approve NSFW content on this server. Ask him to use the command:") + " /accept", ephemeral = True)
                        else:
                            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
                            else:
                                

                                url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"curse/"+urllib.parse.quote(currentguildid)+ "/" + utils.get_guild_language(currentguildid) + "/"
                                message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm creating a random blasphemy")  + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
                            
                                worker = PlayAudioWorker(url, interaction, message)
                                worker.play_audio_worker.start()
                    except Exception as e:
                        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)
            await session.close() 
              
    except Exception as e:        
        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Impossible to use this command") + ": API 'http://bestemmie.org' Status = OFFLINE", ephemeral = True)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def restart(interaction: discord.Interaction):
    """Restart bot."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")) and str(interaction.user.id) == str(os.environ.get("ADMIN_ID")):
            if interaction.user.guild_permissions.administrator:
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I am restarting the bot."), ephemeral = True)
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def delete(interaction: discord.Interaction, text: str):
    """Delete sentences by text."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        currentguildid = get_current_guild_id(interaction.guild.id)

        async with aiohttp.ClientSession() as session:
            async with session.get(get_api_url() + os.environ.get("API_PATH_DATABASE") + "/download/sentences/" + urllib.parse.quote(currentguildid)) as response:
                if (response.status == 200):

                    textdl = await response.text()

                    #nameout = str(interaction.guild.name) + "_" + str(client.user.name)  + "_Backup_"  + datetime.now().strftime("%d%m%Y_%H%M%S") + ".txt"
                    nameout = "trainfile.txt"

                    filepath = os.environ.get("TMP_DIR") + nameout
                    with open(filepath, 'w') as filewrite:
                        filewrite.write(textdl)            
                        #for line in response.text.splitlines():
                        #    filewrite.write(line)            
                        #    filewrite.write("\n")            


                        #await interaction.followup.send("Bot Backup.", file=discord.File(filename=nameout, fp=open(filepath, "rb")), ephemeral = True) 
                        
                        #channel = client.get_channel(int(os.environ.get("BACKUP_CHANNEL_ID")))
                        #await channel.send(await utils.translate(currentguildid,"Someone deleted the word: " + text))
                        #await channel.send(await utils.translate(currentguildid,"Here's the backup."), file = discord.File(filename=nameout, fp=open(filepath, "rb")))

                        async with aiohttp.ClientSession() as session2:
                            async with session2.get(get_api_url() + os.environ.get("API_PATH_DATABASE") + "/forcedelete/bytext/" + urllib.parse.quote(text) + "/" + urllib.parse.quote(currentguildid)) as response:
                                if (response.status == 200):
                                    #text = await response.text()
                                    #await interaction.followup.send(text, ephemeral = True) 
                                    text = await utils.translate(currentguildid,"Someone deleted the word: " + text) + ". " + await utils.translate(currentguildid,"Here's the backup.")

                                    await interaction.followup.send(text, file=discord.File(filename=nameout, fp=open(filepath, "rb")), ephemeral = True) 
                                elif (response.status == 500):
                                    await interaction.followup.send("Temporarily disabled. Other processes are running in the background, you need to wait for the end of their execution.", ephemeral = True) 
                                else:
                                    logging.error("[GUILDID : %s] forcedelete/bytext - Received bad response from APIs", str(currentguildid))
                                    await interaction.followup.send(await utils.translate(currentguildid,"Error."), ephemeral = True)     
                            await session.close() 
                        
                    os.remove(filepath)      
                    
                else:
                    logging.error("[GUILDID : %s] download/sentences - Received bad response from APIs", str(currentguildid))
                    await interaction.followup.send(await utils.translate(currentguildid,"Error."), ephemeral = True)     
            await session.close() 
        
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def download(interaction: discord.Interaction):
    """Download sentences."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        if interaction.user.guild_permissions.administrator:
            currentguildid = get_current_guild_id(interaction.guild.id)

            async with aiohttp.ClientSession() as session:
                async with session.get(get_api_url() + os.environ.get("API_PATH_DATABASE") + "/download/sentences/" + urllib.parse.quote(currentguildid)) as response:
                    if (response.status == 200):

                        text = await response.text()

                        #nameout = str(interaction.guild.name) + "_" + str(client.user.name)  + "_Backup_"  + datetime.now().strftime("%d%m%Y_%H%M%S") + ".txt"
                        nameout = "trainfile.txt"

                        filepath = os.environ.get("TMP_DIR") + nameout
                        with open(filepath, 'w') as filewrite:
                            filewrite.write(text)            
                            #for line in response.text.splitlines():
                            #    filewrite.write(line)            
                            #    filewrite.write("\n")            


                            #await interaction.followup.send("Bot Backup.", file= 
                            
                            #channel = client.get_channel(int(os.environ.get("BACKUP_CHANNEL_ID")))
                            #await channel.send(await utils.translate(currentguildid,"Someone generated a Backup."), file = discord.File(filename=nameout, fp=open(filepath, "rb")))
                                                
                            await interaction.followup.send("Bot Backup.", file=discord.File(filename=nameout, fp=open(filepath, "rb")), ephemeral = True) 

                        os.remove(filepath)
                        
                        #await interaction.followup.send("Done.", ephemeral = True) 
                    else:
                        logging.error("[GUILDID : %s] download/sentences - Received bad response from APIs", str(currentguildid))
                        await interaction.followup.send(await utils.translate(currentguildid,"Error."), ephemeral = True)     
                await session.close() 
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def stop(interaction: discord.Interaction):
    """Stop playback."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        logging.info("stop - voice_client.stop()")
        await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm interrupting the bot"), ephemeral = True)
        voice_client.stop()
            
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

    

@client.tree.command()
@app_commands.rename(name='name')
@app_commands.describe(name="New bot nickname (32 chars limit)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def rename(interaction: discord.Interaction, name: str):
    """Rename bot."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        
        if len(name) < 32:
            currentguildid = get_current_guild_id(interaction.guild.id)
            
            message = await utils.translate(currentguildid,"You renamed me to") + ' "'+name+'"'
            #name = name + " [" + utils.get_guild_language(currentguildid) + "]"
            await interaction.guild.me.edit(nick=name)
            await interaction.followup.send(message, ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"My name cannot be longer than 32 characters"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(image='image')
@app_commands.describe(image="New bot avatar")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def avatar(interaction: discord.Interaction, image: discord.Attachment):
    """Change bot avatar."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            imgfile=await image.to_file()
            filepath = os.environ.get("TMP_DIR") + "/avatar_guild_" + str(interaction.guild.id) + pathlib.Path(imgfile.filename).suffix
            with open(filepath, 'wb') as file:
                file.write(imgfile.fp.getbuffer())
            if check_image_with_pil(filepath):
                with open(filepath, 'rb') as f:
                    image = f.read()
                await client.user.edit(avatar=image)
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The image has been changed"), ephemeral = True)
                os.remove(filepath)
            else:
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"This file type is not supported"), ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.rename(language='language')
@app_commands.describe(language="New bot language")
@app_commands.choices(language=optionslanguages)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def language(interaction: discord.Interaction, language: app_commands.Choice[str]):
    """Change bot language."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        currentguildid = get_current_guild_id(interaction.guild.id)
        if interaction.user.guild_permissions.administrator:

            utils.update_guild_lang(currentguildid, language.value)

            await interaction.followup.send(await utils.translate(currentguildid,"Bot language changed to ") + ' "'+language.name+'"', ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(currentguildid,"Only administrators can use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


#@client.tree.command()
#@app_commands.rename(member='member')
#@app_commands.describe(member="The user to track")
#@app_commands.rename(whatsapp='whatsapp')
#@app_commands.describe(whatsapp="Notify user tracking on whatsapp?")
#@app_commands.choices(whatsapp=truefalsemenu)
#@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
#async def trackuser(interaction: discord.Interaction, member: discord.Member, whatsapp: app_commands.Choice[str]):
#    """Track a user."""
#    is_deferred=True
#    try:
#        await interaction.response.defer(thinking=True, ephemeral=True)
#        currentguildid = get_current_guild_id(interaction.guild.id)
#        global track_users_dict
#
#        name = ""   
#        if member.nick is not None:
#            name = str(member.nick)
#        else:
#            name = str(member.name)  
#        track_users_dict[member.id] = TrackUser(name, currentguildid, whatsapp.value)
#
#
#
#        await interaction.followup.send(await utils.translate(currentguildid,"I am starting to monitor the user:") + " " + name + ".", ephemeral = True)
#    except Exception as e:
#        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

#@client.tree.command()
#@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
#async def untrackall(interaction: discord.Interaction):
#    """Untrack all users."""
#    is_deferred=True
#    try:
#        await interaction.response.defer(thinking=True, ephemeral=True)
#        currentguildid = get_current_guild_id(interaction.guild.id)
#        global track_users_dict
#        track_users_dict = {}
#        await interaction.followup.send(await utils.translate(currentguildid,"I am not monitoring anyone anymore."), ephemeral = True)
#    except Exception as e:
#        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to convert")
@app_commands.rename(language_to='language_to')
@app_commands.describe(language_to="The language to convert to")
@app_commands.choices(language_to=optionslanguages)
@app_commands.rename(language_from='language_from')
@app_commands.describe(language_from="The language to convert from")
@app_commands.choices(language_from=optionslanguages)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def translate(interaction: discord.Interaction, text: str, language_to: app_commands.Choice[str], language_from: app_commands.Choice[str] = "xx"):
    """Translate a sentence and repeat it"""
    is_deferred=True
    
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        else:

            currentguildid = get_current_guild_id(interaction.guild.id)

            lang_to_use_from = ""
            if hasattr(language_from, 'name'):
                lang_to_use_from = language_from.value
            else:
                lang_to_use_from = utils.get_guild_language(currentguildid)

            

            async with aiohttp.ClientSession() as session:
                async with session.get(get_api_url() + os.environ.get("API_PATH_TEXT") + "translate/" + urllib.parse.quote(lang_to_use_from) + "/" + urllib.parse.quote(language_to.value) + "/" + urllib.parse.quote(text) + "/" + urllib.parse.quote(currentguildid) + "/") as response:
                    if (response.status == 200):
                        translated_text = await response.text()
                        url = get_api_url()+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(translated_text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(language_to.value) + "/"
                        
                        message:discord.Message = await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I'm translating:") + " **" + text + "**" + await get_queue_message(get_current_guild_id(interaction.guild.id)), ephemeral = True)
                        worker = PlayAudioWorker(url, interaction, message)
                        worker.play_audio_worker.start()
                    else:
                        logging.error("[GUILDID : %s] translate - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)))
                        await interaction.followup.send("API Timeout, " + await utils.translate(currentguildid,"please try again later"), ephemeral = True)
                await session.close() 
                      
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.rename(url='url')
@app_commands.describe(url="Youtube link (Must match https://www.youtube.com/watch?v=1abcd2efghi)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def youtube(interaction: discord.Interaction, url: str):
    """Play a youtube link"""
    is_deferred=True
    
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
        
        if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        elif voice_client:

            if "watch?v=" in url:
                currentguildid = get_current_guild_id(interaction.guild.id)

                urlapi = get_api_url()+os.environ.get("API_PATH_MUSIC")+"youtube/get/"+(url.split("watch?v=",1)[1])+"/"+urllib.parse.quote(currentguildid)
                await do_play(urlapi, interaction, currentguildid, ephermeal = False)
            else:
                await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"URL must match something like https://www.youtube.com/watch?v=1abcd2efghi"), ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The bot is not ready yet or another user is already using another command.") +"\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)
           
                
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def enable(interaction: discord.Interaction):
    """Enable auto talking feature."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        currentguildid = get_current_guild_id(interaction.guild.id)
        if not loops_dict[interaction.guild.id].play_audio_loop.is_running():
            loops_dict[interaction.guild.id].play_audio_loop.start()
            logging.info("enable - play_audio_loop.start()")
            await interaction.followup.send(await utils.translate(currentguildid,"I'm enabling the auto talking feature"), ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(currentguildid,"The auto talking feature is already enabled"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred = is_deferred)
        

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def disable(interaction: discord.Interaction):
    """Disable auto talking feature."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        currentguildid = get_current_guild_id(interaction.guild.id)
        if loops_dict[interaction.guild.id].play_audio_loop.is_running():
            loops_dict[interaction.guild.id].play_audio_loop.stop()
            logging.info("disable - play_audio_loop.stop()")
            loops_dict[interaction.guild.id].play_audio_loop.cancel()
            logging.info("disable - play_audio_loop.cancel()")
            await interaction.followup.send(await utils.translate(currentguildid,"I'm disabling the auto talking feature"), ephemeral = True)
        else:
            await interaction.followup.send(await utils.translate(currentguildid,"The auto talking feature is already disabled"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.rename(seconds='seconds')
@app_commands.describe(seconds="Timeout seconds (Min 30 - Max 1200)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def timer(interaction: discord.Interaction, seconds: int):
    """Change the timer for the auto talking feature."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        currentguildid = get_current_guild_id(interaction.guild.id)
        if seconds < 60 or seconds > 1200:
            await interaction.followup.send(await utils.translate(currentguildid,"Seconds must be greater than 60 and lower than 1200"), ephemeral = True)
        else:
            loops_dict[interaction.guild.id].play_audio_loop.change_interval(seconds=seconds)
            logging.info("timer - play_audio_loop.change_interval(seconds="+str(seconds)+")")
            await interaction.followup.send(await utils.translate(currentguildid,"I'm setting a " + str(seconds) + " seconds timer for the auto talking feature"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)



#@client.tree.command()
#@app_commands.rename(link='link')
#@app_commands.describe(link="Subito.it link")
#@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
#async def add_subito_url(interaction: discord.Interaction, link: str):
#    """Add a new Subito.it link."""
#    is_deferred=True
#    try:
#        await interaction.response.defer(thinking=True, ephemeral=True)
#        check_permissions(interaction)
#        currentguildid = get_current_guild_id(interaction.guild.id) 
#        
# 
#        keywo = link.replace("https://www.subito.it/", "")
#
#        pattern = r'[-/&?=]'
#        titles = re.split(pattern, keywo)
#
#        finaltitle = None
#
#        for title in titles:
#            if title != '':
#                string = ''.join(letter for letter in title if letter.isalnum())
#                if finaltitle is None:
#                    finaltitle = string
#                else:
#                    finaltitle = finaltitle + "-" + string
#
#        if finaltitle is not None:
#            finaltitle = finaltitle.lower()
#            if len(finaltitle) > 100:
#                finaltitle = finaltitle[0:99]
#
#            category = discord.utils.get(interaction.guild.categories, name=str(os.environ.get("SUBITO_IT_CATEGORY_NAME")))
#
#            channel = discord.utils.get(interaction.guild.channels, name=finaltitle, category=category)
#            if channel is None:
#                channel = await interaction.guild.create_text_channel(finaltitle, category=category)
#
#            await utils.insert_subito_db(currentguildid, link, '', '', '', '', '', '', finaltitle)     
#            await interaction.followup.send(await utils.translate(currentguildid,"I am adding a configuration link:") + link + "\n" + await utils.translate(currentguildid,"Creating channel:") + finaltitle, ephemeral = True) 
#        else:
#            await interaction.followup.send(await utils.translate(currentguildid,"There was an error generating the discord channel for this link.") + link, ephemeral = True)  
#    except Exception as e:
#        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)



#@client.tree.command()
#@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
#async def list_subito_urls(interaction: discord.Interaction):
#    """List Subito.it configured link(s)."""
#    is_deferred=True
#    try:
#        await interaction.response.defer(thinking=True, ephemeral=True)
#        check_permissions(interaction)
#        currentguildid = get_current_guild_id(interaction.guild.id)
#        links = await utils.select_subito_urls(currentguildid)
#        message = ''
#        for link in links:         
#            message = message + "\n" + link
#        if message == '':
#            await interaction.followup.send(await utils.translate(currentguildid,"No configuration link found."), ephemeral = True)
#        else:
#            message = await utils.translate(currentguildid,"Configured links found:") + "\n" + message
#            await interaction.followup.send(message, ephemeral = True)
#         
#    except Exception as e:
#        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)



#@client.tree.command()
#@app_commands.rename(link='link')
#@app_commands.describe(link="Subito.it link")
#@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
#async def delete_subito_url(interaction: discord.Interaction, link: str):
#    """Add a new Subito.it link."""
#    is_deferred=True
#    try:
#        await interaction.response.defer(thinking=True, ephemeral=True)
#        check_permissions(interaction)
#        currentguildid = get_current_guild_id(interaction.guild.id)  
#
#        finaltitle = await utils.select_subito_channel(currentguildid, link) 
#
#        if finaltitle is not None:
#                
#            category = discord.utils.get(interaction.guild.categories, name=str(os.environ.get("SUBITO_IT_CATEGORY_NAME")))
#
#            channel = discord.utils.get(interaction.guild.channels, name=finaltitle, category=category)
#            if channel is not None:
#                await channel.delete()
#
#            await utils.delete_subito_url(currentguildid, link)
#            await interaction.followup.send(await utils.translate(currentguildid,"I am removing a configuration link:") + link + "\n" + await utils.translate(currentguildid,"Deleting channel:") + finaltitle, ephemeral = True) 
#        else:
#            await interaction.followup.send(await utils.translate(currentguildid,"No configuration found for that link.") + link, ephemeral = True) 
#    except Exception as e:
#        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)




@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def soundrandom(interaction: discord.Interaction, text: Optional[str] = "random"):
    """Play a random sound from the soundboard."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        
        if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        elif voice_client:
            currentguildid = get_current_guild_id(interaction.guild.id)

            url = get_api_url() + os.environ.get("API_PATH_SOUNDBOARD") + "/random/" + urllib.parse.quote(str(text)) + "/" + urllib.parse.quote(currentguildid)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        text = await response.text()
                        json_object = json.loads(text)
                        name = json_object['name']
                        url = json_object['url']
                        await do_play(url, interaction, currentguildid, name=name)
                    else:
                        if text == "random":
                            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I haven't found any results "), ephemeral = True)   
                        else:
                            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"I haven't found any results ") + " [" + text + "]", ephemeral = True)     
                await session.close() 
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"The bot is not ready yet or another user is already using another command.") +"\n" + await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)
         
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def soundsearch(interaction: discord.Interaction, text: Optional[str] = "random"):
    """Search for sounds on the soundboard."""
    is_deferred=True
    
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        
        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
        await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

        
        #if not hasattr(voice_client, 'play'):
        #    await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later, I'm initializing the voice connection..."), ephemeral = True)
        #elif not voice_client.is_playing():
        currentguildid = get_current_guild_id(interaction.guild.id)
        is_deferred=True            
        url = get_api_url() + os.environ.get("API_PATH_SOUNDBOARD") + "/query/" + urllib.parse.quote(str(text)) + "/" + urllib.parse.quote(currentguildid)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if (response.status == 200):
                    text_resp = await response.text()
                    json_object = json.loads(text_resp)
                    view = discord.ui.View()
                    for element in json_object:
                        button = SoundBoardButton(element['name'], element['url'])
                        view.add_item(button)
                    await interaction.followup.send(text, view=view, ephemeral = True)   
                else:
                    logging.error("[GUILDID : %s] soundboard - Received bad response from APIs", currentguildid)
                    if text == "random":
                        await interaction.followup.send(await utils.translate(currentguildid,"I haven't found any results "), ephemeral = True)   
                    else:
                        await interaction.followup.send(await utils.translate(currentguildid,"I haven't found any results ") + " [" + text + "]", ephemeral = True)   
            await session.close() 
          
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def commands(interaction: discord.Interaction):
    """Show bot commands."""
    is_deferred=True
    try:     
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        view = discord.ui.View()
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.DISCLAIMER))
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.CURSE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.INSULT))
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.GENERATE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.STORY))
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.RANDOM))

        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.SOUNDRANDOM))
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.ENABLE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.DISABLE))

        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.JOIN))
        view.add_item(SlashCommandButton(discord.ButtonStyle.green, constants.LEAVE))
        

        
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.SPEAK))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.TRANSLATE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.RENAME))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.TIMER))  

        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.DOWNLOAD))
        #view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.TRACKUSER))
        #view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.UNTRACKALL))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.TRAIN))

        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.SOUNDSEARCH))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.YOUTUBE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.WIKIPEDIA))
        #view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.BARD))
        view.add_item(SlashCommandButton(discord.ButtonStyle.red, constants.STOP))

        message = await utils.translate(get_current_guild_id(interaction.guild.id),"These are the bot's base commands")
        message = "\n\n"
        message = await utils.translate(get_current_guild_id(interaction.guild.id),"To show the bot's admin commands use") + "  /admin"

        await interaction.followup.send(message, view = view, ephemeral = False)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def admin(interaction: discord.Interaction):
    """Show Admin bot commands."""
    is_deferred=True
    try:     
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        if interaction.user.guild_permissions.administrator:

            view = discord.ui.View()
            view.add_item(AdminCommandButton(discord.ButtonStyle.green, constants.DOWNLOAD))
            view.add_item(AdminCommandButton(discord.ButtonStyle.primary, constants.LANGUAGE))
            view.add_item(AdminCommandButton(discord.ButtonStyle.primary, constants.AVATAR))
            view.add_item(AdminCommandButton(discord.ButtonStyle.primary, constants.DELETE))
            view.add_item(AdminCommandButton(discord.ButtonStyle.red, constants.RESET))

            message = await utils.translate(get_current_guild_id(interaction.guild.id),"These are the bot's admin commands")
            message = "\n\n"
            message = await utils.translate(get_current_guild_id(interaction.guild.id),"To show the bot's base commands use") + "  /commands"

            await interaction.followup.send(message, view = view, ephemeral = True)
     
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)    
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)



@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def accept(interaction: discord.Interaction):
    """Accept or Decline NSFW content."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        if interaction.user.guild_permissions.administrator:
            view = discord.ui.View()
            view.add_item(AcceptButton())
            view.add_item(DeclineButton())
            message = "DISCLAIMER\n"
            message = message + await utils.translate(get_current_guild_id(interaction.guild.id),"The developer takes no responsability of what the bot generates or on what the users write using the bot commands.")
            message = "\n\n"
            message = await utils.translate(get_current_guild_id(interaction.guild.id),"Do you want to allow NSFW content for this server?")
            await interaction.followup.send(message, view = view,  ephemeral = True)   
        else:
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def disclaimer(interaction: discord.Interaction):
    """Show DISCLAIMER."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=False)
        #check_permissions(interaction)
        await interaction.followup.send(await get_disclaimer(get_current_guild_id(interaction.guild.id)), ephemeral = True)   
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.rename(file='file')
@app_commands.describe(file="The sentences file")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def train(interaction: discord.Interaction, file: discord.Attachment):
    """Train the Bot using a sentences file."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        check_permissions(interaction)
        currentguildid = get_current_guild_id(interaction.guild.id)
        if not utils.allowed_file(file.filename):
            await interaction.followup.send(await utils.translate(currentguildid,"Please upload a valid text file.") + " (.txt)", ephemeral = True)     
        else:
        
            url = get_api_url() + os.environ.get("API_PATH_DATABASE") + "/upload/trainfile/txt"
            form_data = {'chatid': str(currentguildid),
                        'lang': utils.get_guild_language(currentguildid)
                        }
            trainfile = await file.to_file()
            filepath = os.environ.get("TMP_DIR") + "/trainfile.txt"
            with open(filepath, 'wb') as filewrite:
                additional_msg = "\n\n**!! "+ await utils.translate(currentguildid,"Until the end of this process the Bot is not available") + " !!**"
                filewrite.write(trainfile.fp.getbuffer())
                with open(filepath, "r") as f:
                    for l in f:
                        logging.info("[GUILDID : %s] upload/trainfile/txt - Found line: " + l)
                
                response = requests.post(url, data=form_data, files={"trainfile": open(filepath, "rb")})
                if (response.status_code == 200):
                    await interaction.followup.send(await utils.translate(currentguildid,"I am inserting the sentences into the bot. This process might take a lot time."), ephemeral = True) 
                elif response.status_code == 500:
                    await interaction.followup.send(await utils.translate(currentguildid,"Temporarily disabled. Other functions are running in the background, you need to wait for the end of their execution. This process might take a lot time."), ephemeral = True) 
                elif response.status_code == 406:
                    message = response.headers["X-Generated-Text"].encode('latin-1').decode('utf-8')
                    logging.error("[GUILDID : %s] do_play - Blocked by filters detected from APIs", str(get_current_guild_id(interaction.guild.id)))
                    message = await utils.translate(get_current_guild_id(interaction.guild.id),"Error. The sentence contains a word that is blocked by filters.") + " ["+ str(message) +"]"
                    await interaction.followup.send(message, ephemeral = True)
                elif response.status_code == 424:
                    logging.error("[GUILDID : %s] do_play - FakeYou APIs are offline", str(get_current_guild_id(interaction.guild.id)))
                    message = ""
                    message = message + "\n" + await utils.translate(currentguildid,"I can't reproduce this audio because FakeYou isn't available at the moment. Please try again later.")
                    message = message + "\n" + await utils.translate(currentguildid,"Alternatively you can use one of these voices:") + " google, Giorgio"
                    message = message + "\n" + await utils.translate(currentguildid,"You can check the status of the FakeYou.com service and the TTS queue here:") + "https://fakeyou.com/"
                    await interaction.followup.send(message, ephemeral = True)
                else:
                    logging.error("[GUILDID : %s] upload/trainfile/txt - Received bad response from APIs", str(currentguildid))
                    await interaction.followup.send(await utils.translate(currentguildid,"Error."), ephemeral = True)  

            os.remove(filepath)   

    except UnicodeDecodeError:
        logging.error("[GUILDID : %s] train - Uploaded bad text file.", str(currentguildid))
        await interaction.followup.send(await utils.translate(currentguildid,"Please upload a valid text file.") + " (.txt)", ephemeral = True)   
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def reset(interaction: discord.Interaction):
    """Resets the bot database"""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #check_permissions(interaction)
        
        if interaction.user.guild_permissions.administrator:
            currentguildid = get_current_guild_id(interaction.guild.id)
            url = get_api_url() + os.environ.get("API_PATH_DATABASE") + "/reset/" +urllib.parse.quote(currentguildid)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        await interaction.followup.send(await utils.translate(currentguildid,"All the sentences saved in the bot's database have been deleted"), ephemeral = True)
                    else:
                        logging.error("[GUILDID : %s] reset - Received bad response from APIs", str(currentguildid))
                        await interaction.followup.send("API Timeout, " + await utils.translate(currentguildid,"please try again later"), ephemeral = True)
                await session.close() 
        else:        
            await interaction.followup.send(await utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
            
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@admin.error
@accept.error
@audio.error
@avatar.error
#@bard.error
@commands.error
@curse.error
@delete.error
@disable.error
@disclaimer.error
@download.error
@enable.error
@generate.error
@insult.error
@join.error
@language.error
@leave.error
@random.error
@rename.error
@reset.error
@soundrandom.error
@soundsearch.error
@speak.error
@story.error
@timer.error
@train.error
#@trackuser.error
@translate.error
@stop.error
#@untrackall.error
@youtube.error
@wikipedia.error
async def on_generic_error(interaction: discord.Interaction, e: app_commands.AppCommandError):
    await send_error(e, interaction, from_generic=True)

client.run(os.environ.get("BOT_TOKEN"))
