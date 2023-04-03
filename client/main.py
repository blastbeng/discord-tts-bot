import os
import re
import sys
import json
import time
import utils
import signal
import random
import urllib
import typing
import base64
import asyncio
import logging
import pathlib
import requests
import database
import functools
import constants
import urllib.request
from PIL import Image
from contextlib import contextmanager
from typing import Literal, Optional
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv
import requests.exceptions
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Greedy, Context
from discord.errors import ClientException


from io import BytesIO
from utils import FFmpegPCMAudioBytesIO

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

GUILD_ID = discord.Object(id=os.environ.get("GUILD_ID"))

class MyClient(discord.Client):
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
        try:
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
                if not hasattr(voice_client, 'play') or not voice_client.is_connected():
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    await do_play(voice_client, self.audiourl, interaction, currentguildid, name = self.name)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)            
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False)

class SlashCommandButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, style, name):
        super().__init__(style=style, label="/"+name)
        self.name = name
    
    async def callback(self, interaction: discord.Interaction):
        try:
            if self.name == constants.ASK:
                await interaction.response.send_message("/ask <text> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot answers to your questions"), ephemeral = True)
            elif self.name == constants.CURSE:
                await curse_internal(interaction, "random")
            elif self.name == constants.INSULT:
                await insult_internal(interaction, None)
            elif self.name == constants.RANDOM:
                await random_internal(interaction, "random")
            elif self.name == constants.TIMER:
                await interaction.response.send_message("/timer <seconds> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"This is used to set the timer for the auto talking feature"), ephemeral = True)
            elif self.name == constants.SPEAK:
                await interaction.response.send_message("/speak <text> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot repeats something"), ephemeral = True)
            elif self.name == constants.TRANSLATE:
                await interaction.response.send_message("/translate <text> <language_to> <language_from[Optional]> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot translates a text"), ephemeral = True)
            elif self.name == constants.GENERATE:
                await generate_internal(interaction)
            elif self.name == constants.STORY:
                await story_internal(interaction)
            elif self.name == constants.ENABLE:
                await enable_internal(interaction)
            elif self.name == constants.DISABLE:
                await disable_internal(interaction)
            elif self.name == constants.JOIN:
                await join_internal(interaction)
            elif self.name == constants.LEAVE:
                await leave_internal(interaction)
            elif self.name == constants.LANGUAGE:
                await interaction.response.send_message("/language <language> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its main language"), ephemeral = True)
            elif self.name == constants.RENAME:
                await interaction.response.send_message("/rename <name> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its name"), ephemeral = True)
            elif self.name == constants.AVATAR:
                await interaction.response.send_message("/avatar <image> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot change its avatar"), ephemeral = True)
            elif self.name == constants.SOUNDRANDOM:
                await soundrandom_internal(interaction, "random")
            elif self.name == constants.SOUNDSEARCH:
                await interaction.response.send_message("/soundsearch <text> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"The bot searches and displays audio results, allowing you to play them"), ephemeral = True)
            elif self.name == constants.YOUTUBE:
                await interaction.response.send_message("/youtube <url> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Listen to a youtube song"), ephemeral = True)
            elif self.name == constants.VOTEMUTE:
                await interaction.response.send_message("/votemute <member> -> " + utils.translate(get_current_guild_id(interaction.guild.id),"Start a poll to mute someone for 60 seconds"), ephemeral = True)
            elif self.name == constants.STOP:
                await stop_internal(interaction)
            else:
                await interaction.response.send_message("Work in progress", ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False)


class StopButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Stop")
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            logging.info("stop - StopButton.callback.stop()")
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm interrupting the bot"), ephemeral = True)
            voice_client.stop()
            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)

