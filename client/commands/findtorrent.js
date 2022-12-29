const { SlashCommandBuilder } = require('@discordjs/builders');
const {
    Collection,
    ActionRowBuilder, 
    ButtonBuilder,
    EmbedBuilder,
    ButtonStyle
} = require('discord.js');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
const fetch = require('node-fetch');

const PROWLARR_HOST=config.PROWLARR_HOST;
const PROWLARR_PORT=config.PROWLARR_PORT;
const PROWLARR_API_KEY=config.PROWLARR_API_KEY;
const path = config.CACHE_DIR;

module.exports = {
    data: new SlashCommandBuilder()
        .setName('findtorrent')
        .setDescription("Cerca un torrent")
        .addStringOption(option => option.setName('text').setDescription('Il testo da cercare').setRequired(true))
        ,
    async execute(interaction) {
        
        if (!interaction.member._roles.includes(config.ENABLED_ROLE)){
            interaction.reply({ content: "Non sei abilitato all'utilizzo di questo bot.", ephemeral: true });
        } else {
            const torrent_name = interaction.options.getString('text');

            interaction.deferReply({ content: "Sto cercando: " + torrent_name, ephemeral: true });

            var params = "http://"+ PROWLARR_HOST + ":" + PROWLARR_PORT + "/api/v1/search" 
                + "?query=" + encodeURIComponent(torrent_name)
                + "&type=search"
                + "&limit=100"
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
                        if(data.length > 0){
                            data.sort((a,b) => parseFloat(b.seeders) - parseFloat(a.seeders));
                           

                                var embed = new EmbedBuilder()
                                .setColor('#0099ff')
                                .setTitle("Risultati per: " + torrent_name)    
                                for(let i=0; i++; i<data.length && i < 12) {
                                }

                                var filehtml = Math.random().toString(36).slice(2)+".html";     
                                var outFilehtml = path+"/"+filehtml;
                                var stream = fs.createWriteStream(outFilehtml);
                                
                                stream.once('open', function(fd) {
                                    stream.write('<!DOCTYPE html><html lang="en">');
                                    stream.write('<head>');
                                    stream.write('<meta charset="utf-8">');
                                    stream.write('<meta name="viewport" content="width=device-width,initial-scale=1, shrink-to-fit=no">');                                  
                                    stream.write('<link href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet">');
                                    stream.write('</head>');
                                    stream.write('<body>');
                                    stream.write('<div class="container">');
                                    stream.write('<h2>Torrent results for: ' + torrent_name + '</h2>');
                                    stream.write('<table id="torrentsTable" class="table table-striped">');
                                    stream.write('<thead>');
                                    stream.write('<tr>');
                                    stream.write('  <th>TITLE</th>');
                                    stream.write('  <th>INDEXER</th>');
                                    stream.write('  <th>SEEDERS</th>');
                                    stream.write('  <th>LEECHERS</th>');
                                    stream.write('  <th>SIZE</th>');
                                    stream.write('  <th>DATE</th>');
                                    stream.write('</tr>');
                                    stream.write('</thead>');
                                    let i = 0;
                                    for(const torrent of data) {
                                        if(i<12){
                                            embed.addFields(
                                                { name: torrent['title'], value: torrent['infoUrl'] },
                                                { name: 'Seeders: ' + torrent['seeders'] + ", Indexer: "+ torrent['indexer'], inline: true , value: "Date: "+ torrent['publishDate'] + ", Size: " + torrent['size'], inline: true },
                                            )
                                            i = i +1;
                                        }
                                        stream.write('<tr>');
                                        stream.write('  <td><a href=' + torrent['infoUrl'] + '>' + torrent['title'] + '</a></td>');
                                        stream.write('  <td>' + torrent['indexer'] + '</td>');
                                        stream.write('  <td>' + torrent['seeders'] + '</td>');
                                        stream.write('  <td>' + torrent['leechers'] + '</td>');
                                        stream.write('  <td>' + torrent['size'] + '</td>');
                                        stream.write('  <td>' + torrent['publishDate'] + '</td>');

                                        stream.write('</tr>');
                                    }
                                    embed.setTimestamp();
                                    stream.write('</table></div>');
                                    stream.write('<script  src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>');
                                    stream.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/js/bootstrap.min.js"></script>');
                                    stream.write('<script src="https://cdn.jsdelivr.net/npm/jquery.fancytable/dist/fancyTable.min.js"></script>');
                                    stream.write('<script type="text/javascript">');
                                                    
                                    stream.write('    $(document).ready(function(){');
                                                
                                    stream.write('        $("#torrentsTable").fancyTable({');
                                    stream.write('           sortColumn:0,');
                                    stream.write('            /* Setting pagination or enabling */');
                                    stream.write('            pagination: false,');
                                    stream.write('                globalSearch:true,');
                                    stream.write('                /* Exclude 2nd column from global search.*/');
                                    stream.write('            globalSearchExcludeColumns: [2],');
                                    stream.write('            onInit:function(){');
                                    stream.write('            /* On initialization of table */');
                                    stream.write('                console.log({ element:this });');
                                    stream.write('            },');
                                    stream.write('            onUpdate:function(){');
                                    stream.write('            /* On update like search and sort of table */');
                                    stream.write('                console.log({ element:this });');
                                    stream.write('                }');
                                    stream.write('            });');
                                    stream.write('        });');
                                    stream.write('        </script>');
                                    stream.write('</body></html>');
                                    stream.end(function() {                                    
                                        interaction.editReply({
                                            embeds: [ embed ],
                                            files: [{
                                                attachment: outFilehtml,
                                                name: torrent_name+'.html'
                                            }], 
                                            ephemeral: true
                                        }).catch(function(error) {
                                            console.error("ERRORE!", "["+ error + "]");
                                            interaction.editReply({ content: 'Si è verificato un errore', ephemeral: true });   
                                        }).then(data=>{
                                            fs.unlinkSync(outFile);
                                            fs.unlinkSync(outFilehtml);
                                        });
                                    });
                                });
                        } else {
                            interaction.editReply({ content: 'Nessun torrent trovato per: ' + torrent_name, ephemeral: true }).then(data=>{
                                fs.unlinkSync(outFile);
                                fs.unlinkSync(outFilehtml);
                            });
                        }
                    });
                });
            }).catch(function(error) {
                console.error("ERRORE!", "["+ error + "]");
                interaction.editReply({ content: 'Si è verificato un errore', ephemeral: true });   
            });  
        }
    }
}; 
