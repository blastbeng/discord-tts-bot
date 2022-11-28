const { SlashCommandBuilder } = require('@discordjs/builders');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer, createAudioResource, StreamType  } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const player = createAudioPlayer();
const fetch = require('node-fetch');
const http = require("http");

const path = config.CACHE_DIR;
const port=config.API_PORT;
const hostname=config.API_HOSTNAME;
const api=config.API_URL;
const path_audio=config.API_PATH_AUDIO
const path_text=config.API_PATH_TEXT
module.exports = {
    data: new SlashCommandBuilder()
        .setName('wikipedia')
        .setDescription('Il pezzente cerca qualcosa su wikipedia')      
        .addStringOption(option => option.setName('input').setDescription('Che cosa vuoi cercare?').setRequired(true)),
    async execute(interaction) {     

            if (interaction.member.voice === null 
                || interaction.member.voice === undefined 
                || interaction.member.voice.channelId === null 
                || interaction.member.voice.channelId === undefined ){
                    interaction.reply({ content: 'Devi prima entrare in un canale vocale', ephemeral: true });
            } else {
                var connection = null;
                const connection_old = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection_old !== null 
                    && connection_old !== undefined
                    && connection_old.joinConfig.channelId !== interaction.member.voice.channelId){
                    connection_old.destroy();
                } else {
                    connection = connection_old;
                }
                
                connection = joinVoiceChannel({
                    channelId: interaction.member.voice.channelId,
                    guildId: interaction.guildId,
                    adapterCreator: interaction.guild.voiceAdapterCreator,
                    selfDeaf: false,
                    selfMute: false
                });

                const words = interaction.options.getString('input');

                if (words.length <= 500) {
                    
                    interaction.reply({ content: "Il pezzente sta generando l'audio", ephemeral: true }).then(data => {          

                        var params = api+path_audio+"search/"+encodeURIComponent(words);

                        fetch(
                            params,
                            {
                                method: 'GET',
                                headers: { 'Accept': '*/*' }
                            }
                        ).then(res => {
                            if(!res.ok) {
                                res.text().then((text) => {
                                    console.error("ERRORE!", text);
                                    interaction.editReply({ content: "Errore!: \n\n" + text, ephemeral: true });
                                });    
                            } else {
                                new Promise((resolve, reject) => {
                                    var file = Math.random().toString(36).slice(2)+".wav";
                                    //var file = "temp.wav";
                                    var outFile = path+"/"+file;
                                    const dest = fs.createWriteStream(outFile);
                                    res.body.pipe(dest);
                                    res.body.on('end', () => resolve());
                                    dest.on('error', reject);        

                                    dest.on('finish', function(){       
                                        connection.subscribe(player);                     
                                        const resource = createAudioResource(outFile, {
                                            inputType: StreamType.Arbitrary,
                                        });
                                        player.on('error', error => {
                                            console.error("ERRORE!", "["+ error + "]");
                                            interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });     
                                        });
                                        
                                        player.on('error', error => {
                                            console.error("ERRORE!", "["+ error + "]");
                                            interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });     
                                        });
                                        player.play(resource);
                                        interaction.editReply({ content: "Il pezzente ha cercato su Wikipedia: "+words, ephemeral: true });          
                                        console.log("Il pezzente ha cercato su Wikipedia:", words);                    
                                    });
                                }).catch(function(error) {
                                    console.error("ERRORE!", "["+ error + "]");
                                    interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });   
                                }); 
                            }
                        }).catch(function(error) {
                            console.error("ERRORE!", "["+ error + "]");
                            interaction.editReply({ content: 'Si è verificato un errore', ephemeral: true });   
                        }); 
                    });
                } else {
                    interaction.reply({ content: 'Errore! Caratteri massimi consentiti: 500', ephemeral: true });    
                }
            }

    }
}; 
