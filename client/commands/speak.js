const { SlashCommandBuilder } = require('@discordjs/builders');
const { ButtonBuilder, ActionRowBuilder, ButtonStyle } = require('discord.js');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer, createAudioResource, StreamType  } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const player = createAudioPlayer();
const fetch = require('node-fetch');
const syncfetch = require('sync-fetch')
const GUILD_ID = config.GUILD_ID;

const path = config.CACHE_DIR;
const api=config.API_URL;
const text="&text=";
const path_audio=config.API_PATH_AUDIO
const path_utils=config.API_PATH_UTILS
let data;


function getSlashCommand() {
    const url = api+path_utils+"fakeyou/get_voices_by_cat/Italiano";
    data = syncfetch(url).json();

    var command = new SlashCommandBuilder()
        .setName('speak')
        .setDescription('Il pezzente parla ripetendo il testo scritto')
        .addStringOption(option => option.setName('input').setDescription('Il testo da ripetere').setRequired(true))
        .addStringOption(option =>{
            option.setName('voice')
                .setDescription('La voce da usare')
                .setRequired(false)


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

            var voicetoken = interaction.options.getString('voice');

            if (voicetoken === undefined || voicetoken === null){
                voicetoken = "google";
                voicename = "google";
            } else {
                voicename = Object.keys(data).find(key => data[key] === voicetoken);
            }

            try{            

                if (words.length <= 500) {

                    interaction.reply({ content: "Il pezzente sta generando l'audio\nAd esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting\nTesto: " + words + "  \nVoce: " + voicename, ephemeral: true }).then(data => {    

                        if(voicetoken === "") {
                            
                            interaction.editReply({ content: 'Si è verificato un errore \nTesto: ' + words + '  \nVoce: ' + voicename, ephemeral: true });     
                            } else {

                            var guildid=""
                            if(interaction.member.voice.guild.id === GUILD_ID){
                                guildid="000000"
                            }
                            else{
                                guildid = interaction.member.voice.guild.id
                            }

                            

                            var params = api+path_audio+"repeat/learn/user/"+encodeURIComponent(interaction.member.user.username)+"/"+encodeURIComponent(words)+"/"+encodeURIComponent(guildid)+"/"+encodeURIComponent(voicetoken);

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
                                        const row = new ActionRowBuilder()
                                        .addComponents(
                                            new ButtonBuilder()
                                                .setCustomId('errore')
                                                .setLabel("ERRORE! Attendi almeno altri 30 secondi.")
                                                .setStyle(ButtonStyle.Danger)
                                                .setDisabled(true));

                                        interaction.editReply({ content: "Testo: " + words + " \nVoce: " + voicename + "\n\n" + text, ephemeral: true, components: [row] });
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
                                                const row = new ActionRowBuilder()
                                                .addComponents(
                                                    new ButtonBuilder()
                                                        .setCustomId('errore')
                                                        .setLabel("ERRORE! Attendi almeno altri 30 secondi.")
                                                        .setStyle(ButtonStyle.Danger)
                                                        .setDisabled(true));
                                                        
                                                interaction.editReply({ content: "Testo: " + words + " \nVoce: " + voicename + "\n\n" + error.message, ephemeral: true, components: [row] });      
                                            });
                                            interaction.editReply({ content: "Il pezzente sta parlando\nAd esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting\nTesto: " + words + "  \nVoce: " + voicename, ephemeral: true });    
                                            player.play(resource);
                                            console.log("Il pezzente sta parlando", "[username: " + interaction.member.user.username +"]", "[words: " + words +"]", "[voicename: "+ voicename +"]");  
                                        });
                                    }).catch(function(error) {
                                        console.error("ERRORE!", "["+ error + "]");
                                        const row = new ActionRowBuilder()
                                        .addComponents(
                                            new ButtonBuilder()
                                                .setCustomId('errore')
                                                .setLabel("ERRORE! Attendi almeno altri 30 secondi.")
                                                .setStyle(ButtonStyle.Danger)
                                                .setDisabled(true));
                                                
                                        interaction.editReply({ content: "Testo: " + words + " \nVoce: " + voicename + "\n\n" + error.message, ephemeral: true, components: [row] }); 
                                    }); 
                                }
                            }).catch(function(error) {
                                console.error("ERRORE!", "["+ error + "]");
                                const row = new ActionRowBuilder()
                                .addComponents(
                                    new ButtonBuilder()
                                        .setCustomId('errore')
                                        .setLabel("ERRORE! Attendi almeno altri 30 secondi.")
                                        .setStyle(ButtonStyle.Danger)
                                        .setDisabled(true));
                                        
                                interaction.editReply({ content: "Testo: " + words + " \nVoce: " + voicename + "\n\n" + error.message, ephemeral: true, components: [row] });  
                            }); 

                            
                        }
                    });
                } else {
                    interaction.reply({ content: 'Errore! Caratteri massimi consentiti: 500', ephemeral: true });    
                }
            } catch (error) {
                console.error("ERRORE!", "["+ error + "]");
                const row = new ActionRowBuilder()
                .addComponents(
                    new ButtonBuilder()
                        .setCustomId('errore')
                        .setLabel("ERRORE! Attendi almeno altri 30 secondi.")
                        .setStyle(ButtonStyle.Danger)
                        .setDisabled(true));
                        
                interaction.editReply({ content: "Testo: " + words + " \nVoce: " + voicename + "\n\n" + error.message, ephemeral: true, components: [row] });  
            }
        }

    }
}; 