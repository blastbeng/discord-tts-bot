const {
    Client,
    Intents,
    Collection,
    ActionRowBuilder, 
    ButtonBuilder,
    EmbedBuilder,
    ButtonStyle
} = require('discord.js');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer, createAudioResource, AudioPlayerStatus, StreamType  } = require('@discordjs/voice');
const { addSpeechEvent } = require("discord-speech-recognition");
const {
    REST
} = require('@discordjs/rest');
const {
    Routes
} = require('discord-api-types/v9');
const fs = require('fs');
const findRemoveSync = require('find-remove');
const config = require("./config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const http = require("http");
const wait = require('node:timers/promises').setTimeout;
require( 'console-stamp' )( console );
const client = new Client({ intents: 32767 });
addSpeechEvent(client, { lang: "it-IT", profanityFilter: false });

const TOKEN = config.BOT_TOKEN;
const path = config.CACHE_DIR;
const GUILD_ID = config.GUILD_ID;


const player = createAudioPlayer();
player.on('error', error => {
    console.error("ERRORE!", "["+ error + "]");  
});

const fetch = require('node-fetch');

const api=config.API_URL;
const port=config.API_PORT;
const hostname=config.API_HOSTNAME;
const path_audio=config.API_PATH_AUDIO
const path_music=config.API_PATH_MUSIC
const path_text=config.API_PATH_TEXT
let lastSpeech = 0;

//setInterval(findRemoveSync.bind(this, path, { extensions: ['.wav', '.mp3'] }), 21600000)

const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));


const commands = [];

client.commands = new Collection();

for (const file of commandFiles) {
    const command = require(`./commands/${file}`);
    //commands.push(command.data.toJSON());
    client.commands.set(command.data.name, command);
}

/**client.on('ready', () => {
    const rest = new REST({ version: '9' }).setToken(config.BOT_TOKEN);

    (async () => {
        try {
            console.log('Started refreshing application (/) commands.');

            await rest.put(
                Routes.applicationGuildCommands(config.BOT_ID, config.GUILD_ID),
                { body: commands },
            );

            console.log('Successfully reloaded application (/) commands.');
        } catch (error) {
            console.error(error);
        }
    })();
});*/

client.on('voiceStateUpdate', (oldMember, newMember) => {
  try{            
      if (newMember?.channelId) {
        client.channels.fetch(newMember?.channelId)
                .then(channel => {
          const connection_old = getVoiceConnection(newMember?.guild.id);
          if (connection_old !== null 
              && connection_old !== undefined
              && connection_old.joinConfig.channelId !== newMember?.channelId){
                  connection_old.destroy();
                  joinVoiceChannel({
                      channelId: newMember?.channelId,
                      guildId: newMember?.guild.id,
                      adapterCreator: channel.guild.voiceAdapterCreator,
                      selfDeaf: false,
                      selfMute: false
                  });
          } else if (connection_old === null 
              || connection_old === undefined){
                  joinVoiceChannel({
                      channelId: newMember?.channelId,
                      guildId: newMember?.guild.id,
                      adapterCreator: channel.guild.voiceAdapterCreator,
                      selfDeaf: false,
                      selfMute: false
                  });
          }
        }).catch(function(error) {
            console.error("ERRORE!", "["+ error + "]");
        });
      }
  } catch (error) {
      console.error(error);
  }
});

function postDeleteReply(interaction, msg) {
	return new Promise(resolve => {
        interaction.reply({ content: msg, ephemeral: false });  
		setTimeout(() => interaction.deleteReply(), 10000);
	});
}

function escapeRegExp(string){
    return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}



