const { SlashCommandBuilder } = require('@discordjs/builders');
const { getVoiceConnection, createAudioPlayer } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const player = createAudioPlayer();
const fetch = require('node-fetch');


module.exports = {
    data: new SlashCommandBuilder()
        .setName('stop')
        .setDescription('Il pezzente smette di parlare'),
    async execute(interaction) {
        if (interaction.member.voice === null 
            || interaction.member.voice === undefined 
            || interaction.member.voice.channelId === null 
            || interaction.member.voice.channelId === undefined ){
                interaction.reply({ content: 'Devi prima entrare in un canale vocale', ephemeral: true });
        } else {
            try {
                const connection_old = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection_old !== null && connection_old !== undefined){
                    connection_old.subscribe(player);
                    player.stop();
                    interaction.reply({ content: 'Il pezzente ha smesso di parlare', ephemeral: true });
                }  
            } catch (error) {
                console.error(error);
            }
        }
    }
};