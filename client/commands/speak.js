const { SlashCommandBuilder } = require('@discordjs/builders');
const { ButtonBuilder, ActionRowBuilder, ButtonStyle } = require('discord.js');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer, NoSubscriberBehavior, createAudioResource, StreamType  } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
//require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const player = createAudioPlayer({
	behaviors: {
		noSubscriber: NoSubscriberBehavior.Play,
	},
});
const fetch = require('node-fetch');
const syncfetch = require('sync-fetch')
const { createReadStream } = require('fs')
const GUILD_ID = config.GUILD_ID;

const path = config.CACHE_DIR;
const api=config.API_URL;
const text="&text=";
const path_audio=config.API_PATH_AUDIO
const path_text=config.API_PATH_TEXT
const path_utils=config.API_PATH_UTILS
const MESSAGES_CHANNEL_ID = config.MESSAGES_CHANNEL_ID;
let data;

let playAsStream = true;

function getSlashCommand() {
    const url = api+path_utils+"fakeyou/get_voices_by_cat/Italiano";
    try {
        data = syncfetch(url).json();
    } catch (error) {
         console.error("ERRORE!", "["+ error + "]");
         data = []
         data["errore"] = "errore"
    }

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

                            

                            var params = api+path_audio+"repeat/learn/user/"+encodeURIComponent(interaction.member.user.username)+"/"+encodeURIComponent(words)+"/"+encodeURIComponent(voicetoken)+"/"+encodeURIComponent(guildid);

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
                                        //var file = Math.random().toString(36).slice(2)+".mp3";
                                        //var file = "temp.mp3";
                                        var file = words;
                                        if(file.length > 50){
                                            file = file.substring(0,50);
                                        }
                                        file = file.replace(/[^\w\s\']|_/g, "")
                                                        .replace(/\s+/g, " ")
                                                        .split(' ')
                                                        .join('_');
                                        file = file + "__";
                                        file = file + voicename.replace(/[^\w\s\']|_/g, "")
                                                        .replace(/\s+/g, " ")
                                                        .split(' ')
                                                        .join('_');
                                        file = file + ".mp3";

                                        var outFile = path+"/"+file;
                                        const dest = fs.createWriteStream(outFile);
                                        res.body.pipe(dest);
                                        res.body.on('end', () => resolve());
                                        dest.on('error', reject);

                                        dest.on('finish', function(){      
                                            const subscription = connection.subscribe(player);     
                                            
                                            let resource;
                                            if (playAsStream) {
                                                resource = createAudioResource(createReadStream(outfile), {
                                                    inputType: StreamType.Arbitrary,
                                                });
                                            playAsStream = false;
                                            } else {
                                                resource = createAudioResource(outfile, {
                                                    inputType: StreamType.Arbitrary,
                                                });
                                            }          
                                            
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
                                            var outcontent = "Il pezzente sta parlando\nAd esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting\nTesto: " 
                                                    + words 
                                                    + "  \nVoce: " 
                                                    + voicename;
                                            
                                            if (config.DOWNLOAD_ENABLED) {

                                                var url = config.DOWNLOAD_SERVER_URL + file;
                                                outcontent = outcontent + "\n--> [Download Link]("+url+") <--";
                                                outcontent = outcontent + "\nIl download sarà disponibile per due ore a partire da adesso";
                                                console.log("Il pezzente sta parlando", "[username: " + interaction.member.user.username +"]", "[words: " + words +"]", "[voicename: "+ voicename +"]", "[url: "+ url +"]");  
                                                
                                            } else {
        
                                                console.log("Il pezzente sta parlando", "[username: " + interaction.member.user.username +"]", "[words: " + words +"]", "[voicename: "+ voicename +"]");  
                                                
                                            }

                                            interaction.editReply({ content: outcontent, ephemeral: true });    


                                            player.play(resource);
                                            if(subscription) {
                                                setTimeout(() => subscription.unsubscribe(), 15000)
                                            }  

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
                                                    channel = interaction.client.guilds.cache.get(config.GUILD_ID).channels.cache.get(MESSAGES_CHANNEL_ID);
                                                    if (res === undefined || res === "") {
                                                        console.error("ERRORE!", "[res is empty]");
                                                    } else if (channel === undefined ) {
                                                        console.error("ERRORE!", "[channel is empty]");
                                                    } else {
                                                        channel.send(res);
                                                    }
                                                } catch (error) {
                                                    console.error("ERRORE!", "["+ error + "]");
                                                }
                                            }).catch(function(error) {
                                                console.error("ERRORE!", "["+ error + "]");
                                            }); 
                                            
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
