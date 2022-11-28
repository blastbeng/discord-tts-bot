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
        .setDescription('Il pezzente ti dice quali voci son disponibili per il comando /speak');
    return command;
}

module.exports = {
    data: getSlashCommand(),
    async execute(interaction) {
        await interaction.reply({ content: 'Carico la lista delle voci disponibili...' + "\nAd esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting", ephemeral: true });    
        try {                

            var resps="Ad esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting\n\n";

            const url = api+path_utils+"fakeyou/get_voices_by_cat/Italiano";

            const data = syncfetch(url).json();

            for(var attributename in data){
                resps += attributename + "\n"
            }
            await interaction.editReply(resps);
        } catch (error) {
            console.error("ERRORE!", "["+ error + "]");
            await interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });   
        }

    }

}; 