client.on('interactionCreate', async interaction => {
    try{
        if (!interaction.isSelectMenu() && !interaction.isCommand() && !interaction.isButton()) return;
        if (interaction.isCommand()){        
            const command = client.commands.get(interaction.commandName);
            if (!command) return;
            try {
                await command.execute(interaction);
            } catch (error) {
                if (error) console.error(error);
                await interaction.reply({ content: 'Errore!', ephemeral: true });
            }
        } else if (interaction.isButton()){
            if(interaction.customId === 'tournament_regen'){
                var tournamentData = { 
                    'author' : interaction.message.embeds[0].author.name, 
                    'name' : interaction.message.embeds[0].title, 
                    'description' : interaction.message.embeds[0].description
                };
                var bodyData = JSON.stringify(tournamentData)
                const options = {
                    "method": "POST",
                    "hostname": hostname,
                    "port": port,
                    "path": path_text+'tournament/regen',
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
            } else if(interaction.customId === 'tournament_publish'){
                await interaction.reply({ embeds: [ interaction.message.embeds[0] ], ephemeral: false });
            } else if(interaction.customId === 'stop'){
                const connection = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection !== null
                    && connection !== undefined){
                        connection.subscribe(player);
                        player.stop();
                        await interaction.reply({ content: 'Il pezzente ha smesso di riprodurre', ephemeral: true });
                    } else {
                        await interaction.reply({ content: 'Il pezzente non sta riproducendo nulla', ephemeral: true });
                    }
            } else if(interaction.customId === 'leave'){
                const connection = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection !== null
                    && connection !== undefined){
                        connection.destroy();
                        await interaction.reply({ content: 'Il pezzente è uscito dal canale', ephemeral: true });
                    } else {
                        await interaction.reply({ content: 'Il pezzente non si trova in nessun canale', ephemeral: true });
                    }
            }else if(interaction.customId === 'insult'){
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
    
                    var guildid=""
                    if(interaction.member.voice.guild.id === GUILD_ID){
                        guildid="000000"
                    }
                    else{
                        guildid = interaction.member.voice.guild.id
                    }
                    var params = api+path_audio+"insult?text=none&chatid="+encodeURIComponent(guildid);
    
    
                    fetch(
                        params,
                        {
                            method: 'GET',
                            headers: { 'Accept': '*/*' }
                        }
                    ).then(res => {
                        if(!res.ok) {
                            console.error("ERRORE!", text);    
                            interaction.editReply({ content: 'Si è verificato un errore', ephemeral: true });           
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
                                    console.log('Il pezzente sta insultando');
                                    interaction.editReply({ content: 'Il pezzente sta insultando', ephemeral: true });          
                                });
                            }).catch(function(error) {
                                console.error("ERRORE!", "["+ error + "]");
                                interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });   
                            }); 
                        }
                    }).catch(function(error) {
                        console.error("ERRORE!", "["+ error + "]");
                        interaction.reply({ content: 'Si è verificato un errore', ephemeral: true });   
                    }); 
                }
            }
        } else if (interaction.isSelectMenu()) {
            if(interaction.customId === 'videoselect'){
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
                    if (connection !== null
                        && connection !== undefined){
                        var video = interaction.values[0];
                        var params = api+path_music+'youtube/get?url='+encodeURIComponent(video);
                        await interaction.deferUpdate();
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
                                    var file = "youtube.mp3";
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
                                        console.log('youtube.mp3');
                                        const row = new ActionRowBuilder()
                                        .addComponents(
                                            new ButtonBuilder()
                                                .setCustomId('stop')
                                                .setLabel('Stop')
                                                .setStyle(ButtonStyle.Primary),
                                        );
                                        const options = {
                                            "method": "GET",
                                            "hostname": hostname,
                                            "port": port,
                                            "path": path_music+'youtube/info?url='+encodeURIComponent(video)
                                        }
                                        const req = http.request(options, function(res) {
                    
                                            var chunks = [];
                                        
                                            req.on('error', function (error) {
                                                console.error("ERRORE!", "["+ error + "]");
                                                interaction.reply({ content: 'Si è verificato un errore', ephemeral: true }); 
                                            });
                                            res.on("data", function (chunk) {
                                                chunks.push(chunk);
                                            });
                                        
                                            res.on("end", function() {
                                                try {
                                                    var body = Buffer.concat(chunks);
                                                    var object = JSON.parse(body.toString())
                                                    
                                                    const rowStop = new ActionRowBuilder()
                                                    .addComponents(
                                                        new ButtonBuilder()
                                                            .setCustomId('stop')
                                                            .setLabel('Stop')
                                                            .setStyle(ButtonStyle.Primary),
                                                    );
                                                    if (object.length === 0) {                                
                                                        interaction.editReply({ content: 'Il pezzente sta riproducendo', ephemeral: false, components: [rowStop] });  
                                                    } else {
                                                    var videores = object[0];
                                                    const embed = new EmbedBuilder()
                                                            .setColor('#0099ff')
                                                            .setTitle(videores.title)
                                                            .setURL(videores.link)
                                                            .setDescription(videores.link);
                                                    
                                                    interaction.editReply({ content: 'Il pezzente sta riproducendo', ephemeral: false, embeds: [embed], components: [rowStop] });  
                                                    }
                                                
                                                } catch (error) {
                                                    interaction.editReply({ content: 'Si è verificato un errore\n' + error.message, ephemeral: true });
                                                    console.error(error);
                                                }
                                            });
                                        
                                        });        
                                        
                                        req.end()  
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
                        await interaction.reply({ content: 'Si è verificato un errore', ephemeral: true });
                    }
                }
            }
        }
    } catch (error) {
        await interaction.reply({ content: 'Si è verificato un errore', ephemeral: true });
        console.error(error);
    }
});

