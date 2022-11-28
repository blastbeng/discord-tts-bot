const { SlashCommandBuilder } = require('@discordjs/builders');
const { joinVoiceChannel, getVoiceConnection, createAudioPlayer } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const fs = require('fs');
const config = require("../config.json");
const player = createAudioPlayer();
const fetch = require('node-fetch');

const path = config.CACHE_DIR;
const api=config.API_URL;
const path_audio=config.API_PATH_AUDIO

module.exports = {
    data: new SlashCommandBuilder()
        .setName('join')
        .setDescription('Il pezzente entra nel canale'),
    async execute(interaction) {
      if (interaction.member.voice === null 
            || interaction.member.voice === undefined 
            || interaction.member.voice.channelId === null 
            || interaction.member.voice.channelId === undefined ){
                interaction.reply({ content: 'Stronzo che cazzo fai? Devi prima entrare in un canale vocale', ephemeral: true });
        } else {
            try {                
                var connection = null;
                const connection_old = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection_old !== null 
                    && connection_old !== undefined
                    && connection_old.joinConfig.channelId !== interaction.member.voice.channelId){
                    connection_old.destroy();
                    interaction.reply({ content: 'Il pezzente è entrato nel canale', ephemeral: true });
                } else {
                    connection = connection_old;
                    interaction.reply({ content: 'Il pezzente è entrato nel canale', ephemeral: true });
                }
                
                connection = joinVoiceChannel({
                    channelId: interaction.member.voice.channelId,
                    guildId: interaction.guildId,
                    adapterCreator: interaction.guild.voiceAdapterCreator,
                    selfDeaf: false,
                    selfMute: false
                });
            } catch (error) {
                console.error(error);
            }
        }
    }
};