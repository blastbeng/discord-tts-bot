const { Client, LocalAuth, MessageMedia, MediaFromURLOptions } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const config = require("./config.json");
const axios = require('axios');
const fs = require('fs');
const ERROR_MSG = "Schifo, bestemmia e disagio.\nSi é verificato un errore stronzo.\nChiedere a blast di sistemare.\nSe ha voglia lo farà."


const client = new Client({
    authStrategy: new LocalAuth({ dataPath: `${process.cwd()}/config/wacache` }),
    puppeteer: {
        args: ['--no-sandbox']
    }
});

client.initialize();

client.on('loading_screen', (percent, message) => {
    console.log('LOADING SCREEN', percent, message);
});

client.on('qr', qr => {
    console.log('QR RECEIVED', qr);
    qrcode.generate(qr, {small: true});
});

client.on('authenticated', () => {
    console.log('AUTHENTICATED');
});

client.on('auth_failure', msg => {
    // Fired if session restore was unsuccessful
    console.error('AUTHENTICATION FAILURE', msg);
});

client.on('disconnected', (reason) => {
    console.log('Client was logged out', reason);
})

client.on('ready', () => {
    console.log('READY');
});

client.on('message', async msg => {
    let chat = await msg.getChat();

    let canReply = false;

    if (chat.isGroup) {
        for (let i = 0; i < chat.participants.length; i++) {
            if (chat.participants[i].id.user === config.TEL_NUMBER){
                canReply = true;
            }
        }
    }


    if (canReply) { 
        if (msg.body == '/help' || msg.body.startsWith('/help')) {
            let message = msg.body.slice(5);
            helpmsg = "Lista Comandi: \n- /ask: chiedimi qualcosa\n- /speak: fammi ripetere qualcosa\n- /random: frase casuale\n /random <testo>: frase casuale dato un testo"
            if ( message.length === 0 ) {
                await msg.reply(helpmsg);
            } else {
                await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nNon é necessario scrivere niente dopo /help per visualizzare i comandi disponibili.\n\n" + helpmsg);
            }

        } else if (msg.body == '/random' || msg.body.startsWith('/random')) {
            url = config.API_URL + "chatbot_text/random/000000/"
            let message = msg.body.slice(7);
            if ( message.length !== 0 ) {
                url = config.API_URL + "chatbot_text/random/000000/" + encodeURI(message)
            } 
            await replyMsg(url, msg)    
        } else if (msg.body.startsWith('/ask/000000/it')) {
            let message = msg.body.slice(4);
            if ( message.length !== 0 ) {
                await replyMsg(config.API_URL + "chatbot_text/ask/" + message + "/", msg)
            } else {
                await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nSe devi chiedermi qualcosa devi scrivere un testo dopo /ask.");
            }
        } else if (msg.body.startsWith('/speak')) {
            let message = msg.body.slice(6);
            if ( message.length !== 0 ) {
                await replyMedia(config.API_URL + "chatbot_audio/repeat/learn/" + encodeURI(message.trim()) +"/google/000000/it/audio.mp3", msg)
            } else {
                await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nSe vuoi farmi parlare devi scrivere un testo dopo /speak.");
            }
        }
    }
});



async function replyMedia(url, msg){
    await axios({
        url: url,
        method: 'GET',
        responseType: 'stream'
    }).then(async function (response){
        return new Promise((resolve, reject) => {
            const writer = fs.createWriteStream("/tmp/discord-tts-bot-api/watmpaudio.mp3");
            response.data.pipe(writer);
            let error = null;
            writer.on('error', err => {
              error = err;
              writer.close();
              reject(err);
            });
            writer.on('close', () => {
              if (!error) {
                resolve(true);
              }
            });
            writer.on('finish', async function(){      
                await msg.reply(MessageMedia.fromFilePath("/tmp/discord-tts-bot-api/watmpaudio.mp3"), null, { sendAudioAsVoice: true })  
            }); 
          });
    }).catch(async function(error) {
        console.error("ERRORE!", "["+ error + "]");
        await msg.reply("Schifo, bestemmia e disagio. Si é verificato un errore stronzo. Chiedere a blast di sistemare. Se ha voglia lo farà.");
    });
}   

async function replyMsg(url, msg){
    await axios.get(url).then(async function(response) {
        if(response.status === 204) {
            await msg.reply("Non ho trovato nessun testo contenente queste parole.");
        } else if(response.status === 200) {
            await msg.reply(response.data);
        } else {
            await msg.reply(ERROR_MSG);
        }
    }).catch(async function(error) {
        console.error("ERRORE!", "["+ error + "]");
        await msg.reply(ERROR_MSG);
    });
}
