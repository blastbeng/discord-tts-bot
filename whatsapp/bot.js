const { Client, LocalAuth, MessageMedia, List } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const config = require("./config.json");
const axios = require('axios');
const fs = require('fs');
const ERROR_MSG = "Schifo, bestemmia e disagio.\nSi é verificato un errore stronzo.\nChiedere a blast di sistemare.\nSe ha voglia lo farà."
const TIMEOUT_MSG = "Schifo, bestemmia e disagio.\nSi é verificato errore di TimeOut verso API esterne.\nRiprova fra qualche minuto."
const API_ERROR = "Schifo, bestemmia e disagio.\nLa generazione dell'audio sta impiegando troppo tempo.\nRiprova fra qualche minuto o prova con una frase piú corta."

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
    try {
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
            if (msg.body.toLowerCase() == '/help' || msg.body.toLowerCase().startsWith('/help')) {
                let message = msg.body.slice(5);
                helpmsg = "Lista Comandi: \n- /ask: chiedimi qualcosa\n- /speak: parla con la voce di google\n- /berlusca: parla con la voce di Silvio Berlusconi\n- /gerry: parla con la voce di Gerry Scotti\n- /goku: parla con la voce di Goku\n- /papa: parla con la voce di Papa Francesco\n- /random: frase casuale\n /random <testo>: frase casuale dato un testo"
                if ( message.length === 0 ) {
                    await msg.reply(helpmsg);
                } else {
                    await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nNon é necessario scrivere niente dopo /help per visualizzare i comandi disponibili.\n\n" + helpmsg);
                }

            } else if (msg.body.toLowerCase() == '/random' || msg.body.toLowerCase().startsWith('/random')) {
                url = config.API_URL + "chatbot_text/random/000000/"
                let message = msg.body.slice(7);
                if ( message.length !== 0 ) {
                    url = config.API_URL + "chatbot_text/random/000000/" + encodeURI(message)
                } 
                await replyMsg(url, msg)    
            } else if (msg.body.toLowerCase().startsWith('/ask')) {
                let message = msg.body.slice(4);
                if ( message.length !== 0 ) {
                    await replyMsg(config.API_URL + "chatbot_text/ask/" + message + "/000000/it", msg)
                } else {
                    await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nSe devi chiedermi qualcosa devi scrivere un testo dopo /ask.");
                }
            } else if (msg.body.toLowerCase().startsWith('/speak')) {
                await repeat(msg.body.slice(0, 6).toLowerCase(), msg.body.slice(6), "google", msg)
            } else if (msg.body.toLowerCase().startsWith('/papa')) {
                await repeat(msg.body.slice(0, 5).toLowerCase(), msg.body.slice(5), "TM:8bqjb9x51vz3", msg)
            } else if (msg.body.toLowerCase().startsWith('/berlusca')) {
                await repeat(msg.body.slice(0, 9).toLowerCase(), msg.body.slice(9), "TM:22e5sxvt2dvk", msg)
            } else if (msg.body.toLowerCase().startsWith('/goku')) {
                await repeat(msg.body.slice(0, 5).toLowerCase(), msg.body.slice(5), "TM:eb0rmkq6fxtj", msg)
            }else if (msg.body.toLowerCase().startsWith('/gerry')) {
                await repeat(msg.body.slice(0, 6).toLowerCase(), msg.body.slice(6), "TM:5ggf3m5w2mhq", msg)
            }
        }
    } catch (error) {
        console.error("ERRORE!", "["+ error + "]");
        await msg.reply(ERROR_MSG);
    }
});

async function repeat(command, message, voice, msg){
    
    if ( message.length !== 0 ) {
        await replyMedia(config.API_URL + "chatbot_audio/repeat/learn/" + encodeURI(message.trim()) + "/" + encodeURI(voice) + "/000000/it/audio.mp3", msg)
    } else {
        await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nSe vuoi farmi parlare devi scrivere un testo dopo " + command + ".");
    }
}

async function replyMedia(url, msg){
    await axios({
        timeout: 180000,
        url: url,
        method: 'GET',
        responseType: 'stream'
    }).then(async function (response){
        return new Promise(async function(resolve, reject) {
            if(response.status === 200){
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
            } else {
                console.error("ERRORE!", "["+ error + "]");
                await msg.reply(TIMEOUT_MSG);
            }
          });
    }).catch(async function(error) {
        console.error("ERRORE!", "["+ error + "]");
        await msg.reply(API_ERROR);
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
