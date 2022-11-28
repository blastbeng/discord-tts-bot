const { SlashCommandBuilder } = require('@discordjs/builders');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer, createAudioResource, StreamType  } = require('@discordjs/voice');
const { ActionRowBuilder, SelectMenuBuilder } = require('discord.js');
const fs = require('fs');
const config = require("../config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const http = require("http");
require( 'console-stamp' )( console );
const path = config.CACHE_DIR;
const api=config.API_URL;
const port=config.API_PORT;
const hostname=config.API_HOSTNAME;
const path_music=config.API_PATH_MUSIC

module.exports = {
    data: new SlashCommandBuilder()
        .setName('youtube')
        .setDescription('Il pezzente riproduce audio da un video di youtube')
            .addStringOption(option => option.setName('video').setDescription('video da cercare').setRequired(true)),
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
       
            const video = interaction.options.getString('video');
            

                if ( video.startsWith('http')) {                    
                    interaction.reply({ content: 'Devi selezionare "link" se vuoi riprodurre un url di youtube', ephemeral: true });   
                } else {
                    interaction.deferReply({ ephemeral: true });
                    const options = {
                        "method": "GET",
                        "hostname": hostname,
                        "port": port,
                        "path": path_music+'youtube/search?text='+encodeURIComponent(video)
                    }
                    const req = http.request(options, function(res) {
                        
                        req.on('error', function (error) {
                            console.error("ERRORE!", "["+ error + "]");
                            interaction.reply({ content: 'Si è verificato un errore', ephemeral: true }); 
                        });
                        var chunks = [];
                    
                        res.on("data", function (chunk) {
                            chunks.push(chunk);
                        });
                    
                        res.on("end", function() {

                            try{
                                var body = Buffer.concat(chunks);
                                var object = JSON.parse(body.toString())
                                if (object.length === 0) {                                
                                    interaction.editReply({ content: 'Non ho trovato risultati per "'+video+'"', ephemeral: true});  
                                } else {
                                    var options = [];
                                    for (var i = 0; i < object.length && i < 25; i++) {
                                        var videores = object[i];
                                        var option = {};
                                        option.label = videores.title;
                                        option.description = videores.link;
                                        option.value = videores.link
                                        options.push(option);
                                    }
                                    
                                    const row = new ActionRowBuilder()
                                    .addComponents(
                                        new SelectMenuBuilder()
                                            .setCustomId('videoselect')
                                            .setPlaceholder('Seleziona un video da riprodurre')
                                            .addOptions(options),
                                    )
                                    interaction.editReply({ content: 'Qualcuno ha cercato "' + video + '" Seleziona un link da riprodurre',  ephemeral: true, components: [row] });     
                                }
                             
                            } catch (error) {
                                interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });
                                console.error(error);
                            }
                        });
                    
                    });
                    
                    req.end();
                }
        }

    }
}; 