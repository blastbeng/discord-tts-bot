const { SlashCommandBuilder } = require('@discordjs/builders');
const { ButtonBuilder, ActionRowBuilder, ButtonStyle } = require('discord.js');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
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
        .setName('generate')
        .setDescription('Il pezzente genera un audio partendo ripetendo il testo scritto')
        .addStringOption(option => option.setName('input').setDescription('Il testo da generare').setRequired(true))
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
                                        //var file = Math.random().toString(36).slice(2)+".wav";
                                        //var file = "temp.wav";
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
                                        file = file + ".wav";

                                        var outFile = path+"/"+file;
                                        const dest = fs.createWriteStream(outFile);
                                        res.body.pipe(dest);
                                        res.body.on('end', () => resolve());
                                        dest.on('error', reject);

                                        dest.on('finish', function(){      
                                            
                                            var outcontent = "Il pezzente ha generato l'audio\nAd esclusione di google, tutte le voci sono fornite da fakeyou con possibile Rate Limiting\nTesto: " 
                                                    + words 
                                                    + "  \nVoce: " 
                                                    + voicename;
                                            if (config.DOWNLOAD_ENABLED) {

                                                var url = config.DOWNLOAD_SERVER_URL + file;
                                                outcontent = outcontent + "\n--> [Download Link]("+url+") <--";
                                                outcontent = outcontent + "\nIl download sarà disponibile per due ore a partire da adesso";
                                                console.log("Il pezzente ha generato l'audio", "[username: " + interaction.member.user.username +"]", "[words: " + words +"]", "[voicename: "+ voicename +"]", "[url: "+ url +"]");  
                                        
                                            } else {

                                                console.log("Il pezzente ha generato l'audio", "[username: " + interaction.member.user.username +"]", "[words: " + words +"]", "[voicename: "+ voicename +"]");  
                                        
                                            }

                                            interaction.editReply({ content: outcontent, ephemeral: true });  

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
}; 