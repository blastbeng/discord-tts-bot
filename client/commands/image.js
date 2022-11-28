const { SlashCommandBuilder } = require('@discordjs/builders');
const { joinVoiceChannel, getVoiceConnection  } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const config = require("../config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;

const path = config.CACHE_DIR;
const api=config.API_URL;
const path_image=config.API_PATH_IMAGE

module.exports = {
    data: new SlashCommandBuilder()
        .setName('image')
        .setDescription("Il pezzente cerca un'immagine")
        .addStringOption(option => option.setName('input').setDescription("L'immagine da cercare").setRequired(true)),
    async execute(interaction) {
            //interaction.deferReply({ ephemeral: true});
            const words = interaction.options.getString('input');    


            var params = api+path_image+"search/"+words;
            interaction.reply({ content: 'Il pezzente sta cercando: "' + words + '"', ephemeral: true }).then(data => { 
                try {
                    interaction.followUp({
                        content: interaction.user.username + ' ha cercato: "' + encodeURIComponent(words) + '"',
                        files: [{
                            attachment: params,
                            name: words+'.jpg'
                        }]
                    }).catch(function(error) {
                        console.error("ERRORE!", "["+ error + "]");
                        interaction.followUp({ content: 'Nessun immagine trovata', ephemeral: true });   
                    });
                } catch (error) {
                    console.error("ERRORE!", "["+ error + "]");
                    interaction.followUp({ content: 'Nessun immagine trovata', ephemeral: true });   
                } 

            }).catch(function(error) {
                console.error("ERRORE!", "["+ error + "]");
                interaction.reply({ content: 'Nessun immagine trovata', ephemeral: true });   
            });  

    }
}; 