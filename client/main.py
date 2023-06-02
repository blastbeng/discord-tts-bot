
import os
import sys
import json
import time
import utils
import random
import urllib
import logging
import pathlib
import constants
import urllib.request
from PIL import Image
from typing import Optional
from os.path import join, dirname
from dotenv import load_dotenv
import requests.exceptions
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.errors import ClientException
from requests.exceptions import ReadTimeout
from datetime import datetime
from typing import List
import asyncio
import threading
import requests
import aiohttp

from utils import FFmpegPCMAudioBytesIO

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

GUILD_ID = discord.Object(id=os.environ.get("GUILD_ID"))

class MyClient(discord.AutoShardedClient):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

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
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
                if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif voice_client:
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    await do_play(self.audiourl, interaction, currentguildid, name = self.name)
                else:
                    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)            
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

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
                await interaction.followup.send("/insult <member> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Insult someone"), ephemeral = True)
            elif self.name == constants.RANDOM:
                await interaction.followup.send("/random -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Random sentence"), ephemeral = True)
            elif self.name == constants.TIMER:
                await interaction.followup.send("/timer <seconds> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"This is used to set the timer for the auto talking feature"), ephemeral = True)
            elif self.name == constants.SPEAK:
                await interaction.followup.send("/speak <text> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot repeats something"), ephemeral = True)
            elif self.name == constants.TRANSLATE:
                await interaction.followup.send("/translate <text> <language_to> <language_from[Optional]> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot translates a text"), ephemeral = True)
            elif self.name == constants.GENERATE:
                await interaction.followup.send("/generate -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Generate a random sentence"), ephemeral = True)
            elif self.name == constants.STORY:
                await interaction.followup.send("/story -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Generate a random story"), ephemeral = True)
            elif self.name == constants.ENABLE:
                await interaction.followup.send("/enable -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Enable auto talking feature"), ephemeral = True)
            elif self.name == constants.DISABLE:
                await interaction.followup.send("/disable -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Disable auto talking feature"), ephemeral = True)
            elif self.name == constants.JOIN:
                await interaction.followup.send("/join -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot joins the voice channel"), ephemeral = True)
            elif self.name == constants.LEAVE:
                await interaction.followup.send("/leave -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot leaves the voice channel"), ephemeral = True)
            elif self.name == constants.RENAME:
                await interaction.followup.send("/rename <name> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its name"), ephemeral = True)
            elif self.name == constants.SOUNDRANDOM:
                await interaction.followup.send("/soundrandom <text> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot searches and plays an audio results"), ephemeral = True)
            elif self.name == constants.SOUNDSEARCH:
                await interaction.followup.send("/soundsearch <text> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot searches and displays audio results, allowing you to play them"), ephemeral = True)
            elif self.name == constants.YOUTUBE:
                await interaction.followup.send("/youtube <url> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Listen to a youtube song"), ephemeral = True)
            elif self.name == constants.STOP:
                await interaction.followup.send("/stop -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot stops talking"), ephemeral = True)
            elif self.name == constants.DISCLAIMER:
                await interaction.followup.send("/disclaimer -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Show disclaimer"), ephemeral = True)
            elif self.name == constants.TRAIN:
                await interaction.followup.send("/train <file> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot inserts in its database the sentencess present in the TXT file"), ephemeral = True)
            elif self.name == constants.WIKIPEDIA:
                await interaction.followup.send("/wikipedia <text> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot searches something on wikipedia"), ephemeral = True)
            elif self.name == constants.BLOCK:
                await interaction.followup.send("/block <word> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot adds a word to the blacklist"), ephemeral = True)         
            elif self.name == constants.UNBLOCK:
                await interaction.followup.send("/unblock <word> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot removes a word from the blacklist"), ephemeral = True)   
            else:
                await interaction.followup.send("Work in progress", ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)



class AdminCommandButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, style, name):
        super().__init__(style=style, label="/"+name)
        self.name = name
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:            
            await interaction.response.defer(thinking=True, ephemeral=True)
            if self.name == constants.LANGUAGE:
                await interaction.followup.send("/language <language> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its main language"), ephemeral = True)
            elif self.name == constants.AVATAR:
                await interaction.followup.send("/avatar <image> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its avatar"), ephemeral = True)
            elif self.name == constants.DELETE:
                await interaction.followup.send("/delete <text> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot deletes all the sentences containing the given text"), ephemeral = True)
            elif self.name == constants.DOWNLOAD:
                await interaction.followup.send("/download -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Downloads a copy of the BOT's database"), ephemeral = True)       
            elif self.name == constants.UNBLOCKALL:
                await interaction.followup.send("/unblockall -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot removes all the words from the blacklist"), ephemeral = True)         
            elif self.name == constants.RESET:
                await interaction.followup.send("/reset -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot resets its database and deletes all the saved sentences"), ephemeral = True)         
            else:
                await interaction.followup.send("Work in progress", ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

class SaveButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, message):
        super().__init__(style=discord.ButtonStyle.primary, label="Save")
        self.message = message
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            currentguildid = get_current_guild_id(interaction.guild.id)
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_TEXT") + "repeat/learn/" + urllib.parse.quote(self.message) + "/" + currentguildid + "/" + utils.get_guild_language(currentguildid)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),'This sentence has been saved.'), ephemeral = True)  
                    else:
                        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),'Error detected while saving this sentence.'), ephemeral = True)    
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message) 
            
        
class PlayButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, content, message):
        super().__init__(style=discord.ButtonStyle.green, label="Play")
        self.content = content
        self.message = message
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                voice_client.play(FFmpegPCMAudioBytesIO(self.content, pipe=True), after=lambda e: logging.info("do_play - " + self.message))
                await interaction.followup.send(self.message, ephemeral = True)
                
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)
            
class StopButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Stop")
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                logging.info("stop - StopButton.callback.stop()")
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I'm interrupting the bot"), ephemeral = True)
                voice_client.stop()
                
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)
            
class AcceptButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Accept")
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            utils.update_guild_nsfw(get_current_guild_id(interaction.guild.id), 1)
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You have enabled NSFW content."), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)
            
class DeclineButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Decline")
    
    async def callback(self, interaction: discord.Interaction):
        is_deferred=True
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
            utils.update_guild_nsfw(get_current_guild_id(interaction.guild.id), 0)
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You have disabled NSFW content."), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


intents = discord.Intents.default()
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
populator_loops_dict = {}
generator_loops_dict = {}
cvc_loops_dict = {}
fakeyou_voices = {}

async def display_loader(interaction, currentguildid):
    with open('loading.gif', 'rb') as f:
        picture = discord.File(f)
        name = interaction.guild.me.nick if interaction.guild.me.nick else interaction.guild.me.name 
        message = utils.translate(currentguildid,"Someone used") + " **/" + interaction.command.name + "**\n"
        message = "*" + message + utils.translate(currentguildid,name+"'s working on it*")
        load_message = await interaction.channel.send(message, file=picture)
        return load_message

async def listvoices_api(language="it", filter=None):
    try:
        global fakeyou_voices
        if fakeyou_voices is None or len(fakeyou_voices) == 0 or len(fakeyou_voices) == 1:
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/fakeyou/listvoices/" + language
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        text = await response.text()
                        fakeyou_voices = json.loads(text)
        if (fakeyou_voices is not None and len(fakeyou_voices) > 0):
            if filter is not None:
                voice = None
                for key in fakeyou_voices:
                    if filter.lower() in key.lower():
                        voice = fakeyou_voices[key]
                return voice
            else:
                return fakeyou_voices
        else:
            fakeyou_voices = {}
            fakeyou_voices ["google"] = "google"
            return fakeyou_voices
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        return None

async def rps_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    currentguildid=get_current_guild_id(interaction.guild.id)
    choices = await listvoices_api(language=utils.get_guild_language(currentguildid))
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

