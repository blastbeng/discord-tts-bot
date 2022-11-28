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
const text="&text=";
const path_audio=config.API_PATH_AUDIO
const GUILD_ID = config.GUILD_ID;

module.exports = {
    data: new SlashCommandBuilder()
        .setName('ask')
        .setDescription('Chiedi o scrivi qualcosa al pezzente')
        .addStringOption(option => option.setName('input').setDescription('Che cosa vuoi chiedere?').setRequired(true)),
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
            //interaction.deferReply({ ephemeral: true});       

            const words = interaction.options.getString('input');
            
            if (words.length <= 500) {

                interaction.reply({ content: "Il pezzente sta generando l'audio", ephemeral: true }).then(data => {     

                    if(!(new RegExp("([a-zA-Z0-9]+://)?([a-zA-Z0-9_]+:[a-zA-Z0-9_]+@)?([a-zA-Z0-9.-]+\\.[A-Za-z]{2,4})(:[0-9]+)?(/.*)?").test(words))){
                        
                        var guildid=""
                        if(interaction.member.voice.guild.id === GUILD_ID){
                            guildid="000000"
                        }
                        else{
                            guildid = interaction.member.voice.guild.id
                        }
                        var params = api+path_audio+"ask/user/"+encodeURIComponent(interaction.member.user.username)+"/"+encodeURIComponent(words)+"/"+encodeURIComponent(guildid);

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
                                        interaction.editReply({ content: "Il pezzente sta rispondendo\nAd esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting\nTesto: " + words, ephemeral: true });    
                                        player.play(resource);      
                                        console.log("Il pezzente sta rispondendo", "[words: "+ words +"]");
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
                    } else {
                        interaction.editReply({ content: 'Ma che c**** scrivi?!', ephemeral: true });
                    }
                });
            } else {
                interaction.reply({ content: 'Errore! Caratteri massimi consentiti: 500', ephemeral: true });    
            }
        }
    }
}; 