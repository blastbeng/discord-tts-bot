const { SlashCommandBuilder } = require('@discordjs/builders');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer, createAudioResource, VoiceConnectionStatus, entersState } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
//require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const player = createAudioPlayer();
player.on('error', error => {
    console.error("ERRORE!", "["+ error + "]");   
});   
const fetch = require('node-fetch');
const { createReadStream } = require('fs')


const path = config.CACHE_DIR;
const api=config.API_URL;
const path_jokes_audio=config.API_PATH_JOKES_AUDIO


let connection;

function unsubscribeConnection() {
    if ( connection !== null
        && connection !== undefined 
        && connection.state !== null 
        && connection.state !== undefined 
        && connection.state.subscription !== null
        && connection.state.subscription !== undefined) {
        connection.state.subscription.unsubscribe();
    } 
}


module.exports = {
    data: new SlashCommandBuilder()
        .setName('joke')
        .setDescription('barzelletta a caso'),
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
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_3
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_4){
                interaction.reply({ content: "Impossibile utilizzare questo comando in questo canale vocale.", ephemeral: true });
        } else {
            const connection_old = getVoiceConnection(interaction.member.voice.guild.id);
            if ((connection_old === undefined 
                || connection_old === null) 
                || 
                (connection_old !== null 
                && connection_old !== undefined
                && connection_old.joinConfig.channelId !== interaction.member.voice.channelId)){
                    if (connection_old !== undefined 
                        && connection_old !== null) {
                            connection_old.destroy();
                        }
            
                connection = joinVoiceChannel({
                    channelId: interaction.member.voice.channelId,
                    guildId: interaction.guildId,
                    adapterCreator: interaction.guild.voiceAdapterCreator,
                    selfDeaf: false,
                    selfMute: false
                });
            } else {
                connection = connection_old;
            }
            //interaction.deferReply({ ephemeral: true});
            interaction.reply({ content: "Il pezzente sta generando l'audio", ephemeral: true }).then(data => {        

                var params = api+path_jokes_audio+"random";

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
                            let outFile = path+"/"+file;
                            const dest = fs.createWriteStream(outFile);
                            res.body.pipe(dest);
                            res.body.on('end', () => resolve());
                            dest.on('error', reject);        

                            dest.on('finish', function(){  
                                let resource = createAudioResource(outFile); //let resource = createAudioResource(createReadStream(outFile));
                                if ( connection !== null 
                                    && connection !== undefined
                                    && connection.state !== null  
                                    && connection.state !== undefined
                                    && connection.state.subscription !== null 
                                    && connection.state.subscription !== undefined
                                    && connection.state.subscription.player !== null 
                                    && connection.state.subscription.player !== undefined){
                                        connection.state.subscription.player.play(resource);
                                } else {
                                    connection.subscribe(player);
                                    player.play(resource);
                                }


                                //setTimeout(() => unsubscribeConnection(), 15_000)
                                interaction.editReply({ content: "Il pezzente sta rispondendo con qualche disagiata", ephemeral: true });  
                                console.log("Il pezzente sta rispondendo con qualche disagiata");    
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