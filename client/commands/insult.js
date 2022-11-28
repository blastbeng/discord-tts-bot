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
const hostname=config.API_HOSTNAME;
const api=config.API_URL;
const port=config.API_PORT;
const path_audio=config.API_PATH_AUDIO
const path_text=config.API_PATH_TEXT
const GUILD_ID = config.GUILD_ID;


module.exports = {
    data: new SlashCommandBuilder()
        .setName('insult')
        .setDescription('Il pezzente insulta qualcuno')        
        .addUserOption(option => option.setName('user')
        	.setDescription('Chi vuoi insultare? (Puoi lasciare vuoto)')
		.setRequired(true)),
    async execute(interaction) {

        
        const user = interaction.options.getUser('user');
        var words = null;
        if (user !== null && user !== undefined){
            words = interaction.options.getUser('user').username;
        }

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
                interaction.reply({ content: "Il pezzente sta generando l'audio", ephemeral: true }).then(data => {    

                    var guildid=""
                    if(interaction.member.voice.guild.id === GUILD_ID){
                        guildid="000000"
                    }
                    else{
                        guildid = interaction.member.voice.guild.id
                    }

                    var params = "";
                    if (words === null || words === undefined){
                        params = api+path_audio+"insult?text=none&chatid="+encodeURIComponent(guildid);
                    } else {
                        params = api+path_audio+"insult?text="+encodeURIComponent(words)+"&chatid="+encodeURIComponent(guildid);
                    }




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
                                    player.play(resource);      
                                    interaction.editReply({ content: 'Il pezzente sta insultando', ephemeral: true });  
                                    console.log("Il pezzente sta insultando");          
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