async def send_error(e, interaction, from_generic=False, is_deferred=False, load_message=None):
    currentguildid=get_current_guild_id(interaction.guild.id)
    if load_message:
        await load_message.delete()
    if isinstance(e, app_commands.CommandOnCooldown):
        try:
            dtc = "Spam " + utils.translate(currentguildid,"detected.")
            spamarray=[]
            spamarray.append(dtc + " " + interaction.user.mention + " " + utils.translate(currentguildid,"I am watching you."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + utils.translate(currentguildid,"This doesn't make you a good person."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + utils.translate(currentguildid,"I'm stupid but not annoying."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + utils.translate(currentguildid,"Take your time."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + utils.translate(currentguildid,"Keep calm."))
            spamarray.append(dtc + " " + interaction.user.mention + " " + utils.translate(currentguildid,"Do you also do this at your home?"))
            spamarray.append(dtc + " " + interaction.user.mention + " " + utils.translate(currentguildid,"Why are you so anxious?"))
            spamarray.append(dtc + " " + interaction.user.mention + " " + utils.translate(currentguildid,"I'll add you to the blacklist."))
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
                await interaction.followup.send("Discord API Error, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
            else:
                await interaction.response.send_message("Discord API Error, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("[GUILDID : %s] %s %s %s", currentguildid, exc_type, fname, exc_tb.tb_lineno)
        if is_deferred:
            await interaction.followup.send("Discord API Error, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
        else:
            await interaction.response.send_message("Discord API Error, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
    

def get_voice_client_by_guildid(voice_clients, guildid):
    for vc in voice_clients:
        if vc.guild.id == guildid:
            return vc
    return None

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
            if (perms.administrator or (perms.connect and perms.speak)):
                if voice_client and voice_client.channel and voice_client.is_connected():
                    await voice_client.disconnect()
                    time.sleep(10)
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
            
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if (response.status != 200):
                    logging.error("Initializing chatterbot on chatid " + currentguildid + " failed")
                else:
                    message = url
                    if "X-Generated-Text" in response.headers:
                        message = response.headers["X-Generated-Text"]
                    elif name is not None:
                        message = name
                    if (response is not None and response.status == 200):
                        content = await response.content.read()
                        voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                        if not voice_client:
                            raise ClientException("voice_client is None")
                        if voice_client.is_playing():
                            voice_client.stop()
                            
                        voice_client.play(FFmpegPCMAudioBytesIO(content, pipe=True), after=lambda e: logging.info("do_play - " + message))
                        view = discord.ui.View()
                        view.add_item(PlayButton(content, message))
                        view.add_item(StopButton())
                        if show_save:
                            view.add_item(SaveButton(message))
                        await interaction.followup.send(message, view = view, ephemeral = ephermeal)
                    elif response.status == 400:
                        logging.error("[GUILDID : %s] do_play - TTS Limit exceeded detected from APIs", str(get_current_guild_id(interaction.guild.id)))
                        message = message + "\n\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Error. Can't reproduce audio.\nThe Generated TTS is longer than the maximum limit. ("+ str(int(os.environ.get("MAX_TTS_DURATION"))) +" seconds)")
                        await interaction.followup.send(message, ephemeral = True)
                    elif response.status == 406:
                        logging.error("[GUILDID : %s] do_play - Blocked by filters detected from APIs", str(get_current_guild_id(interaction.guild.id)))
                        message = utils.translate(get_current_guild_id(interaction.guild.id),"Error. The sentence contains a word that is blocked by filters.") + " ["+ str(message) +"]"
                        await interaction.followup.send(message, ephemeral = True)
                    else:
                        logging.error("[GUILDID : %s] do_play - Received bad response from APIs.", str(get_current_guild_id(interaction.guild.id)))
                        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)
    except ReadTimeout as te:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        #if defer:
        await interaction.followup.send("API Timeout, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
        #else:
        #    await interaction.response.send_message("API Timeout, " + utils.translate(get_current_guild_id(interaction.guild.id),"please try again later"), ephemeral = True)
    except ClientException as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        #if defer:
        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)
        #else:
        #    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.\nPlease try again later or use stop command"), ephemeral = True)
    except Exception as ee:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        #if defer:
        await interaction.followup.send("API Timeout, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
        #else:
        #    await interaction.response.send_message("API Timeout, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)

class PlayAudioLoop:
    
    def __init__(self, guildid):
        for guild in client.guilds:
            if guild.id == guildid:
                self.guild = guild

    @tasks.loop(seconds=120)
    async def play_audio_loop(self):
        try:
            currentguildid = get_current_guild_id(str(self.guild.id))
            channelfound = None
            channeluserfound = None
            voice_client = get_voice_client_by_guildid(client.voice_clients, self.guild.id)                
            for channel in self.guild.voice_channels:
                perms = channel.permissions_for(channel.guild.me)
                if (perms.administrator or (perms.connect and perms.speak)):
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
                    response = requests.get(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/random/" + currentguildid + "/" + utils.get_guild_language(currentguildid), timeout=60)
                    if (response is not None and response.status_code == 200 and response.content):
                        text = response.headers["X-Generated-Text"].encode('latin-1').decode('utf-8')
                        message = 'play_audio_loop - random - ' + text
                        voice_client.play(FFmpegPCMAudioBytesIO(response.content, pipe=True), after=lambda e: logging.info(message))
        except ReadTimeout as te:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
            logging.error('play_audio_loop - random - Timeout!')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)


class PopulatorLoop:
    
    def __init__(self, guildid):
        self.guildid = guildid

    @tasks.loop(minutes=int(180))
    async def populator_loop(self):
        try:
            currentguildid = get_current_guild_id(str(self.guildid))
            response = requests.get(os.environ.get("API_URL")+os.environ.get("API_PATH_DATABASE")+"/audiodb/populate/20/" + currentguildid + "/" + utils.get_guild_language(currentguildid) + "/1") 
            if (response.status_code == 200 and response.text):
                logging.info("populator_loop - " + str(response.text))
            else:
                logging.error("populator_loop - Error calling populator - status_code: " + str(response.status_code))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)


class GeneratorLoop:
    
    def __init__(self, guildid):
        self.guildid = guildid

    @tasks.loop(hours=12)
    async def generator_loop(self):
        try:
            currentguildid = get_current_guild_id(str(self.guildid))
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/initgenerator/" + urllib.parse.quote(currentguildid) + "/" + utils.get_guild_language(currentguildid)
            response = requests.get(url)
            if (response.status_code != 200):
                logging.error("Initializing generator on chatid " + currentguildid + " failed")
            else:
                logging.info(response.text)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)


class CheckVoiceConnectionLoop:
    
    def __init__(self, guildid):
        self.guildid = guildid

    @tasks.loop(minutes=1)
    async def check_voice_connection_loop(self):
        try:
            voice_client = get_voice_client_by_guildid(client.voice_clients, self.guildid)
            if voice_client and voice_client.channel:
                userFound = False
                for member in voice_client.channel.members:
                    if not member.bot:
                        userFound = True
                        break
                if not userFound:
                    await voice_client.disconnect()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)



@tasks.loop(hours=6)
async def change_presence_loop():
    try:
        url = "https://steamspy.com/api.php?request=top100in2weeks"
        response = requests.get(url)
        if (response.status_code == 200):
            game_array = []
            for key, value in response.json().items():
                game_array.append(value['name'])
            game = str(utils.get_random_from_array(game_array))
            logging.info("change_presence_loop - change_presence - game: " + game)
            await client.change_presence(activity=discord.Game(name=game))
        else:
            logging.error("change_presence_loop - steamspy API ERROR - status_code: " + str(response.status_code))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user} (ID: {client.user.id})')

@client.event
async def on_connect():
    logging.info(f'Connected as {client.user} (ID: {client.user.id})')
    change_presence_loop.start()

@client.event
async def on_guild_available(guild):

    try:
        currentguildid = get_current_guild_id(str(guild.id))
        
        loops_dict[guild.id] = PlayAudioLoop(guild.id)
        if currentguildid == "000000":
            loops_dict[guild.id].play_audio_loop.start()

        populator_loops_dict[guild.id] = PopulatorLoop(guild.id)
        populator_loops_dict[guild.id].populator_loop.start()

        generator_loops_dict[guild.id] = GeneratorLoop(guild.id)
        generator_loops_dict[guild.id].generator_loop.start()

        cvc_loops_dict[guild.id] = CheckVoiceConnectionLoop(guild.id)
        cvc_loops_dict[guild.id].check_voice_connection_loop.start()


        utils.check_exists_guild(currentguildid)        
        lang = utils.get_guild_language(currentguildid)
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/init/" + urllib.parse.quote(currentguildid) + "/" + urllib.parse.quote(lang)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if (response.status != 200):
                    logging.error("Initializing chatterbot on chatid " + currentguildid + " failed")
                else:
                    text = await response.text()
                    logging.info(text)

        await listvoices_api(language=lang, filter=None)

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

@client.event
async def on_voice_state_update(member, before, after):
    try:
        if before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            voice_client = get_voice_client_by_guildid(client.voice_clients, member.guild.id)

            perms = after.channel.permissions_for(after.channel.guild.me)
            if (perms.administrator or (perms.connect and perms.speak)):
                if voice_client:
                    await voice_client.disconnect()
                await connect_bot_by_voice_client(voice_client, after.channel, None, member=member)
        elif before.channel is None and after.channel is not None:
            voice_client = get_voice_client_by_guildid(client.voice_clients, member.guild.id)
            await connect_bot_by_voice_client(voice_client, after.channel, None, member=member)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def get_disclaimer(currentguildid):
    message = "**DISCLAIMER**"
    message = message + "\n" + utils.translate(currentguildid,"This Bot saves data in its encrypted database, used for the auto-talking feature.")
    message = message + "\n" + utils.translate(currentguildid,"Please don't write sensitive data, you have been warned.")
    message = message + "\n" + utils.translate(currentguildid,"The developer takes no responsibility of what the bot generates or on what the users write using the bot commands.")
    message = message + "\n\n" + utils.translate(currentguildid,"I am a dumb Bot and I don't want to cause any problem.")
    message = message + "\n\n" + utils.translate(currentguildid,"The default language is English, if you want to change language ask an Administrator to do so with the command:") + " /language."
    message = message + "\n\nNSFW => [/insult] [/curse]"        
    message = message + "\n" + utils.translate(currentguildid,"Two commands delivers NSFW content. An administrator must approve NSFW content using the command") + " /accept."
    return message
    
@client.event
async def on_guild_join(guild):
    logging.info(f'Guild joined (ID: {guild.id})')
    utils.check_exists_guild(get_current_guild_id(str(guild.id)))
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)
    logging.info(f'Syncing commands to Guild (ID: {guild.id}) (NAME: {guild.name})')

    await guild.system_channel.send(get_disclaimer(get_current_guild_id(guild.id)))

@client.event
async def on_guild_remove(guild):
    try:
        if str(interaction.guild.id) != str(os.environ.get("GUILD_ID")):
            utils.delete_guild(str(guild.id))
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_DATABASE") + "/reset/" +urllib.parse.quote(str(guild.id))
            response = await requests.get(url)
            if (response.status_code != 200):
                logging.error("[GUILDID : %s] on_guild_remove -> reset - Received bad response from APIs", str(guild.id))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def join(interaction: discord.Interaction):
    """Join channel."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I'm joining the voice channel"), ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        #await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def leave(interaction: discord.Interaction):
    """Leave channel"""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            if voice_client and voice_client.channel.id == interaction.user.voice.channel.id:
                await voice_client.disconnect()
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I'm leaving the voice channel"), ephemeral = True)
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I'm not connected to any voice channel"), ephemeral = True)       
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        #await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to repeat")
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.autocomplete(voice=rps_autocomplete)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def speak(interaction: discord.Interaction, text: str, voice: str = "google"):
    """Repeat a sentence"""
    is_deferred=True
    load_message = None
    try:
      
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:

                currentguildid = get_current_guild_id(interaction.guild.id)
                
                lang_to_use = utils.get_guild_language(currentguildid)

                if voice != "google":
                    voice = await listvoices_api(language=lang_to_use, filter=voice)

                if voice is not None:
                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(text))+"/" + urllib.parse.quote(voice) + "/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(lang_to_use)
                    await do_play(url, interaction, currentguildid)
                else:
                    await interaction.followup.send("Discord API Error, " + utils.translate(get_current_guild_id(interaction.guild.id),"please try again later"), ephemeral = True)      
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)            
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def wikipedia(interaction: discord.Interaction, text: str):
    """Search something on wikipedia"""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:

                currentguildid = get_current_guild_id(interaction.guild.id)
                url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"search/"+urllib.parse.quote(str(text))+"/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                await do_play(url, interaction, currentguildid)

            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)            
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="the sentence to ask")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.autocomplete(voice=rps_autocomplete)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def ask(interaction: discord.Interaction, text: str, voice: str = "google"):
    """Ask something."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            
            if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:
                currentguildid = get_current_guild_id(interaction.guild.id)

                if voice != "google":
                    voice = await listvoices_api(language=lang_to_use, filter=voice)

                if voice is not None:
                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"ask/"+urllib.parse.quote(str(text))+"/1/" + urllib.parse.quote(voice) + "/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                    await do_play(url, interaction, currentguildid)
                else:
                    await interaction.followup.send("Discord API Error, " + utils.translate(get_current_guild_id(interaction.guild.id),"please try again later"), ephemeral = True) 
                
                
                await do_play(URL, interaction, currentguildid)
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)

            
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def generate(interaction: discord.Interaction):
    """Generate a random sentence."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))

        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            
            if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:
                currentguildid = get_current_guild_id(interaction.guild.id)
                url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/sentences/generate/" + urllib.parse.quote(currentguildid) + "/0"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if (response.status == 200):
                            text = await response.text()
                            url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                            await do_play(url, interaction, currentguildid, show_save=True)
                        else:
                            logging.error("[GUILDID : %s] generate - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)))
                            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),'Error. The generator database is still empty, try again later.\nNOTE: If you just invited the bot, this feature will be available in 12 hours if you continue to use the "speak" command.'), ephemeral = True)     
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def story(interaction: discord.Interaction):
    """Generate a random story."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)


            if voice_client and not hasattr(voice_client, 'play') and voice_client.is_connected():
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:
                currentguildid = get_current_guild_id(interaction.guild.id)
                url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/paragraph/generate/" + urllib.parse.quote(currentguildid)
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if (response.status == 200):
                            text = await response.text()
                            url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)
                            await do_play(url, interaction, currentguildid)
                        else:
                            logging.error("[GUILDID : %s] story - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)))
                            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),'Error. The generator database is still empty, try again later.\nNOTE: If you just invited the bot, this feature will be available in 12 hours if you continue to use the "speak" command.'), ephemeral = True)         

            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)



