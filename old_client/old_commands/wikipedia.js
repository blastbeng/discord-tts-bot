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
const http = require("http");
const { createReadStream } = require('fs')

const path = config.CACHE_DIR;
const port=config.API_PORT;
const hostname=config.API_HOSTNAME;
const api=config.API_URL;
const path_audio=config.API_PATH_AUDIO
const path_text=config.API_PATH_TEXT
const MESSAGES_CHANNEL_ID = config.MESSAGES_CHANNEL_ID;

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
        .setName('wikipedia')
        .setDescription('Il pezzente cerca qualcosa su wikipedia')      
        .addStringOption(option => option.setName('input').setDescription('Che cosa vuoi cercare?').setRequired(true)),
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

                    var guildid=""
                    if(interaction.member.voice.guild.id === GUILD_ID){
                        guildid="000000"
                    }
                    else{
                        guildid = interaction.member.voice.guild.id
                    }
                    
                    connection = joinVoiceChannel({
                        channelId: interaction.member.voice.channelId,
                        guildId: guildid,
                        adapterCreator: interaction.guild.voiceAdapterCreator,
                        selfDeaf: false,
                        selfMute: false
                    });
                } else {
                    connection = connection_old;
                }

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
                                        interaction.editReply({ content: "Il pezzente ha cercato su Wikipedia: "+words, ephemeral: true });          
                                        //console.log("Il pezzente ha cercato su Wikipedia:", words);       

                                        var params = api+path_text+"lastsaid/"+encodeURIComponent(words)+"/"+encodeURIComponent(guildid);
                                        fetch(
                                            params,
                                            {
                                                method: 'GET',
                                                headers: { 'Accept': '*/*' }
                                            }
                                        ).then((result) => result.text())
                                        .then((res) => {
                                            try {
                                                interaction.client.guilds.cache.get(config.GUILD_ID).channels.cache.get(MESSAGES_CHANNEL_ID).send(res);
                                            } catch (error) {
                                                console.error("ERRORE!", "["+ error + "]");
                                            }
                                        }).catch(function(error) {
                                            console.error("ERRORE!", "["+ error + "]");
                                        });              
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
