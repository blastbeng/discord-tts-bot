const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const express = require('express');
const qrcode = require('qrcode-terminal');
const config = require("./config.json");
const axios = require('axios');
const log = require('loglevel');
const fs = require('fs');
const ERROR_MSG = "Schifo, bestemmia e disagio.\nSi é verificato un errore stronzo.\nExternal API Error? Bug Brutti? Chi lo sa!\nChiedere a blast di controllare.\nSe ha voglia lo farà."


console.log("Logging - Setting log level to: " + config.LOG_LEVEL)
log.setLevel(config.LOG_LEVEL);

client = new Client({
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
    const app = express();

    app.get('/message/:chatid/:text', async function(req, res) {
        try {
            const chatid = req.params.chatid;
            const text = req.params.text;
            let found = false;
            chats = await client.getChats();    
            for (let j = 0; j < chats.length; j++) {
                const chat = chats[j];
                if (chat.isGroup) {
                    for (let i = 0; i < chat.participants.length; i++) {
                        if (chat.participants[i].id.user === config.TEL_NUMBER && chat.id.user == chatid){
                            try {
                                found = true;
                                await chat.sendSeen();
                                await chat.sendStateTyping();
                                await chat.sendMessage(`${text}`);
                                await chat.clearState();
                            } catch (error) {
                                await chat.clearState();
                                throw error;
                            }
                        }
                    }
                }
            }
            if (found) {
                res.send('Chat trovata. Hai scritto: ' + text);
            } else {
                res.status(404).send('Chat non trovata.');
            }
        } catch (error) {
            log.error("ERRORE!", "["+ error + "]");
            res.status(404).send('ERRORE!');
        }
    });

    app.listen(config.REST_PORT, () => console.log(`App listening on port ${config.REST_PORT}!`));
});