@client.tree.command()
@app_commands.rename(member='member')
@app_commands.describe(member="The user to insult")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def insult(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Insult someone"""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        currentguildid = get_current_guild_id(interaction.guild.id)
        if utils.get_guild_nsfw(currentguildid) == 0:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"An Administrator must approve NSFW content on this server. Ask him to use the command:") + " /accept", ephemeral = True)
        elif interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:
                insulturl=os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult"
                if member:
                    name = None
                    if member.nick is not None:
                        name = str(member.nick)
                    else:
                        name = str(member.name)
                    insulturl=insulturl +"?text="+urllib.parse.quote(name) + "&chatid="+urllib.parse.quote(get_current_guild_id(interaction.guild.id))
                else:
                    insulturl=insulturl +"?chatid="+urllib.parse.quote(get_current_guild_id(interaction.guild.id)) + "&lang=" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                await do_play(insulturl, interaction, currentguildid)
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)

        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)



@client.tree.command()
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.autocomplete(voice=rps_autocomplete)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def random(interaction: discord.Interaction, voice: str = "random"):
    """Say a random sentence"""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:
                
                currentguildid = get_current_guild_id(interaction.guild.id)                

                if voice != "random":
                    voice = await listvoices_api(language=utils.get_guild_language(currentguildid), filter=voice)

                if voice is not None:
                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/" + urllib.parse.quote(voice) + "/"+urllib.parse.quote(currentguildid)+ "/" + utils.get_guild_language(currentguildid)
                    await do_play(url, interaction, currentguildid)
                else:
                    await interaction.followup.send("Discord API Error, " + utils.translate(get_current_guild_id(interaction.guild.id),"please try again later"), ephemeral = True)
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)

        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)



@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def curse(interaction: discord.Interaction):
    """Curse."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        async with aiohttp.ClientSession() as session:
            async with session.get('https://bestemmie.org') as response:
                if (response.status != 200):
                    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Impossible to use this command") + ": API 'http://bestemmie.org' Status = OFFLINE", ephemeral = True)
                else:
                    try:
                        currentguildid = get_current_guild_id(interaction.guild.id)
                        if utils.get_guild_nsfw(currentguildid) == 0:
                            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"An Administrator must approve NSFW content on this server. Ask him to use the command:") + " /accept", ephemeral = True)
                        elif interaction.user.voice and interaction.user.voice.channel:
                            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                            elif voice_client:
                                

                                url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"curse/"+urllib.parse.quote(currentguildid)+ "/" + utils.get_guild_language(currentguildid)
                                await do_play(url, interaction, currentguildid)
                            else:
                                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)

                        else:
                            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
                    except Exception as e:
                        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)
        if load_message:
            await load_message.delete()  
    except Exception as e:
        if load_message:
            await load_message.delete()            
        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Impossible to use this command") + ": API 'http://bestemmie.org' Status = OFFLINE", ephemeral = True)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def restart(interaction: discord.Interaction):
    """Restart bot."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")) and str(interaction.user.id) == str(os.environ.get("ADMIN_ID")):
            if interaction.user.guild_permissions.administrator:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Restarting bot."), ephemeral = True)
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=None)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def delete(interaction: discord.Interaction, text: str):
    """Delete sentences by text."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.guild_permissions.administrator:
            currentguildid = get_current_guild_id(interaction.guild.id)
            async with aiohttp.ClientSession() as session:
                async with session.get(os.environ.get("API_URL") + os.environ.get("API_PATH_DATABASE") + "/forcedelete/bytext/" + urllib.parse.quote(text) + "/" + urllib.parse.quote(currentguildid)) as response:
                    if (response.status == 200):
                        text = await response.text()
                        await interaction.followup.send(text, ephemeral = True) 
                    else:
                        logging.error("[GUILDID : %s] forcedelete/bytext - Received bad response from APIs", str(currentguildid))
                        await interaction.followup.send(utils.translate(currentguildid,"Error."), ephemeral = True)     
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=None)

