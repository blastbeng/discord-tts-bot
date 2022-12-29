const { SlashCommandBuilder } = require('@discordjs/builders');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer, createAudioResource, StreamType  } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const player = createAudioPlayer();
const fetch = require('node-fetch');

const path = config.CACHE_DIR;
const api=config.API_URL;
const path_jokes_audio=config.API_PATH_JOKES_AUDIO

module.exports = {
    data: new SlashCommandBuilder()
        .setName('chuck')
        .setDescription('Chuck Norris.'),
    async execute(interaction) {
        if (!interaction.member._roles.includes(config.ENABLED_ROLE)){
            interaction.reply({ content: "Non sei abilitato all'utilizzo di questo bot.", ephemeral: true });
        } else if (interaction.member.voice === null 
            || interaction.member.voice === undefined 
            || interaction.member.voice.channelId === null 
            || interaction.member.voice.channelId === undefined ){
                interaction.reply({ content: 'Devi prima entrare in un canale vocale', ephemeral: true });
        } else if (interaction.member.voice !== null 
            && interaction.member.voice !== undefined 
            && interaction.member.voice.channelId !== null 
            && interaction.member.voice.channelId !== undefined
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_1
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_2
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_3){
                interaction.reply({ content: "Impossibile utilizzare questo comando in questo canale vocale.", ephemeral: true });
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
            //interaction.deferReply({ ephemeral: true});
            interaction.reply({ content: "Il pezzente sta generando l'audio", ephemeral: true }).then(data => {            

                var params = api+path_jokes_audio+"chuck";

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
                            var file = Math.random().toString(36).slice(2)+".mp3";
                            //var file = "temp.mp3";
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
                                interaction.editReply({ content: "Il pezzente sta rispondendo con una frase su Chuck Norris", ephemeral: true });    
                                player.play(resource);      
                                console.log("Il pezzente sta rispondendo con una frase su Chuck Norris");  
                            });
                        }).catch(function(error) {
                            console.error("ERRORE!", "["+ error + "]");
                            interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });   
                        }); 
                    }
                }).catch(function(error) {
                    console.error("ERRORE!", "["+ error + "]");
                    interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });   
                }); 
            });
        }

    }
}; 