class VoteButton(discord.ui.Button["InteractionRoles"]):

    def __init__(self, style, function, name, member, start_member):
        super().__init__(style=style, label=name)
        self.name = name
        self.style = style
        self.function = function
        self.member = member
        self.votes = {}
        self.votes[start_member] = 1
        self.ended = False
    
    async def callback(self, interaction: discord.Interaction):
        try:
            if self.function == constants.MUTE:
                if self.ended:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This poll has ended"), ephemeral = True)
                elif interaction.user.voice and interaction.user.voice.channel:
                    if not self.member.voice or not self.member.voice.channel:
                        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This user is not connected to any voice channel"), ephemeral = True)
                    elif self.member.voice and self.member.voice.channel and interaction.user.voice.channel != self.member.voice.channel:
                        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This user is not connected to your voice channel"), ephemeral = True)
                    elif interaction.user.name in self.votes:
                        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You have already voted"), ephemeral = True)
                    else:         
                        message = interaction.message
                        if message.embeds is not None and len(message.embeds) > 0:
                            embed = message.embeds[0]
                            if(self.style == discord.ButtonStyle.green):
                                self.votes[interaction.user.name] = 1
                                cyes = 0
                                for key in self.votes:
                                    if self.votes[key] == 1:
                                        cyes = cyes + 1
                                embed.set_field_at(1, name=embed.fields[1].name, value=str(cyes), inline=embed.fields[1].inline)
                            elif(self.style == discord.ButtonStyle.red):
                                self.votes[interaction.user.name] = 0
                                cno = 0
                                for key in self.votes:
                                    if self.votes[key] == 0:
                                        cno = cno + 1
                                embed.set_field_at(2, name=embed.fields[2].name, value=str(cno), inline=embed.fields[2].inline)
                            if int(embed.fields[1].value) >= int(embed.fields[0].value):                            
                                self.ended = True
                                if len(embed.fields) == 4:
                                    embed.set_field_at(3, name=utils.translate(get_current_guild_id(interaction.guild.id),"The poll has passed, I'm disabling " + self.member.name + "'s voice for 60 seconds"), value="", inline=False)
                                else: 
                                    embed.add_field(name=utils.translate(get_current_guild_id(interaction.guild.id),"The poll has passed, I'm disabling " + self.member.name + "'s voice for 60 seconds"), value="", inline=False)
                            elif int(embed.fields[2].value) >= int(embed.fields[0].value):                   
                                self.ended = True                 
                                if len(embed.fields) == 4:
                                    embed.set_field_at(3, name=utils.translate(get_current_guild_id(interaction.guild.id),"The poll hasn't passed"), value="", inline=False)
                                else: 
                                    embed.add_field(name=utils.translate(get_current_guild_id(interaction.guild.id),"The poll hasn't passed"), value="", inline=False)
                            await interaction.response.edit_message(embed=embed)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        except Exception as e:
            await send_error(e, interaction, from_generic=False)

intents = discord.Intents.default()
client = MyClient(intents=intents)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

logging.getLogger('discord').setLevel(int(os.environ.get("LOG_LEVEL")))

discord.utils.setup_logging(level=int(os.environ.get("LOG_LEVEL")), root=False)



def listvoices():
    try:
        voices = []
        url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/fakeyou/get_voices_by_cat/Italiano"
        response = requests.get(url)
        if (response.status_code == 200 and response.text != "Internal Server Error"):
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
        if (response.status_code == 200 and response.text != "Internal Server Error"):
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
    options.append(app_commands.Choice(name="Arabic", value="ar"))
    options.append(app_commands.Choice(name="Azeri", value="az"))
    options.append(app_commands.Choice(name="Chinese", value="zh"))
    options.append(app_commands.Choice(name="Czech", value="cs"))
    options.append(app_commands.Choice(name="Danish", value="da"))
    options.append(app_commands.Choice(name="Dutch", value="nl"))
    options.append(app_commands.Choice(name="German", value="de"))
    options.append(app_commands.Choice(name="Greek", value="el"))
    options.append(app_commands.Choice(name="English", value="en"))
    options.append(app_commands.Choice(name="Finnish", value="fi"))
    options.append(app_commands.Choice(name="French", value="fr"))
    options.append(app_commands.Choice(name="Hindi", value="hi"))
    options.append(app_commands.Choice(name="Hungarian", value="hu"))
    options.append(app_commands.Choice(name="Irish", value="ga"))
    options.append(app_commands.Choice(name="Italian", value="it"))
    options.append(app_commands.Choice(name="Japanese", value="ja"))
    options.append(app_commands.Choice(name="Korean", value="ko"))
    options.append(app_commands.Choice(name="Spanish", value="es"))
    options.append(app_commands.Choice(name="Persian", value="fa"))
    options.append(app_commands.Choice(name="Polish", value="pl"))
    options.append(app_commands.Choice(name="Portuguese", value="pt"))
    options.append(app_commands.Choice(name="Russian", value="ru"))
    options.append(app_commands.Choice(name="Swedish", value="sv"))
    options.append(app_commands.Choice(name="Turkish", value="tr"))
    options.append(app_commands.Choice(name="Ukrainian", value="uk"))

    return options