@client.tree.command()
@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.user.id))
async def download(interaction: discord.Interaction):
    """Delete sentences by text."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.guild_permissions.administrator:
            currentguildid = get_current_guild_id(interaction.guild.id)

            async with aiohttp.ClientSession() as session:
                async with session.get(os.environ.get("API_URL") + os.environ.get("API_PATH_DATABASE") + "/download/sentences/" + urllib.parse.quote(currentguildid)) as response:
                    if (response.status == 200):

                        text = await response.text()

                        nameout = str(interaction.guild.name) + "_" + str(client.user.name)  + "_Backup_"  + datetime.now().strftime("%d%m%Y_%H%M%S") + ".txt"

                        filepath = os.environ.get("TMP_DIR") + nameout
                        with open(filepath, 'w') as filewrite:
                            filewrite.write(text)            
                            #for line in response.text.splitlines():
                            #    filewrite.write(line)            
                            #    filewrite.write("\n")            


                        await interaction.followup.send("Bot Backup.", file=discord.File(filename=nameout, fp=open(filepath, "rb")), ephemeral = True) 

                        os.remove(filepath)
                    else:
                        logging.error("[GUILDID : %s] download/sentences - Received bad response from APIs", str(currentguildid))
                        await interaction.followup.send(utils.translate(currentguildid,"Error."), ephemeral = True)     
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def stop(interaction: discord.Interaction):
    """Stop playback."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            logging.info("stop - voice_client.stop()")
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I'm interrupting the bot"), ephemeral = True)
            voice_client.stop()
            
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=None)

    