client.on("messageCreate", (msg) => {
        try{            
            if (msg.channelId === '972093345306411010' && !msg.member?.user.bot) {
                msg.delete();
            }
            if (msg.member?.voice !== null
                && msg.member?.voice != undefined
                && msg.member?.voice.channel != null
                && msg.member?.voice.channel != undefined) {
                const connection_old = getVoiceConnection(msg.member?.voice.guild.id);
                if (connection_old !== null 
                    && connection_old !== undefined
                    && connection_old.joinConfig.channelId !== msg.member?.voice.channelId){
                        connection_old.destroy();
                        joinVoiceChannel({
                            channelId: msg.member?.voice.channel.id,
                            guildId: msg.member?.voice.channel.guild.id,
                            adapterCreator: msg.member?.voice.channel.guild.voiceAdapterCreator,
                            selfDeaf: false,
                            selfMute: false
                        });
                } else if (connection_old === null 
                    || connection_old === undefined){
                        joinVoiceChannel({
                            channelId: msg.member?.voice.channel.id,
                            guildId: msg.member?.voice.channel.guild.id,
                            adapterCreator: msg.member?.voice.channel.guild.voiceAdapterCreator,
                            selfDeaf: false,
                            selfMute: false
                        });
                }
            }
        } catch (error) {
            console.error(error);
        }
    });
  
    

client.on("speech", (msg) => {

    try{    
        const connection = getVoiceConnection(msg.member?.voice.guild.id);
        if(connection
            && msg.content !== null 
            && msg.content !== ''
            && msg.content !== undefined 
            && msg.content !== 'undefined'
            && config.ENABLED) {

            //var regex = '\\b';
            //regex += escapeRegExp(msg.content.toLowerCase());
            //regex += '\\b';

            var wordsss = msg.content.toLowerCase();

            //let randMinutes = Math.floor(Math.random() * 59);
            //let date_ob = new Date();
            //let minutes = date_ob.getMinutes();
            // TEST
            // randMinutes = date_ob.getMinutes();
            // TEST

            var bcAuto = false;
            var bcSpeech = false;

            if(config.AUTONOMOUS) {
                bcAuto = true;
            } else if (new RegExp('^pezzente', "i").test(wordsss) 
                || new RegExp('^scemo', "i").test(wordsss) 
                || new RegExp('^bot', "i").test(wordsss) 
                || new RegExp('^boat', "i").test(wordsss)) {
                bcSpeech = true;
            }
            


            differenctMs = (new Date()).getTime() - lastSpeech;

            if (new RegExp('^disabilita', "i").test(wordsss)
                || new RegExp('^disable', "i").test(wordsss)) {
                config.AUTONOMOUS = false;
            } else if ((bcAuto && (differenctMs > config.AUTONOMOUS_TIMEOUT)) || bcSpeech) {
                lastSpeech = (new Date()).getTime();
                    
                var words = msg.content.toLowerCase()
                if(!config.AUTONOMOUS){
                    words = msg.content.toLowerCase()
                    .replace(/pezzente/, "")
                    .replace(/scemo/, "")
                    .replace(/bot/, "")
                    .replace(/boat/, "")
                    .trim();
                }

                if (words === ''){
                    words = msg.content.toLowerCase();
                }

                var params = ""
                /**if(bcAuto) {
                    params = api+path_audio+"ask/"+config.AUTONOMOUS_TIMEOUT+"/"+words;
                } else {
                    params = api+path_audio+"ask/"+words;
                }*/
                var guildid=""
                if(msg.guild.id === GUILD_ID){
                    guildid="000000"
                }
                else{
                    guildid = msg.guild.id
                }
                params = api+path_audio+"ask/nolearn/random/"+encodeURIComponent(words)+"/"+encodeURIComponent(guildid);
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
                                player.play(createAudioResource(outFile, {
                                    inputType: StreamType.Arbitrary,
                                }));
                            });
                            //console.log("Speech running.", "[differenctMs: " + differenctMs +"]", "[bcSpeech: " + bcSpeech +"]", "[bcAuto: " +bcAuto +"]", "[config.AUTONOMOUS: " + config.AUTONOMOUS +"]", "[msg.content: " + msg.content +"]");
                        }).catch(function(error) {
                            console.error("ERRORE!", "["+ error + "]");
                        }); 
                    }
                }).catch(function(error) {
                    console.error("ERRORE!", "["+ error + "]");
                }); 
            } else if (msg.content.toLowerCase().includes('stop') || msg.content.toLowerCase().includes('ferma')) {
                    player.stop();
            //} else {
            //    console.log("Speech not running.", "[differenctMs: " + differenctMs +"]", "[bcSpeech: " + bcSpeech +"]", "[bcAuto: " +bcAuto +"]", "[config.AUTONOMOUS: " + config.AUTONOMOUS +"]", "[msg.content: " + msg.content +"]");
            } 
        }
      } catch (error) {
        console.error(error);
      }
    });

client.login(TOKEN);
