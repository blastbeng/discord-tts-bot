const { SlashCommandBuilder } = require('@discordjs/builders');
const { EmbedBuilder, ButtonBuilder, ActionRowBuilder, ButtonStyle } = require('discord.js');
const { joinVoiceChannel, getVoiceConnection } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const config = require("../config.json");
const http = require("http");

const port=config.API_PORT;
const hostname=config.API_HOSTNAME;
const path_text=config.API_PATH_TEXT

module.exports = {
    data: new SlashCommandBuilder()
        .setName('quicktournament')
        .setDescription('Genera un torneo usando gli utenti connessi in chat (Min 3 - Max 16 Partecipanti)')
        .addIntegerOption(option => option.setName('size').setDescription('Dimensione dei Team').setRequired(true)),
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
                var errorMsg = "";
                

                var teamsize = interaction.options.getInteger('size');
                if (teamsize <= 0 || teamsize > 17) {                  
                    var errorMsg = "Errore! La grandezza del team non può essere inferiore o uguale a 0 o maggiore di 16!";
                    interaction.reply({ content: errorMsg, ephemeral: true });  
                    return
                }

                var arrayUsers = []
                var members = interaction.client.guilds.cache.get(config.GUILD_ID).channels.cache.get(interaction.member.voice.channelId).members;
                members.forEach((member) => {
                    //if (!member.user.bot) { 
                        var user_add = {
                            'id': member.user.id,
                            'username': member.user.username,
                            'image': member.user.displayAvatarURL()
                        }
                        arrayUsers.push(user_add);
                    //}
                });

                if(arrayUsers.length < 3){      
                    var errorMsg = "Errore! Sono connessi meno di 3 utenti al canale vocale! Impossibile generare un torneo!";
                    interaction.reply({ content: errorMsg, ephemeral: true });  
                    return
                }

                var tournamentData = { 
                    'author' : interaction.member.user.username, 
                    'author_image' : interaction.member.user.displayAvatarURL(), 
                    'guild_image' : interaction.member.guild.iconURL(), 
                    'teamsize' : teamsize,
                    'name' : 'TORNEO: Luridi Pezzenti n° ' + Math.floor(Math.random() * 9999), 
                    'description' : 'torneo generato automaticamente', 
                    'image' : interaction.member.guild.iconURL(), 
                    'users' : arrayUsers
                };

                var bodyData = JSON.stringify(tournamentData)

                const options = {
                    "method": "POST",
                    "hostname": hostname,
                    "port": port,
                    "path": path_text+'tournament',
                    "headers": {
                        'Content-Type': 'application/json',
                        "Content-Length": Buffer.byteLength(bodyData)
                    }
                }
                const req = http.request(options, function(res) {
                    
                    var chunks = [];
                    res.setEncoding('utf8');
                    req.on('error', function (error) {
                        console.error("ERRORE!", "["+ error + "]");
                        interaction.reply({ content: 'Si è verificato un errore', ephemeral: true }); 
                    });

                    res.on("data", function (chunk) {
                        chunks.push(chunk);
                    });
                
                    res.on("end", function() {
                        try {
                            var object = JSON.parse(chunks); 
                            var embed = new EmbedBuilder()
                            .setColor('#0099ff')
                            .setTitle(object.name)
                            .setAuthor({ name: object.author, iconURL: object.author_image, url: '' })
                            .setDescription(object.description)
                            .setThumbnail(object.image)


                            if(object.teamsize == 1){
                                embed.addField('PARTECIPANTI:', '\u200b', false);
                
                                //var fieldsUsers = [];              
                                //var fieldsTeams = [];           
                                //var fieldsRounds = []; 

                                var i = 0;
                                for (i = 0; i < object.users.length; i++) {
                                    var user = object.users[i];
                                    //var fieldsUser = { name: user.username, value: user.title, inline: true }
                                    //fieldsUsers.push(fieldsUser);     
                                    embed.addField(user.username, user.title, true)
                                }
                                
                                if (i%3 !== 0){
                                    while(i%3 !== 0) {
                                        //var fieldsUser = { name: '\u200b', value: '\u200b', inline: true }
                                        //fieldsUsers.push(fieldsUser);     
                                        embed.addField('\u200b', '\u200b', true)
                                        i = i + 1;
                                    }
                                }
                            }
                            if(object.teamsize > 1){
                                embed.addField('\u200b', 'SQUADRE', false)
                            }
                            var k = 0;
                            if (object.teamsize > 1) {
                                for (k = 0; k < object.teams.length; k++) {
                                    var team = object.teams[k];
                                    var users_add = "";
                                    for (var j = 0; j < team.users.length; j++) {
                                        var user = team.users[j];
                                        users_add = user.username + " " + users_add;                    
                                    }                  
                                    var teamName = "";   
                                    if ( team.name === 0) {
                                        teamName = team.users[0].title;
                                    } else {
                                        teamName = team.name;
                                    }
                                    //var fieldsTeam = { name: teamName, value: users_add, inline: true }
                                    //fieldsTeams.push(fieldsTeam);
                                    if(object.teamsize > 1){
                                        embed.addField(teamName, users_add, true)
                                    }
                                }                    
                                if (k%3 !== 0 && object.teamsize > 1){
                                    while(k%3 !== 0) {
                                        //var fieldsTeam = { name: '\u200b', value: '\u200b', inline: true }
                                        //fieldsTeams.push(fieldsTeam);    
                                        embed.addField('\u200b', '\u200b', true) 
                                        k = k + 1;
                                    }
                                }                            
                            }
                            embed.addField('\u200b', 'MATCH GENERATI', false)
                            var h = 0;
                            for (h = 0; h < object.rounds.length; h++) {
                                var round = object.rounds[h];
                                var teams = "";
                                teams = round.teams[0].name + "     VS     " + round.teams[1].name;

                                var user0 = "";
                                for (var j = 0; j < round.teams[0].users.length; j++) {
                                    var user = round.teams[0].users[j];
                                    user0 = user.username + " " + user0;                    
                                }  
                                var user1 = "";
                                for (var j = 0; j < round.teams[1].users.length; j++) {
                                    var user = round.teams[1].users[j];
                                    user1 = user.username + " " + user1;                    
                                }  

                                var users = user0 + "     VS     " + user1;
                                if (round.teams[0].name === 0 && round.teams[1].name === 0){
                                    //var fieldRound = { name: users, value: '\u200b', inline: false };
                                    //fieldsRounds.push(fieldRound);
                                    embed.addField(users, '\u200b', false) 
                                } else {                            
                                    //var fieldRound = { name: teams, value: users, inline: false };
                                    //fieldsRounds.push(fieldRound);
                                    embed.addField(teams, users, false) 
                                }
                            }
                            embed.setImage(object.image)
                                .setTimestamp()
                                .setFooter({ text: 'Creato da quel pezzente di '  + object.author, iconURL: object.guild_image });
                            const rowInfo1 = new ActionRowBuilder()
                            .addComponents(
                                new ButtonBuilder()
                                    .setCustomId('tournament_review1')
                                    .setLabel("QUESTA E' UN ANTEPRIMA, SOLO TU PUOI VEDERLO!")
                                    .setStyle(ButtonStyle.Danger)
                                    .setDisabled(true),
                            );
                            const rowInfo2 = new ActionRowBuilder()
                            .addComponents(
                                new ButtonBuilder()
                                    .setCustomId('tournament_review2')
                                    .setLabel("PREMI 'PUBBLICA' PER PUBBLICARE IL TORNEO")
                                    .setStyle(ButtonStyle.Danger)
                                    .setDisabled(true),
                            );
                            const rowInfo3 = new ActionRowBuilder()
                            .addComponents(
                                new ButtonBuilder()
                                    .setCustomId('tournament_review3')
                                    .setLabel("OPPURE 'RIGENERA' PER RIGENERARE LE SQUADRE")
                                    .setStyle(ButtonStyle.Danger)
                                    .setDisabled(true),
                            );
                            const row = new ActionRowBuilder()
                            .addComponents(
                                new ButtonBuilder()
                                    .setCustomId('tournament_regen')
                                    .setLabel('Rigenera')
                                    .setStyle(ButtonStyle.Primary),
                            )
                            .addComponents(
                                new ButtonBuilder()
                                    .setCustomId('tournament_publish')
                                    .setLabel('Pubblica')
                                    .setStyle(ButtonStyle.Primary),
                            )
                            interaction.reply({ ephemeral: true, embeds: [ embed ], components: [rowInfo1,rowInfo2,rowInfo3,row] });   
                        } catch (error) {
                            interaction.reply({ content: 'Si è verificato un errore', ephemeral: true });
                            console.error(error);
                        }
                    });
                
                });
                
                req.write(bodyData);
                req.end();
                        
                                    
            }
        }
};