optionslanguages = get_languages_menu()

async def send_error(e, interaction, from_generic=False, is_deferred=False):
    currentguildid=get_current_guild_id(interaction.guild.id)
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
            await interaction.response.send_message(spaminteractionmsg)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("[GUILDID : %s] %s %s %s", currentguildid, exc_type, fname, exc_tb.tb_lineno, exc_info=1)
            await interaction.response.send_message(utils.translate(currentguildid,"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong.")+" blastbong#9151", ephemeral = True)
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("[GUILDID : %s] %s %s %s", currentguildid, exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        if is_deferred:
            await interaction.followup.send(utils.translate(currentguildid,"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong.")+" blastbong#9151", ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(currentguildid,"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong.")+" blastbong#9151", ephemeral = True)
    

def get_voice_client_by_guildid(voice_clients, guildid):
    for vc in voice_clients:
        if vc.guild.id == guildid:
            return vc
    return None

async def connect_bot_by_voice_client(voice_client, channel, guild):
    try:  
        if (voice_client and not voice_client.is_playing() and voice_client.channel and voice_client.channel.id != channel.id) or (not voice_client or not voice_client.channel):
            #if voice_client.is_connected():
            #    await voice_client.disconnect()
            await channel.connect()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def get_current_guild_id(guildid):
    if str(guildid) == str(os.environ.get("GUILD_ID")):
        return '000000' 
    else:
        return str(guildid)

async def do_play(voice_client, url: str, interaction: discord.Interaction, currentguildid: str, ephermeal = True, defer = True, name = None):
    try:
        if defer:
            await interaction.response.defer(thinking=True, ephemeral = ephermeal)
        response = requests.get(url)
        if (response.status_code == 200 and response.content and not voice_client.is_playing()):
            message = url
            if "X-Generated-Text" in response.headers:
                message = response.headers["X-Generated-Text"].encode('latin-1').decode('utf-8')
            elif name is not None:
                message = name
            voice_client.play(FFmpegPCMAudioBytesIO(response.content, pipe=True), after=lambda e: logging.info("do_play - " + message))
            view = discord.ui.View()
            view.add_item(StopButton())
            await interaction.followup.send(message, view = view, ephemeral = ephermeal)
        else:
            logging.error("[GUILDID : %s] do_play - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)), exc_info=1)
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong.")+" blastbong#9151", ephemeral = True)
    except ClientException as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        if defer:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)
    except Exception as ee:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        if defer:
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong.")+" blastbong#9151", ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong.")+" blastbong#9151", ephemeral = True)

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
                    if hasattr(voice_client, 'play') and voice_client.is_connected() and not voice_client.is_playing():
                        response = requests.get(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/random/000000")
                        if (response.status_code == 200 and response.content):
                            message = 'play_audio_loop - random - ' + response.headers["X-Generated-Text"].encode('latin-1').decode('utf-8')
                            voice_client.play(FFmpegPCMAudioBytesIO(response.content, pipe=True), after=lambda e: logging.info(message))
                #elif voice_client is not None and voice_client.channel is not None:
                #    await voice_client.disconnect()
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

        #await play_audio_loop.start()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        raise Exception(e)

@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if message.embeds is not None and len(message.embeds) > 0:
        if message.embeds[0].title == constants.MUTE:
            embed = discord.Embed.from_data(message.embeds[0])
            reactok = get(message.reactions, emoji="✅")
            reactko = get(message.reactions, emoji="❌")
            if reactok and reactok.count > int(embed.fields[0].value):
                targetuser = message.mentions[0]
                await targetuser.edit(mute=True)
                await message.delete()
                await client.send_message(channel, "✅ " + constants.MUTE + " [" + message.mentions[0] + "]" + utils.translate(get_current_guild_id(message.guild.id), "Poll has passed"))
                await unmute_user(targetuser, 60)
            elif reactko and reactko.count > int(embed.fields[0].value):
                await message.delete()
                await client.send_message(channel, "❌ " + constants.MUTE + " [" + message.mentions[0] + "]" + utils.translate(get_current_guild_id(message.guild.id), "Poll has failed"))
              

@client.event
async def on_voice_state_update(member, before, after):
    try:
        if after.channel is not None:
            voice_client = get_voice_client_by_guildid(client.voice_clients, member.guild.id)
            await connect_bot_by_voice_client(voice_client, after.channel, None)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

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
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def join(interaction: discord.Interaction):
    """Join channel."""
    await join_internal(interaction)

async def join_internal(interaction):
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"I'm joining the voice channel"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def leave(interaction: discord.Interaction):
    """Leave channel"""
    await leave_internal(interaction)
    
async def leave_internal(interaction):
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
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The sentence to repeat")
@app_commands.rename(language='language')
@app_commands.describe(language="The language to use")
@app_commands.choices(language=optionslanguages)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def speak(interaction: discord.Interaction, text: str, language: app_commands.Choice[str] = "Italian"):
    """Repeat a sentence"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if not hasattr(voice_client, 'play') and voice_client.is_connected():
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():

                currentguildid = get_current_guild_id(interaction.guild.id)

                lang_to_use = ""
                if hasattr(language, 'name'):
                    lang_to_use = language.value
                else:
                    lang_to_use = utils.get_guild_language(currentguildid)
                url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(lang_to_use)
                await do_play(voice_client, url, interaction, currentguildid)


            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(text='text')
@app_commands.describe(text="the sentence to ask")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def ask(interaction: discord.Interaction, text: str):
    """Ask something."""
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                
                if not hasattr(voice_client, 'play') and voice_client.is_connected():
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    
                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"ask/"+urllib.parse.quote(str(text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                    await do_play(voice_client, url, interaction, currentguildid)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

                
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)



@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def generate(interaction: discord.Interaction):
    """Generate a random sentence."""
    await generate_internal(interaction)

async def generate_internal(interaction):
    is_deferred=False
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                
                if not hasattr(voice_client, 'play') and voice_client.is_connected():
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    currentguildid = get_current_guild_id(interaction.guild.id)

                    await interaction.response.defer(thinking=True, ephemeral=True)
                    is_deferred=True
                    url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/sentences/generate/" + urllib.parse.quote(currentguildid) + "/0"
                    response = requests.get(url)
                    if (response.status_code == 200 and response.text != "Internal Server Error"):
                        url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(response.text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                        await do_play(voice_client, url, interaction, currentguildid, defer=False)
                    else:
                        logging.error("[GUILDID : %s] generate - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)), exc_info=1)
                        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong."), ephemeral = True)     
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.user.id))
async def story(interaction: discord.Interaction):
    """Generate a random story."""
    await story_internal(interaction)

async def story_internal(interaction):
    is_deferred=False
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                
                if not hasattr(voice_client, 'play') and voice_client.is_connected():
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    currentguildid = get_current_guild_id(interaction.guild.id)
                    await interaction.response.defer(thinking=True, ephemeral=True)
                    is_deferred=True
                    url = os.environ.get("API_URL") + os.environ.get("API_PATH_UTILS") + "/paragraph/generate/" + urllib.parse.quote(currentguildid)
                    response = requests.get(url)
                    if (response.status_code == 200 and response.text != "Internal Server Error"):
                        url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/"+urllib.parse.quote(str(response.text))+"/google/"+urllib.parse.quote(currentguildid)
                        await do_play(voice_client, url, interaction, currentguildid, defer=False)
                    else:
                        logging.error("[GUILDID : %s] story - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)), exc_info=1)
                        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong.")+" blastbong#9151", ephemeral = True)         

                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(member='member')
@app_commands.describe(member="The user to insult")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def insult(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Insult someone"""
    await insult_internal(interaction, member)

async def insult_internal(interaction, member):
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if not hasattr(voice_client, 'play') or not voice_client.is_connected():
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

                await do_play(voice_client, insulturl, interaction, currentguildid)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.context_menu(name="Insult")
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def insult_tree(interaction: discord.Interaction, member: discord.Member):
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if not hasattr(voice_client, 'play') or not voice_client.is_connected():
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():
                currentguildid = get_current_guild_id(interaction.guild.id)
                url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult?text="+urllib.parse.quote(str(member.name))+ "&chatid="+urllib.parse.quote(currentguildid) + "&language=" + urllib.parse.quote(utils.get_guild_language(currentguildid))
                await do_play(voice_client, url, interaction, currentguildid)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.choices(voice=optionsvoices)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def random(interaction: discord.Interaction, voice: Optional[app_commands.Choice[str]] = "random"):
    """Say a random sentence"""
    await random_internal(interaction, voice)

async def random_internal(interaction, voice):
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                if not hasattr(voice_client, 'play') or not voice_client.is_connected():
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    voicename = None

                    if hasattr(voice, 'name'):
                        voicename = str(get_voice_code(voice.name))
                    else:
                        voicename = voice
                    currentguildid = get_current_guild_id(interaction.guild.id)

                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/"+urllib.parse.quote(voicename)+"/"+urllib.parse.quote(currentguildid)
                    await do_play(voice_client, url, interaction, currentguildid)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(voice='voice')
@app_commands.describe(voice="The voice to use")
@app_commands.choices(voice=optionsvoices)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def curse(interaction: discord.Interaction, voice: Optional[app_commands.Choice[str]] = "random"):
    """Curse."""
    await curse_internal(interaction, voice)

async def curse_internal(interaction, voice):
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
                await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

                if not hasattr(voice_client, 'play') or not voice_client.is_connected():
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
                elif not voice_client.is_playing():
                    voicename = None

                    if hasattr(voice, 'name'):
                        voicename = str(get_voice_code(voice.name))
                    else:
                        voicename = voice
                    
                    currentguildid = get_current_guild_id(interaction.guild.id)

                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"curse/"+urllib.parse.quote(voicename)+"/"+urllib.parse.quote(currentguildid)
                    await do_play(voice_client, url, interaction, currentguildid)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
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
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def stop(interaction: discord.Interaction):
    """Stop playback."""
    await stop_internal(interaction)

@client.tree.context_menu(name="Stop")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def stop_tree(interaction: discord.Interaction, member: discord.Member):
    await stop_internal(interaction)

async def stop_internal(interaction: discord.Interaction):
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
        await send_error(e, interaction, from_generic=False)

    

@client.tree.command()
@app_commands.rename(name='name')
@app_commands.describe(name="New bot nickname (20 chars limit)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def rename(interaction: discord.Interaction, name: str):
    """Rename bot."""
    try:
        if len(name) < 20:
            currentguildid = get_current_guild_id(interaction.guild.id)
            
            message = interaction.user.mention + " " + utils.translate(currentguildid," renamed me to") + ' "'+name+'"'
            name = name + " [" + utils.get_guild_language(currentguildid) + "]"
            await interaction.guild.me.edit(nick=name)
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"My name can't be that longer (20 chars limit)"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(image='image')
@app_commands.describe(image="New bot avatar")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
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
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.rename(language='language')
@app_commands.describe(language="New bot language")
@app_commands.choices(language=optionslanguages)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
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
        await send_error(e, interaction, from_generic=False)

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
    is_deferred=False
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            if not hasattr(voice_client, 'play') or not voice_client.is_connected():
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():

                currentguildid = get_current_guild_id(interaction.guild.id)

                lang_to_use_from = ""
                if hasattr(language_from, 'name'):
                    lang_to_use_from = language_from.value
                else:
                    lang_to_use_from = utils.get_guild_language(currentguildid)

                await interaction.response.defer(thinking=True, ephemeral=True)
                is_deferred=True
                translation = requests.get(os.environ.get("API_URL") + os.environ.get("API_PATH_TEXT") + "translate/" + urllib.parse.quote(lang_to_use_from) + "/" + urllib.parse.quote(language_to.value) + "/" + urllib.parse.quote(text) + "/" + urllib.parse.quote(currentguildid))
                if (translation.text != "Internal Server Error" and translation.status_code == 200):
                    translated_text = translation.text
                    url = os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(translated_text))+"/google/"+urllib.parse.quote(currentguildid)+ "/" + urllib.parse.quote(language_to.value)
                    await do_play(voice_client, url, interaction, currentguildid, defer=False)
                else:
                    logging.error("[GUILDID : %s] translate - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)), exc_info=1)
                    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong.") + " blastbong#9151", ephemeral = True)
                
                    
                
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.rename(url='url')
@app_commands.describe(url="Youtube link (Must match https://www.youtube.com/watch?v=1abcd2efghi)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def youtube(interaction: discord.Interaction, url: str):
    """Play a youtube link"""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)
            
            if not hasattr(voice_client, 'play') or not voice_client.is_connected():
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():

                if "watch?v=" in url:
                    currentguildid = get_current_guild_id(interaction.guild.id)

                    urlapi = os.environ.get("API_URL")+os.environ.get("API_PATH_MUSIC")+"youtube/get/"+(url.split("watch?v=",1)[1])+"/"+urllib.parse.quote(currentguildid)
                    await do_play(voice_client, urlapi, interaction, currentguildid, ephermeal = False)
                else:
                    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"URL must match something like https://www.youtube.com/watch?v=1abcd2efghi"), ephemeral = True)
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)

            
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def enable(interaction: discord.Interaction):
    """Enable auto talking feature."""
    await enable_internal(interaction)