@client.tree.command()
@app_commands.rename(name='name')
@app_commands.describe(name="New bot nickname (32 chars limit)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def rename(interaction: discord.Interaction, name: str):
    """Rename bot."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        #load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if len(name) < 32:
            currentguildid = get_current_guild_id(interaction.guild.id)
            
            message = utils.translate(currentguildid,"You renamed me to") + ' "'+name+'"'
            #name = name + " [" + utils.get_guild_language(currentguildid) + "]"
            await interaction.guild.me.edit(nick=name)
            await interaction.followup.send(message, ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"My name cannot be longer than 32 characters"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=None)

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
                    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The image has been changed"), ephemeral = True)
                    os.remove(filepath)
                else:
                    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"This file type is not supported"), ephemeral = True)
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Only the bot owner can use this command"), ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=None)

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
        currentguildid = get_current_guild_id(interaction.guild.id)
        if interaction.user.guild_permissions.administrator:

            utils.update_guild_lang(currentguildid, language.value)

            await interaction.followup.send(utils.translate(currentguildid,"Bot language changed to ") + ' "'+language.name+'"', ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(currentguildid,"Only administrators can use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=None)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to convert")
@app_commands.rename(language_to='language_to')
@app_commands.describe(language_to="The language to convert to")
@app_commands.choices(language_to=optionslanguages)
@app_commands.rename(language_from='language_from')
@app_commands.describe(language_from="The language to convert from")
@app_commands.choices(language_from=optionslanguages)
@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.user.id))
async def translate(interaction: discord.Interaction, text: str, language_to: app_commands.Choice[str], language_from: app_commands.Choice[str] = "xx"):
    """Translate a sentence and repeat it"""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:

                currentguildid = get_current_guild_id(interaction.guild.id)

                lang_to_use_from = ""
                if hasattr(language_from, 'name'):
                    lang_to_use_from = language_from.value
                else:
                    lang_to_use_from = utils.get_guild_language(currentguildid)

                

                async with aiohttp.ClientSession() as session:
                    async with session.get(os.environ.get("API_URL") + os.environ.get("API_PATH_TEXT") + "translate/" + urllib.parse.quote(lang_to_use_from) + "/" + urllib.parse.quote(language_to.value) + "/" + urllib.parse.quote(text) + "/" + urllib.parse.quote(currentguildid)) as response:
                        if (response.status == 200):
                            translated_text = await response.text()
                            url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(translated_text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(language_to.value)
                            await do_play(url, interaction, currentguildid)
                        else:
                            logging.error("[GUILDID : %s] translate - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)))
                            await interaction.followup.send("API Timeout, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
                
                    
                
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)

            
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

@client.tree.command()
@app_commands.rename(url='url')
@app_commands.describe(url="Youtube link (Must match https://www.youtube.com/watch?v=1abcd2efghi)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def youtube(interaction: discord.Interaction, url: str):
    """Play a youtube link"""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
            
            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:

                if "watch?v=" in url:
                    currentguildid = get_current_guild_id(interaction.guild.id)

                    urlapi = os.environ.get("API_URL")+os.environ.get("API_PATH_MUSIC")+"youtube/get/"+(url.split("watch?v=",1)[1])+"/"+urllib.parse.quote(currentguildid)
                    await do_play(urlapi, interaction, currentguildid, ephermeal = False)
                else:
                    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"URL must match something like https://www.youtube.com/watch?v=1abcd2efghi"), ephemeral = True)
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)

            
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def enable(interaction: discord.Interaction):
    """Enable auto talking feature."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        currentguildid = get_current_guild_id(interaction.guild.id)
        if not loops_dict[interaction.guild.id].play_audio_loop.is_running():
            loops_dict[interaction.guild.id].play_audio_loop.start()
            logging.info("enable - play_audio_loop.start()")
            await interaction.followup.send(utils.translate(currentguildid,"I'm enabling the auto talking feature"), ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(currentguildid,"The auto talking feature is already enabled"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred = is_deferred)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def disable(interaction: discord.Interaction):
    """Disable auto talking feature."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        currentguildid = get_current_guild_id(interaction.guild.id)
        if loops_dict[interaction.guild.id].play_audio_loop.is_running():
            loops_dict[interaction.guild.id].play_audio_loop.stop()
            logging.info("disable - play_audio_loop.stop()")
            loops_dict[interaction.guild.id].play_audio_loop.cancel()
            logging.info("disable - play_audio_loop.cancel()")
            await interaction.followup.send(utils.translate(currentguildid,"I'm disabling the auto talking feature"), ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(currentguildid,"The auto talking feature is already disabled"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)

@client.tree.command()
@app_commands.rename(seconds='seconds')
@app_commands.describe(seconds="Timeout seconds (Min 20 - Max 600)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def timer(interaction: discord.Interaction, seconds: int):
    """Change the timer for the auto talking feature."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        currentguildid = get_current_guild_id(interaction.guild.id)
        if seconds < 20 or seconds > 600:
            await interaction.followup.send(utils.translate(currentguildid,"Seconds must be greater than 20 and lower than 600"), ephemeral = True)
        else:
            loops_dict[interaction.guild.id].play_audio_loop.change_interval(seconds=seconds)
            logging.info("timer - play_audio_loop.change_interval(seconds="+str(seconds)+")")
            await interaction.followup.send(utils.translate(currentguildid,"I'm setting a " + str(seconds) + " seconds timer for the auto talking feature"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)




@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def soundrandom(interaction: discord.Interaction, text: Optional[str] = "random"):
    """Play a random sound from the soundboard."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            
            if voice_client and (not hasattr(voice_client, 'play') or not voice_client.is_connected()):
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif voice_client:
                currentguildid = get_current_guild_id(interaction.guild.id)

                url = os.environ.get("API_URL") + os.environ.get("API_PATH_SOUNDBOARD") + "/random/" + urllib.parse.quote(str(text)) + "/" + urllib.parse.quote(currentguildid)
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
                                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I haven't found any results "), ephemeral = True)   
                            else:
                                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I haven't found any results ") + " [" + text + "]", ephemeral = True)     
            else:
                await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"The bot is already talking or another user is already using another command.") +"\n" + utils.translate(get_current_guild_id(interaction.guild.id),"Please try again later or use stop command"), ephemeral = True)
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def soundsearch(interaction: discord.Interaction, text: Optional[str] = "random"):
    """Search for sounds on the soundboard."""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            
            #if not hasattr(voice_client, 'play'):
            #    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            #elif not voice_client.is_playing():
            currentguildid = get_current_guild_id(interaction.guild.id)
            is_deferred=True            
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_SOUNDBOARD") + "/query/" + urllib.parse.quote(str(text)) + "/" + urllib.parse.quote(currentguildid)
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
                            await interaction.followup.send(utils.translate(currentguildid,"I haven't found any results "), ephemeral = True)   
                        else:
                            await interaction.followup.send(utils.translate(currentguildid,"I haven't found any results ") + " [" + text + "]", ephemeral = True)   
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        await load_message.delete()
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def commands(interaction: discord.Interaction):
    """Show bot commands."""
    is_deferred=True
    load_message = None
    try:     
        await interaction.response.defer(thinking=True, ephemeral=True)
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
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.TRAIN))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.BLOCK))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.UNBLOCK))

        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.SOUNDSEARCH))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.YOUTUBE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.WIKIPEDIA))
        view.add_item(SlashCommandButton(discord.ButtonStyle.red, constants.STOP))

        message = utils.translate(get_current_guild_id(interaction.guild.id),"These are the bot's base commands")
        message = "\n\n"
        message = utils.translate(get_current_guild_id(interaction.guild.id),"To show the bot's admin commands use") + "  /admin"

        await interaction.followup.send(message, view = view, ephemeral = False)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def admin(interaction: discord.Interaction):
    """Show Admin bot commands."""
    is_deferred=True
    load_message = None
    try:     
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.user.guild_permissions.administrator:

            view = discord.ui.View()
            view.add_item(AdminCommandButton(discord.ButtonStyle.green, constants.DOWNLOAD))
            view.add_item(AdminCommandButton(discord.ButtonStyle.primary, constants.LANGUAGE))
            view.add_item(AdminCommandButton(discord.ButtonStyle.primary, constants.AVATAR))
            view.add_item(AdminCommandButton(discord.ButtonStyle.primary, constants.DELETE))
            view.add_item(AdminCommandButton(discord.ButtonStyle.primary, constants.UNBLOCKALL))
            view.add_item(AdminCommandButton(discord.ButtonStyle.red, constants.RESET))

            message = utils.translate(get_current_guild_id(interaction.guild.id),"These are the bot's admin commands")
            message = "\n\n"
            message = utils.translate(get_current_guild_id(interaction.guild.id),"To show the bot's base commands use") + "  /commands"

            await interaction.followup.send(message, view = view, ephemeral = True)
     
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)    
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)



@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def accept(interaction: discord.Interaction):
    """Accept or Decline NSFW content."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.user.guild_permissions.administrator:
            view = discord.ui.View()
            view.add_item(AcceptButton())
            view.add_item(DeclineButton())
            message = "DISCLAIMER\n"
            message = message + utils.translate(get_current_guild_id(interaction.guild.id),"The developer takes no responsability of what the bot generates or on what the users write using the bot commands.")
            message = "\n\n"
            message = utils.translate(get_current_guild_id(interaction.guild.id),"Do you want to allow NSFW content for this server?")
            await interaction.followup.send(message, view = view,  ephemeral = True)   
        else:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=None)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def disclaimer(interaction: discord.Interaction):
    """Show DISCLAIMER."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=False)
        await interaction.followup.send(get_disclaimer(get_current_guild_id(interaction.guild.id)), ephemeral = True)   
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=None)


@client.tree.command()
@app_commands.rename(file='file')
@app_commands.describe(file="The sentences file")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def train(interaction: discord.Interaction, file: discord.Attachment):
    """Train the Bot using a sentences file."""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        currentguildid = get_current_guild_id(interaction.guild.id)
        if not utils.allowed_file(file.filename):
            await interaction.followup.send(utils.translate(currentguildid,"Please upload a valid text file.") + " (.txt)", ephemeral = True)     
        else:
        
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_DATABASE") + "/upload/trainfile/txt"
            form_data = {'chatid': str(currentguildid),
                        'lang': utils.get_guild_language(currentguildid)
                        }
            trainfile = await file.to_file()
            filepath = os.environ.get("TMP_DIR") + "/trainfile.txt"
            with open(filepath, 'wb') as filewrite:
                filewrite.write(trainfile.fp.getbuffer())

            try:
                with open(filepath, "r") as f:
                    for l in f:
                        logging.info("[GUILDID : %s] upload/trainfile/txt - Found line: " + l)

                response = requests.post(url, data=form_data, files={"trainfile": open(filepath, "rb")})

                if (response.status_code == 200):
                    await interaction.followup.send(utils.translate(currentguildid,"Done."), ephemeral = True) 
                elif response.status_code == 406:
                    message = response.headers["X-Generated-Text"].encode('latin-1').decode('utf-8')
                    logging.error("[GUILDID : %s] do_play - Blocked by filters detected from APIs", str(get_current_guild_id(interaction.guild.id)))
                    message = utils.translate(get_current_guild_id(interaction.guild.id),"Error. The sentence contains a word that is blocked by filters.") + " ["+ str(message) +"]"
                    await interaction.followup.send(message, ephemeral = True)
                else:
                    logging.error("[GUILDID : %s] upload/trainfile/txt - Received bad response from APIs", str(currentguildid))
                    await interaction.followup.send(utils.translate(currentguildid,"Error."), ephemeral = True)  

            except UnicodeDecodeError:
                logging.error("[GUILDID : %s] train - Uploaded bad text file.", str(currentguildid))
                await interaction.followup.send(utils.translate(currentguildid,"Please upload a valid text file.") + " (.txt)", ephemeral = True)   

            os.remove(filepath)   

    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)



@client.tree.command()
@app_commands.rename(word='word')
@app_commands.describe(word="The word to block")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def block(interaction: discord.Interaction, word: str):
    """Add a word to the blacklist"""
    is_deferred=True
    load_message = None
    try:        
        await interaction.response.defer(thinking=True, ephemeral=True)
        currentguildid = get_current_guild_id(interaction.guild.id)
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_DATABASE") + "/filters/addword/" + urllib.parse.quote(word) +"/"+urllib.parse.quote(currentguildid)

        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if (response.status == 200):
                    await interaction.followup.send(utils.translate(currentguildid,"Word added to the blacklist") + " ["+word+"]", ephemeral = True)
                else:
                    logging.error("[GUILDID : %s] block - Received bad response from APIs [word:%s]", str(currentguildid), word)
                    await interaction.followup.send("API Timeout, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)

            
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.rename(word='word')
@app_commands.describe(word="The word to unblock")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def unblock(interaction: discord.Interaction, word: str):
    """Remove a word from the blacklist"""
    is_deferred=True
    load_message = None
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        currentguildid = get_current_guild_id(interaction.guild.id)
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_DATABASE") + "/filters/deleteword/" + urllib.parse.quote(word) +"/"+urllib.parse.quote(currentguildid)

        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if (response.status == 200):
                    await interaction.followup.send(utils.translate(currentguildid,"Word removed from blacklist") + " ["+word+"]", ephemeral = True)
                else:
                    logging.error("[GUILDID : %s] unblock - Received bad response from APIs [word:%s]", str(currentguildid), word)
                    await interaction.followup.send("API Timeout, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)

            
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def unblockall(interaction: discord.Interaction):
    """Remove all the words from the blacklist"""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.user.guild_permissions.administrator:
            currentguildid = get_current_guild_id(interaction.guild.id)
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_DATABASE") + "/filters/deleteall/" +urllib.parse.quote(currentguildid)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        await interaction.followup.send(utils.translate(currentguildid,"All the words removed from blacklist"), ephemeral = True)
                    else:
                        logging.error("[GUILDID : %s] unblockall - Received bad response from APIs", str(currentguildid))
                        await interaction.followup.send("API Timeout, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
        else:        
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
            
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@client.tree.command()
@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.user.id))
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
async def reset(interaction: discord.Interaction):
    """Resets the bot database"""
    is_deferred=True
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        load_message = await display_loader(interaction, get_current_guild_id(interaction.guild.id))
        if interaction.user.guild_permissions.administrator:
            currentguildid = get_current_guild_id(interaction.guild.id)
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_DATABASE") + "/reset/" +urllib.parse.quote(currentguildid)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if (response.status == 200):
                        await interaction.followup.send(utils.translate(currentguildid,"All the sentences saved in the bot's database have been deleted"), ephemeral = True)
                    else:
                        logging.error("[GUILDID : %s] reset - Received bad response from APIs", str(currentguildid))
                        await interaction.followup.send("API Timeout, " + utils.translate(currentguildid,"please try again later"), ephemeral = True)
        else:        
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Only administrators can use this command"), ephemeral = True)
            
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred, load_message=load_message)


@admin.error
@accept.error
@avatar.error
@block.error
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
@translate.error
@stop.error
@unblock.error
@unblockall.error
@youtube.error
@wikipedia.error
async def on_generic_error(interaction: discord.Interaction, e: app_commands.AppCommandError):
    await send_error(e, interaction, from_generic=True)

client.run(os.environ.get("BOT_TOKEN"))

