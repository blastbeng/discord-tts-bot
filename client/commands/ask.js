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
const text="&text=";
const path_audio=config.API_PATH_AUDIO
const path_text=config.API_PATH_TEXT
const GUILD_ID = config.GUILD_ID;
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
        .setName('ask')
        .setDescription('Chiedi o scrivi qualcosa al pezzente')
        .addStringOption(option => option.setName('input').setDescription('Che cosa vuoi chiedere?').setRequired(true)),
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
        }else {
            const connection_old = getVoiceConnection(interaction.member.voice.guild.id);
            if ((connection_old === undefined 
                || connection_old === null) 
                || 
                (connection_old !== null 
                && connection_old !== undefined
                && connection_old.joinConfig.channelId !== newMember?.channelId)){
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

                    connection.on(VoiceConnectionStatus.Disconnected, async (oldState, newState) => {
                        try {
                            await Promise.race([
                                entersState(connection, VoiceConnectionStatus.Signalling, 5_000),
                                entersState(connection, VoiceConnectionStatus.Connecting, 5_000),
                            ]);
                            // Seems to be reconnecting to a new channel - ignore disconnect
                        } catch (error) {
                            // Seems to be a real disconnect which SHOULDN'T be recovered from
                            connection.destroy();
                        }
                    });
                } else {
                    connection = connection_old;
                }
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
                                    var file = Math.random().toString(36).slice(2)+".mp3";
                                    //var file = "temp.mp3";
                                    let outFile = path+"/"+file;
                                    const dest = fs.createWriteStream(outFile);
                                    res.body.pipe(dest);
                                    res.body.on('end', () => resolve());
                                    dest.on('error', reject);        

                                    dest.on('finish', function(){               
                                        let resource = createAudioResource(outFile); //let resource = createAudioResource(createReadStream(outFile));
                                        interaction.editReply({ content: "Il pezzente sta rispondendo\nAd esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting\nTesto: " + words, ephemeral: true });    
                                        
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


                                        setTimeout(() => unsubscribeConnection(), 15_000) 
                                        console.log("Il pezzente sta rispondendo", "[words: "+ words +"]");

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