@client.tree.context_menu(name="Enable")
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def enable_tree(interaction: discord.Interaction, member: discord.Member):
    await enable_internal(interaction)

async def enable_internal(interaction):
    is_deferred=False
    try:
        if not play_audio_loop.is_running():
            await interaction.response.defer(thinking=True, ephemeral=True)
            is_deferred=True
            play_audio_loop.start()
            logging.info("enable - play_audio_loop.start()")
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Enabling the auto mode"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Auto mode is already enabled"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred = is_deferred)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def disable(interaction: discord.Interaction):
    """Disable auto talking feature."""
    await disable_internal(interaction)

@client.tree.context_menu(name="Disable")
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def disable_tree(interaction: discord.Interaction, member: discord.Member):
    await disable_internal(interaction)

async def disable_internal(interaction: discord.Interaction):
    is_deferred=False
    try:
        if play_audio_loop.is_running():
            await interaction.response.defer(thinking=True, ephemeral=True)
            is_deferred=True
            play_audio_loop.stop()
            logging.info("disable - play_audio_loop.stop()")
            play_audio_loop.cancel()
            logging.info("disable - play_audio_loop.cancel()")
            await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Disabling the auto mode"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Auto mode is already disabled"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

@client.tree.command()
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.rename(seconds='seconds')
@app_commands.describe(seconds="Timeout seconds (Min 20 - Max 600)")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
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
        await send_error(e, interaction, from_generic=False)




