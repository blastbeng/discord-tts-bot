const { SlashCommandBuilder } = require('@discordjs/builders');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
const fetch = require('node-fetch');

const path = config.CACHE_DIR;
const api=config.API_URL;
const text="&text=";
const path_text=config.API_PATH_TEXT
const GUILD_ID = config.GUILD_ID;

module.exports = {
    data: new SlashCommandBuilder()
        .setName('learn')
        .setDescription('Insegna qualcosa al pezzente')
        .addStringOption(option => option.setName('input').setDescription('Che cosa vuoi insegnare?').setRequired(true))
        .addStringOption(option => option.setName('definition').setDescription('Definizione').setRequired(true)),
    async execute(interaction) {
        const words = interaction.options.getString('input');
        const definition = interaction.options.getString('definition');

        if(!(new RegExp("([a-zA-Z0-9]+://)?([a-zA-Z0-9_]+:[a-zA-Z0-9_]+@)?([a-zA-Z0-9.-]+\\.[A-Za-z]{2,4})(:[0-9]+)?(/.*)?").test(words))
            && !(new RegExp("([a-zA-Z0-9]+://)?([a-zA-Z0-9_]+:[a-zA-Z0-9_]+@)?([a-zA-Z0-9.-]+\\.[A-Za-z]{2,4})(:[0-9]+)?(/.*)?").test(definition))
            && words.length <= 500 
            && definition.length <= 100){

            var guildid=""
            if(interaction.member.voice.guild.id === GUILD_ID){
                guildid="000000"
            }
            else{
                guildid = interaction.member.voice.guild.id
            }
            var params = api+path_text+"learn/"+encodeURIComponent(words)+"/"+encodeURIComponent(definition)+"/"+encodeURIComponent(guildid);

            fetch(
                params,
                {
                    method: 'GET',
                    headers: { 'Accept': '*/*' }
                }
            ).then(res => {
                interaction.reply({ content: 'Il pezzente ha imparato: '+words+" => "+definition, ephemeral: true });
            }); 
        } else {
            interaction.reply({ content: 'Ma che c**** scrivi?!', ephemeral: true });
        }
    }
}; 
