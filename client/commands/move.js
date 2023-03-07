const { SlashCommandBuilder } = require('@discordjs/builders');
require( 'console-stamp' )( console );
const fs = require('fs');
const syncfetch = require('sync-fetch')
const config = require("../config.json");
const fetch = require('node-fetch');

const path = config.CACHE_DIR;
const api=config.API_URL;
const text="&text=";
const path_text=config.API_PATH_TEXT
const path_utils=config.API_PATH_UTILS

function getSlashCommand() {
    const url = api+path_utils+"fakeyou/get_voices_by_cat/Italiano";
    try {
        data = syncfetch(url).json();
    } catch (error) {
         console.error("ERRORE!", "["+ error + "]");
         data = []
         data["errore"] = "errore"
    }

    var command = new SlashCommandBuilder()
        
        .setName('move')
        .setDescription("Sposta un utente da un canale ad un altro")
        .addStringOption(option =>{
            option.setName('user')
                .setDescription("L'utente da spostare")
                .setRequired(true)
                for(var attributename in data){
                    option.addChoices({ name: attributename, value: data[attributename] })
                }
                return option

            }
        )
        .addStringOption(option =>{
            option.setName('canale')
                .setDescription("Il canale in cui spostare l'utente")
                .setRequired(true)
                for(var attributename in data){
                    option.addChoices({ name: attributename, value: data[attributename] })
                }
                return option

            }
        );
    return command;
}

module.exports = {
    data: getSlashCommand(),
    async execute(interaction) {
        
        if (!interaction.member._roles.includes(config.ENABLED_ROLE)){
            interaction.reply({ content: "Non sei abilitato all'utilizzo di questo bot.", ephemeral: true });
        } else {

        }
    }
}; 