@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def soundrandom(interaction: discord.Interaction, text: Optional[str] = "random"):
    """Play a random sound from the soundboard."""
    await soundrandom_internal(interaction, text)

async def soundrandom_internal(interaction: discord.Interaction, text: Optional[str] = "random"):
    """Play a random sound from the soundboard."""
    is_deferred=False
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            
            if not hasattr(voice_client, 'play') or not voice_client.is_connected():
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            elif not voice_client.is_playing():
                currentguildid = get_current_guild_id(interaction.guild.id)

                await interaction.response.defer(thinking=True, ephemeral=True)
                is_deferred=True
                url = os.environ.get("API_URL") + os.environ.get("API_PATH_SOUNDBOARD") + "/random/" + urllib.parse.quote(str(text)) + "/" + urllib.parse.quote(currentguildid)
                response = requests.get(url)
                if (response.status_code == 200 and response.json()):
                    name = response.json()['name']
                    url = response.json()['url']
                    await do_play(voice_client, url, interaction, currentguildid, defer=False, name=name)
                else:
                    if text == "random":
                        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I haven't found any results "), ephemeral = True)   
                    else:
                        await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"I haven't found any results ") + " [" + text + "]", ephemeral = True)     
            else:
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment or use stop command"), ephemeral = True)
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to search")
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def soundsearch(interaction: discord.Interaction, text: Optional[str] = "random"):
    """Search for sounds on the soundboard."""
    is_deferred=False
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            voice_client = get_voice_client_by_guildid(client.voice_clients, interaction.guild.id)
            await connect_bot_by_voice_client(voice_client, interaction.user.voice.channel, interaction.guild)

            
            #if not hasattr(voice_client, 'play'):
            #    await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"Retry in a moment, I'm initializing the voice connection..."), ephemeral = True)
            #elif not voice_client.is_playing():
            currentguildid = get_current_guild_id(interaction.guild.id)

            await interaction.response.defer(thinking=True, ephemeral = True)
            is_deferred=True            
            url = os.environ.get("API_URL") + os.environ.get("API_PATH_SOUNDBOARD") + "/query/" + urllib.parse.quote(str(text)) + "/" + urllib.parse.quote(currentguildid)
            response = requests.get(url)
            if (response.status_code == 200 and response.text != "Internal Server Error"):
                view = discord.ui.View()
                for element in response.json():
                    button = SoundBoardButton(element['name'], element['url'])
                    view.add_item(button)
                await interaction.followup.send(text, view=view, ephemeral = True)   
            else:
                logging.error("[GUILDID : %s] soundboard - Received bad response from APIs", currentguildid, exc_info=1)
                if text == "random":
                    await interaction.followup.send(utils.translate(currentguildid,"I haven't found any results "), ephemeral = True)   
                else:
                    await interaction.followup.send(utils.translate(currentguildid,"I haven't found any results ") + " [" + text + "]", ephemeral = True)   
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"You must be connected to a voice channel to use this command"), ephemeral = True)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)

