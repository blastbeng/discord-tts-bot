const config = require("../config.json");
const fs = require('fs');
const fetch = require('node-fetch');

const api=config.API_URL;
const path_text=config.API_PATH_TEXT
const MESSAGES_CHANNEL_ID = config.MESSAGES_CHANNEL_ID;
var params = api+path_text+"lastsaid/"+encodeURIComponent("prova");
fetch(
    params,
    {
        method: 'GET',
        headers: { 'Accept': '*/*' }
    })
.then((result) => result.text())
.then((res) => {
    try {
        console.error("RES:", "["+ res + "]");
    } catch (err) {
        console.error("ERRORE!", "["+ error + "]");
    }
}).catch(function(error) {
    console.error("ERRORE!", "["+ error + "]");
}); 