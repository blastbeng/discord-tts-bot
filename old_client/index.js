const {
    Client,
    Intents,
    Collection,
    ActionRowBuilder, 
    ButtonBuilder,
    EmbedBuilder,
    ButtonStyle,
    GatewayIntentBits 
} = require('discord.js');
const { generateDependencyReport, joinVoiceChannel, getVoiceConnection, createAudioPlayer, VoiceConnectionStatus, entersState, createAudioResource } = require('@discordjs/voice');
const { addSpeechEvent } = require("discord-speech-recognition");
const {
    REST
} = require('@discordjs/rest');
const {
    Routes
} = require('discord-api-types/v9');
const fs = require('fs');
const findRemoveSync = require('find-remove');
const syncfetch = require('sync-fetch')
const config = require("./config.json");
require('events').EventEmitter.prototype._maxListeners = config.MAX_LISTENERS;
const http = require("http");
const wait = require('node:timers/promises').setTimeout;
require( 'console-stamp' )( console );
//const client = new Client({ intents: 32767 });
//const client = new Client({ intents: [32767, GatewayIntentBits.Guilds, GatewayIntentBits.GuildVoiceStates] });
const client = new Client({
	intents: [
		GatewayIntentBits.AutoModerationConfiguration,
		GatewayIntentBits.AutoModerationExecution,
		GatewayIntentBits.DirectMessageReactions,
		GatewayIntentBits.DirectMessageTyping,
		GatewayIntentBits.DirectMessages,
		GatewayIntentBits.GuildEmojisAndStickers,
		GatewayIntentBits.GuildIntegrations,
		GatewayIntentBits.GuildInvites,
		GatewayIntentBits.GuildMembers,
		GatewayIntentBits.GuildMessageReactions,
		GatewayIntentBits.GuildMessageTyping,
		GatewayIntentBits.GuildMessages,
		GatewayIntentBits.GuildPresences,
		GatewayIntentBits.GuildScheduledEvents,
		GatewayIntentBits.GuildVoiceStates,
		GatewayIntentBits.GuildWebhooks,
		GatewayIntentBits.Guilds,
		GatewayIntentBits.MessageContent
	],
});

addSpeechEvent(client, { lang: "it-IT", profanityFilter: false });

console.log(generateDependencyReport());

const cron = require('node-cron');

const TOKEN = config.BOT_TOKEN;
const path = config.CACHE_DIR;
const GUILD_ID = config.GUILD_ID;
const MESSAGES_CHANNEL_ID = config.MESSAGES_CHANNEL_ID;


cron.schedule('0 */5 * * * *', () => {
    var age_param = { seconds: 7200 };
    var extensions_param = '.mp3';
    findRemoveSync(config.CACHE_DIR, {
        age: age_param,
        extensions: extensions_param
      });
    //console.log("Deleting old mp3 files...", "[config.CACHE_DIR: " + config.CACHE_DIR +"]", "[age: " + JSON.stringify(age_param) +"]", "[extensions: "+ extensions_param +"]");  
                                               
});

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

const player = createAudioPlayer();

player.on('error', error => {
    console.error("ERRORE!", "["+ error + "]");  
});

const fetch = require('node-fetch');

const api=config.API_URL;
const port=config.API_PORT;
const hostname=config.API_HOSTNAME;
const path_audio=config.API_PATH_AUDIO;
const path_music=config.API_PATH_MUSIC;
const path_text=config.API_PATH_TEXT;
let lastSpeech = 0;

const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));

let playAsStream = true;


const commands = [];

client.commands = new Collection();

for (const file of commandFiles) {
    const command = require(`./commands/${file}`);
    //commands.push(command.data.toJSON());
    client.commands.set(command.data.name, command);
}

client.on('voiceStateUpdate', (oldMember, newMember) => {
  try{            
      if (newMember?.channelId) {
        client.channels.fetch(newMember?.channelId)
                .then(channel => {
            
                if (newMember?.channelId === config.ENABLED_CHANNEL_ID_1
                    || newMember?.channelId === config.ENABLED_CHANNEL_ID_2
                    || newMember?.channelId === config.ENABLED_CHANNEL_ID_3){   
                    const connection_old = getVoiceConnection(newMember?.guild.id);
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
                            channelId: newMember?.channelId,
                            guildId: newMember?.guild.id,
                            adapterCreator: channel.guild.voiceAdapterCreator,
                            selfDeaf: false,
                            selfMute: false
                        });
                } else {
                        connection = connection_old;
                }
            }
        }).catch(function(error) {
            console.error("ERRORE!", "["+ error + "]");
        });
      }
  } catch (error) {
      console.error(error);
  }
});

client.on("messageDelete", (messageDelete) => {

    if (messageDelete.channel.id === MESSAGES_CHANNEL_ID){
        console.log("Someone deleted:" + messageDelete.content);
        var params = api+path_text+"admin/forcedelete/bytext/"+encodeURIComponent(config.ADMIN_PASS)+"/"+encodeURIComponent(messageDelete.content);
        fetch(
        params,
            {
                method: 'GET',
                headers: { 'Accept': '*/*' }
            }
        ).catch(function(error) {
            console.error("ERRORE!", "["+ error + "]");
        });
    }

});
    

client.on("speech", (msg) => {

    try{
        let content = undefined;
        if( msg.content
            && msg.content !== null
            && msg.content !== ''
            && msg.content !== undefined) {
            content = msg.content;
        } 
             
        const connection = getVoiceConnection(msg.member?.voice.guild.id);
        if(connection !== null && connection !== undefined
            && config.ENABLED) {

            differenctMs = (new Date()).getTime() - lastSpeech;

            if ((config.AUTONOMOUS && (differenctMs > config.AUTONOMOUS_TIMEOUT))) {
                lastSpeech = (new Date()).getTime();
                

                //if ( content === undefined || content === null ) {
                //    var url = api+path_text+"random/";
                //    try {
                //        content = syncfetch(url).text();
                //    } catch (error) {
                //        console.error("ERRORE!", "["+ error + "]");
                //    } 
                //}

                var params = ""
                var guildid=""
                if(msg.guild.id === GUILD_ID){
                    guildid="000000"
                }
                else{
                    guildid = msg.guild.id
                }
                //params = api+path_audio+"ask/nolearn/random/"+encodeURIComponent(content.toLowerCase())+"/"+encodeURIComponent(guildid);
                params = api+path_audio+"random/google/"
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
                            var file = Math.random().toString(36).slice(2)+".mp3";
                            let outFile = path+"/"+file;
                            const dest = fs.createWriteStream(outFile);
                            res.body.pipe(dest);
                            res.body.on('end', () => resolve());
                            dest.on('error', reject);        
                            dest.on('finish', function(){     
                                let resource = createAudioResource(outFile);
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
                                
                            });
                        }).catch(function(error) {
                            console.error("ERRORE!", "["+ error + "]");
                        }); 
                    }
                }).catch(function(error) {
                    console.error("ERRORE!", "["+ error + "]");
                }); 
            } 
        }
      } catch (error) {
        console.error(error);
      }
    });





client.login(TOKEN);