#@client.tree.command()
#@app_commands.rename(member='member')
#@app_commands.describe(member="The user to mute")
#@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.user.id))
#async def votemute(interaction: discord.Interaction, member: discord.Member):
#    """Vote to mute someone for 60 seconds"""
#    try:
#        currentguildid = get_current_guild_id(interaction.guild.id)
#        if interaction.user.voice and interaction.user.voice.channel:
#            if not member.voice or not member.voice.channel:
#                await interaction.response.send_message(utils.translate(currentguildid,"This user is not connected to any voice channel"), ephemeral = True)
#            elif member.voice and member.voice.channel and interaction.user.voice.channel != member.voice.channel:
#                await interaction.response.send_message(utils.translate(currentguildid,"This user is not connected to your voice channel"), ephemeral = True)
#            else:
#                votes = 0
#                
#                for cmember in interaction.user.voice.channel.members:
#                    if not cmember.bot:
#                        votes = votes + 1
#
#                title=constants.MUTE
#                description=utils.translate(currentguildid,"Someone started a poll")
#                embed=discord.Embed(title=title, description=description, color=0xd10a07)
#                embed.add_field(name=utils.translate(currentguildid,"Votes required to close the poll"), value=str((int(1/2))+1), inline=False)
#                embed.add_field(name=utils.translate(currentguildid,"Positive votes:"), value="1", inline=True)
#                embed.add_field(name=utils.translate(currentguildid,"Negative votes:"), value="0", inline=True)
#                message = utils.translate(currentguildid,"disable " + member.mention + "'s voice for 60 seconds?")
#                view = discord.ui.View()
#                view.add_item(VoteButton(discord.ButtonStyle.green, constants.MUTE, utils.translate(currentguildid,"Yes"), member, interaction.user.name))
#                view.add_item(VoteButton(discord.ButtonStyle.red, constants.MUTE, utils.translate(currentguildid,"No"), member, interaction.user.name))
#                await interaction.response.send_message(message, embed=embed, view=view, ephemeral = True)
#        else:
#            await interaction.response.send_message(utils.translate(currentguildid,"You must be connected to a voice channel to use this command"), ephemeral = True)
#    except Exception as e:
#        await send_error(e, interaction, from_generic=False)


