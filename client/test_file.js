const config = require("../config.json");
const fs = require('fs');
const fetch = require('node-fetch');
const PROWLARR_HOST=config.PROWLARR_HOST;
const PROWLARR_PORT=config.PROWLARR_PORT;
const PROWLARR_API_KEY=config.PROWLARR_API_KEY;
const path = config.CACHE_DIR;
const torrent_name = "avatar";

            var params = "http://"+ PROWLARR_HOST + ":" + PROWLARR_PORT + "/api/v1/search" 
                + "?query=" + encodeURIComponent(torrent_name)
                + "&type=search"
                + "&limit=25"
                + "&offset=0"

            fetch(
                params,
                {
                    method: 'GET',
                    mode: 'no-cors',
                    headers: { 
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Host': PROWLARR_HOST + ":" + PROWLARR_PORT,
                        'Pragma': 'no-cache',
                        'X-Api-Key': PROWLARR_API_KEY,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                }
            ).then(res => {
                new Promise((resolve, reject) => {
                    var file = Math.random().toString(36).slice(2)+".json";     
                    var outFile = path+"/"+file;
                    const dest = fs.createWriteStream(outFile);
                    res.body.pipe(dest);
                    res.body.on('end', () => resolve());
                    dest.on('error', reject);

                    dest.on('finish', function(){   
                        let rawdata = fs.readFileSync(outFile);
                        let data = JSON.parse(rawdata);
                        console.log(data);
                        fs.unlinkSync(outFile);
                    });
                });
            }).catch(function(error) {
                console.error("ERRORE!", "["+ error + "]");
            });  