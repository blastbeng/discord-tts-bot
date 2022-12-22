const { SlashCommandBuilder } = require('@discordjs/builders');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer, createAudioResource, StreamType  } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const player = createAudioPlayer();
const fetch = require('node-fetch');
const syncfetch = require('sync-fetch')
const GUILD_ID = config.GUILD_ID;

const path = config.CACHE_DIR;
const api=config.API_URL;
const text="&text=";
const path_audio=config.API_PATH_AUDIO
const path_utils=config.API_PATH_UTILS


function getSlashCommand() {

    var command = new SlashCommandBuilder()
        .setName('listvoices')
        .setDescription('Il pezzente ti dice quali voci son disponibili per i comandi /speak e /generate');
    return command;
}

module.exports = {
    data: getSlashCommand(),
    async execute(interaction) {
            
        if (interaction.member.voice === null 
            || interaction.member.voice === undefined 
            || interaction.member.voice.channelId === null 
            || interaction.member.voice.channelId === undefined ){
                interaction.reply({ content: 'Devi prima entrare in un canale vocale', ephemeral: true });
        } else if (interaction.member.voice !== null 
            && interaction.member.voice !== undefined 
            && interaction.member.voice.channelId !== null 
            && interaction.member.voice.channelId !== undefined
            && interaction.member.voice.channelId !== undefined
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_1
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_2
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_3){
                interaction.reply({ content: "Impossibile utilizzare questo comando in questo canale vocale.", ephemeral: true });
        } else {
            await interaction.reply({ content: 'Carico la lista delle voci disponibili...' + "\nAd esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting", ephemeral: true });    
            try {                

                var resps="Ad esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting\n\n";

                const url = api+path_utils+"fakeyou/get_voices_by_cat/Italiano";

                let data;
                try {
                    data = syncfetch(url).json();
                } catch (error) {
                     console.error("ERRORE!", "["+ error + "]");
                     data = []
                     data["errore"] = "errore"
                }

                for(var attributename in data){
                    resps += attributename + "\n"
                }
                await interaction.editReply(resps);
            } catch (error) {
                console.error("ERRORE!", "["+ error + "]");
                await interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });   
            }
        }
    }

}; 