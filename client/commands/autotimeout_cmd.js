const { SlashCommandBuilder } = require('@discordjs/builders');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
const fetch = require('node-fetch');

const path = config.CACHE_DIR;
const api=config.API_URL;
const text="&text=";
const path_text=config.API_PATH_TEXT

module.exports = {
    data: new SlashCommandBuilder()
        .setName('autotimeout')
        .setDescription("Abilita o Disabilita il bot ad ascoltare tutto e rispondere a 'tono'")
        .addIntegerOption(option => option.setName('secs').setDescription('Tempo in secondi').setRequired(true)),
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
            const secs = interaction.options.getInteger('secs');
            if (secs < 30) {
                interaction.reply({ content: "Il timeout deve essere superiore a 30 secondi.", ephemeral: true });
            } else {
                config.AUTONOMOUS_TIMEOUT=(secs*1000);
                interaction.reply({ content: "Timeout impostato per la modalità automatica: " + secs + " secondi.", ephemeral: true });
            }
        }
    }
}; 
