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
        .setName('speech')
        .setDescription("Abilita o Disabilita l'attivazione vocale del bot'")
        .addBooleanOption(option => option.setName('bool').setDescription('True o False').setRequired(true)),
    async execute(interaction) {
        const bool = interaction.options.getBoolean('bool');
        if(bool){
            config.ENABLED=true;
            config.AUTONOMOUS=false;
            interaction.reply({ content: "L'attivazione vocale del pezzente è stata abilitata", ephemeral: true });
        } else {
            config.ENABLED=false;
            config.AUTONOMOUS=false;
            interaction.reply({ content: "L'attivazione vocale del pezzente è stata disabilitata", ephemeral: true });
        }
    }
}; 