@client.tree.command()
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
async def commands(interaction: discord.Interaction):
    """Show bot commands."""
    try:     
        view = discord.ui.View()
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
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
        

        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")): 
            view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.ASK))
        
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.SPEAK))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.TRANSLATE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.LANGUAGE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.RENAME))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.TIMER))  
        #view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.VOTEMUTE))  


        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")): 
            view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.AVATAR))

        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.SOUNDSEARCH))
        view.add_item(SlashCommandButton(discord.ButtonStyle.primary, constants.YOUTUBE))
        view.add_item(SlashCommandButton(discord.ButtonStyle.red, constants.STOP))

        await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"These are the bot's commands"), view = view, ephemeral = False)
    except Exception as e:
        await send_error(e, interaction, from_generic=False)


@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="The text to generate")
@app_commands.guilds(discord.Object(id=os.environ.get("GUILD_ID")))
@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.user.id))
async def text2image(interaction: discord.Interaction, text: str):
    """Generate an image from text"""
    is_deferred=False
    try:
        if str(interaction.guild.id) == str(os.environ.get("GUILD_ID")):
            try:
                r = requests.get(os.environ.get("STABLE_DIFFUSION_API_URL"))
                r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"The remote APIs are currently offline. blastbong#9151 must power on his powerful Notebook"), ephemeral = False)
            else:
                currentguildid = get_current_guild_id(interaction.guild.id)
                await interaction.response.defer(thinking=True, ephemeral=False)
                is_deferred=True
                payload = {
                    "prompt": text,
                    "steps": 50,
                    "width": 512,
                    "height": 512,
                    "batch_size": 1,
                    "sampler_index": "Euler"
                }
                url = os.environ.get("STABLE_DIFFUSION_API_URL") + os.environ.get("STABLE_DIFFUSION_API_TEXT_2_IMG")
                response = requests.post(url, json=payload)
                if (response.status_code == 200 and response.text != "Internal Server Error"):
                    r = response.json()
                    for i in r['images']:
                        image = Image.open(BytesIO(base64.b64decode(i.split(",",1)[0])))
                    with BytesIO() as image_binary:
                        image.save(image_binary, 'PNG')
                        image_binary.seek(0)
                        file = discord.File(fp=image_binary, filename='text2image.png')
                    await interaction.followup.send(text, ephemeral = False, file=file)     
                else:
                    logging.error("[GUILDID : %s] generate - Received bad response from APIs", str(get_current_guild_id(interaction.guild.id)), exc_info=1)
                    await interaction.followup.send(utils.translate(get_current_guild_id(interaction.guild.id),"Error. Something dumb just happened. You can try to contact the dev and ask what's wrong."), ephemeral = False)     
        else:
            await interaction.response.send_message(utils.translate(get_current_guild_id(interaction.guild.id),"This is a private command and can only be used by members with specific permissions on the main Bot Server"), ephemeral = False)
    except Exception as e:
        await send_error(e, interaction, from_generic=False, is_deferred=is_deferred)


@ask.error
@avatar.error
@commands.error
@curse.error
@disable.error
@disable_tree.error
@enable.error
@enable_tree.error
@generate.error
@insult.error
@insult_tree.error
@join.error
@language.error
@leave.error
@random.error
@rename.error
@soundrandom.error
@soundsearch.error
@speak.error
@story.error
@text2image.error
@timer.error
@translate.error
@stop.error
#@votemute.error
@youtube.error
async def on_generic_error(interaction: discord.Interaction, e: app_commands.AppCommandError):
    await send_error(e, interaction, from_generic=True)

client.run(os.environ.get("BOT_TOKEN"))