client.on('message', async msg => {
    try {
        let chat = await msg.getChat();
        if (msg.body.toLowerCase().startsWith('/help') 
            || msg.body.toLowerCase().startsWith('/random')
            || msg.body.toLowerCase().startsWith('/ask')
            || msg.body.toLowerCase().startsWith('/generate')
            || msg.body.toLowerCase().startsWith('/curse')
            || msg.body.toLowerCase().startsWith('/insult')
            || msg.body.toLowerCase().startsWith('/speak')
            || msg.body.toLowerCase().startsWith('/papa')
            || msg.body.toLowerCase().startsWith('/berlusca')
            || msg.body.toLowerCase().startsWith('/goku')
            || msg.body.toLowerCase().startsWith('/gerry')
            ){

            let canReply = false;

            if (chat.isGroup) {
                for (let i = 0; i < chat.participants.length; i++) {
                    if (chat.participants[i].id.user === config.TEL_NUMBER){
                        canReply = true;
                        break;
                    }
                }
            }


            if (canReply) { 
                await chat.sendSeen();
                log.info("CHATID: [ "+ chat.id.user + " ], COMMAND: [ "+ msg.body + " ], ");
                if (msg.body.toLowerCase() == '/help' || msg.body.toLowerCase().startsWith('/help')) {
                    await chat.sendStateTyping();
                    let message = msg.body.slice(5);
                    helpmsg = "Lista Comandi: \n- /ask: chiedimi qualcosa\n- /speak: parla con la voce di google\n- /generate: genera frasi idiote\n- /insult: genera insulti\n- /curse: curse\n- /berlusca: parla con la voce di Silvio Berlusconi\n- /gerry: parla con la voce di Gerry Scotti\n- /goku: parla con la voce di Goku\n- /papa: parla con la voce di Papa Francesco\n- /random: frase casuale\n /random <testo>: frase casuale dato un testo"
                    if ( message.length === 0 ) {
                        await msg.reply(helpmsg);
                    } else {
                        await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nNon é necessario scrivere niente dopo /help per visualizzare i comandi disponibili.\n\n" + helpmsg);
                    }

                } else if (msg.body.toLowerCase() == '/random' || msg.body.toLowerCase().startsWith('/random')) {
                    let url = config.API_URL + "chatbot_text/random/000000/"
                    let message = msg.body.slice(7);
                    if ( message.length !== 0 ) {
                        url = config.API_URL + "chatbot_text/random/000000/" + encodeURIComponent(message.trim())
                    } 
                    await replyMsg(url, msg, chat)    
                } else if (msg.body.toLowerCase().startsWith('/ask')) {
                    let message = msg.body.slice(4);
                    if ( message.length !== 0 ) {
                        await replyMsg(config.API_URL + "chatbot_text/ask/" + encodeURIComponent(message.trim()) + "/000000/it", msg, chat)
                    } else {
                        await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nSe devi chiedermi qualcosa devi scrivere un testo dopo /ask.");
                    }
                } else if (msg.body.toLowerCase().startsWith('/generate')) {
                    let message = msg.body.slice(9);
                    if ( message.length === 0 ) {
                        await replyMsg(config.API_URL + "utils/sentences/generate/000000/0", msg, chat)
                    } else {
                        await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nNon é necessario scrivere niente dopo /generate.");
                    }
                } else if (msg.body.toLowerCase().startsWith('/curse')) {
                    let message = msg.body.slice(6);
                    if ( message.length === 0 ) {
                        await replyMsg(config.API_URL + "chatbot_text/curse/000000/it", msg, chat)
                    } else {
                        await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nNon é necessario scrivere niente dopo /curse.");
                    }
                } else if (msg.body.toLowerCase() == '/insult' || msg.body.toLowerCase().startsWith('/insult')) {
                    let url = config.API_URL + "chatbot_text/insult?chatid=000000&lang=it"
                    let message = msg.body.slice(7);
                    if ( message.length !== 0 ) {
                        url = config.API_URL + "chatbot_text/insult?chatid=000000&lang=it&text=" + encodeURIComponent(message.trim())
                    } 
                    await replyMsg(url, msg, chat)    
                } else if (msg.body.toLowerCase().startsWith('/speak')) {
                    await repeat(msg.body.slice(0, 6).toLowerCase(), msg.body.slice(6), "google", msg, chat)
                } else if (msg.body.toLowerCase().startsWith('/papa')) {
                    await repeat(msg.body.slice(0, 5).toLowerCase(), msg.body.slice(5), "TM:8bqjb9x51vz3", msg, chat)
                } else if (msg.body.toLowerCase().startsWith('/berlusca')) {
                    await repeat(msg.body.slice(0, 9).toLowerCase(), msg.body.slice(9), "TM:22e5sxvt2dvk", msg, chat)
                } else if (msg.body.toLowerCase().startsWith('/goku')) {
                    await repeat(msg.body.slice(0, 5).toLowerCase(), msg.body.slice(5), "TM:eb0rmkq6fxtj", msg, chat)
                }else if (msg.body.toLowerCase().startsWith('/gerry')) {
                    await repeat(msg.body.slice(0, 6).toLowerCase(), msg.body.slice(6), "TM:5ggf3m5w2mhq", msg, chat)
                }
            }
        }
    } catch (error) {
        log.error("ERRORE!", "["+ error + "]");
        await msg.reply(ERROR_MSG);
        await chat.clearState();
    }
});

async function repeat(command, message, voice, msg, chat){
    
    if ( message.length !== 0 ) {
        await replyMedia(config.API_URL + "chatbot_audio/repeat/learn/" + encodeURIComponent(message.trim()) + "/" + encodeURIComponent(voice) + "/000000/it/audio.mp3", msg, chat)
    } else {
        await msg.reply("Sei stronzo?\nMangi le pietre o sei scemo?\nSe vuoi farmi parlare devi scrivere un testo dopo " + command + ".");
    }
}

async function replyMedia(url, msg, chat){
    await chat.sendStateRecording();
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
                    await chat.clearState(); 
                }); 
            } else {
                log.error("ERRORE!", "["+ error + "]");
                await msg.reply(ERROR_MSG);
                await chat.clearState();
            }
          });
    }).catch(async function(error) {
        log.error("ERRORE!", "["+ error + "]");
        await msg.reply(ERROR_MSG);
        await chat.clearState();
    });
}   

async function replyMsg(url, msg, chat){
    await chat.sendStateTyping();
    await axios.get(url).then(async function(response) {
        if(response.status === 204) {
            await msg.reply("Non ho trovato nessun testo contenente queste parole.");
        } else if(response.status === 200) {
            await msg.reply(response.data);
        } else if(response.status === 406) {
            await msg.reply("Questo testo contiene parole bloccate dai filtri.");
        } else {
            await msg.reply(ERROR_MSG);
        }
        await chat.clearState();
    }).catch(async function(error) {
        log.error("ERRORE!", "["+ error + "]");
        await msg.reply(ERROR_MSG);
        await chat.clearState();
    });
}
