import os
import sys
import time
import urllib
import typing
import logging
import functools
from typing import Optional
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv


import discord
from discord import app_commands


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MY_GUILD = discord.Object(id=os.environ.get("GUILD_ID")) 


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await client.loop.run_in_executor(None, func)

async def random_sentences_loop(count: int):
    for i in range(count):
        time.sleep(30)
        client.voice_clients[0].play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/"), after=lambda e: print('Riproduco un audio causale ('+str(i)+')'))

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command()
async def join(interaction: discord.Interaction):
    """Entra dal canale."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            if client.voice_clients and client.voice_clients[0].channel.id != interaction.user.voice.channel.id:
                await client.voice_clients[0].disconnect()
                await interaction.user.voice.channel.connect()
            elif not client.voice_clients:
                await interaction.user.voice.channel.connect()
            await interaction.response.send_message("Entro nel canale", ephemeral = True)
        else:
            await interaction.response.send_message("Devi essere connesso a un canale vocale per usare questo comando", ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message("Attendi qualche istante", ephemeral = True)

#@client.tree.command()
#async def leave(interaction: discord.Interaction):
#    """Esce dal canale."""
#    try:
#        if interaction.user.voice and interaction.user.voice.channel:
#            if client.voice_clients and client.voice_clients[0].channel.id == interaction.user.voice.channel.id:
#                await client.voice_clients[0].disconnect()
#                await interaction.response.send_message("Esco dal canale", ephemeral = True)
#            else:
#                await interaction.response.send_message("Non mi trovo nel tuo canale vocale", ephemeral = True)       
#        else:
#            await interaction.response.send_message("Devi essere connesso a un canale vocale per usare questo comando", ephemeral = True)
#    except Exception as e:
#        exc_type, exc_obj, exc_tb = sys.exc_info()
#        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
#        await interaction.response.send_message("Attendi qualche istante", ephemeral = True)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text='Il testo da ripetere')
async def speak(interaction: discord.Interaction, text: str):
    """Ripete un testo."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            if client.voice_clients and client.voice_clients[0].channel.id != interaction.user.voice.channel.id:
                await client.voice_clients[0].disconnect()
                await interaction.user.voice.channel.connect()
            elif not client.voice_clients:
                await interaction.user.voice.channel.connect()
            
            client.voice_clients[0].play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"repeat/learn/"+urllib.parse.quote(str(text))+"/google/"), after=lambda e: print('Ho riprodotto: ' + text))

            await interaction.response.send_message("Riproduco: " + text, ephemeral = True)
        else:
            await interaction.response.send_message("Devi essere connesso a un canale vocale per usare questo comando", ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message("Attendi qualche istante", ephemeral = True)

@client.tree.command()
@app_commands.rename(text='text')
@app_commands.describe(text="L'oggetto o persona da insultare")
async def insult(interaction: discord.Interaction, text: str):
    """Ripete un testo."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            if client.voice_clients and client.voice_clients[0].channel.id != interaction.user.voice.channel.id:
                await client.voice_clients[0].disconnect()
                await interaction.user.voice.channel.connect()
            elif not client.voice_clients:
                await interaction.user.voice.channel.connect()
            
            client.voice_clients[0].play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult?text="+urllib.parse.quote(str(text))), after=lambda e: print('Ho insultato: ' + text))

            await interaction.response.send_message("Insulto: " + text, ephemeral = True)
        else:
            await interaction.response.send_message("Devi essere connesso a un canale vocale per usare questo comando", ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message("Attendi qualche istante", ephemeral = True)

@client.tree.context_menu(name='Insultalo!')
async def insult_tree(interaction: discord.Interaction, member: discord.Member):
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            if client.voice_clients and client.voice_clients[0].channel.id != interaction.user.voice.channel.id:
                await client.voice_clients[0].disconnect()
                await interaction.user.voice.channel.connect()
            elif not client.voice_clients:
                await interaction.user.voice.channel.connect()
            
            client.voice_clients[0].play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"insult?text="+urllib.parse.quote(str(member.name))), after=lambda e: print('Ho insultato: ' + member.name))

            await interaction.response.send_message("Insulto " + member.name, ephemeral = True)
        else:
            await interaction.response.send_message("Devi essere connesso a un canale vocale per usare questo comando", ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message("Attendi qualche istante", ephemeral = True)

@client.tree.command()
#@app_commands.rename(count='count')
#@app_commands.describe(count='Quante frasi riprodurre (Max 5)')
async def random(interaction: discord.Interaction):
    """Riproduce frasi casuali."""
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            if client.voice_clients and client.voice_clients[0].channel.id != interaction.user.voice.channel.id:
                await client.voice_clients[0].disconnect()
                await interaction.user.voice.channel.connect()
            elif not client.voice_clients:
                await interaction.user.voice.channel.connect()
            

            #if count > 5:
            #    count = 5
            client.voice_clients[0].play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/"), after=lambda e: print('Riproduco un audio causale (1)'))
            #if count > 1:
            #    await run_blocking(random_sentences_loop, count-1)
            await interaction.response.send_message("Riproduco un audio casuale", ephemeral = True)
        else:
            await interaction.response.send_message("Devi essere connesso a un canale vocale per usare questo comando", ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message("Attendi qualche istante", ephemeral = True)

@client.tree.context_menu(name='Frase casuale')
async def random_tree(interaction: discord.Interaction, member: discord.Member):
    try:
        if interaction.user.voice and interaction.user.voice.channel:
            if client.voice_clients and client.voice_clients[0].channel.id != interaction.user.voice.channel.id:
                await client.voice_clients[0].disconnect()
                await interaction.user.voice.channel.connect()
            elif not client.voice_clients:
                await interaction.user.voice.channel.connect()
                
            client.voice_clients[0].play(discord.FFmpegPCMAudio(os.environ.get("API_URL")+os.environ.get("API_PATH_AUDIO")+"random/"), after=lambda e: print('Riproduco un audio causale'))

            await interaction.response.send_message("Riproduco un audio casuale", ephemeral = True)
        else:
            await interaction.response.send_message("Devi essere connesso a un canale vocale per usare questo comando", ephemeral = True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
        await interaction.response.send_message("Attendi qualche istante", ephemeral = True)

#@client.tree.command()
#async def restart(interaction: discord.Interaction):
#    """Riavvia il bot."""
#    try:
#        await interaction.response.send_message("Riavvio il bot", ephemeral = True)
#        os.execv(sys.executable, ['python'] + sys.argv)
#    except Exception as e:
#        exc_type, exc_obj, exc_tb = sys.exc_info()
#        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
#        await interaction.response.send_message("Attendi qualche istante", ephemeral = True)



client.run(os.environ.get("BOT_TOKEN"))