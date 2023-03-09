const { SlashCommandBuilder } = require('@discordjs/builders');
const { joinVoiceChannel, getVoiceConnection, VoiceConnectionStatus, entersState } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const config = require("../config.json");

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

module.exports = {
    data: new SlashCommandBuilder()
        .setName('join')
        .setDescription('Il pezzente entra nel canale'),
    async execute(interaction) {
      
            
        if (!interaction.member._roles.includes(config.ENABLED_ROLE)){
            interaction.reply({ content: "Non sei abilitato all'utilizzo di questo bot.", ephemeral: true });
        } else if (interaction.member.voice === null 
            || interaction.member.voice === undefined 
            || interaction.member.voice.channelId === null 
            || interaction.member.voice.channelId === undefined ){
                interaction.reply({ content: 'Devi prima entrare in un canale vocale', ephemeral: true });
        } else if (interaction.member.voice !== null 
            && interaction.member.voice !== undefined 
            && interaction.member.voice.channelId !== null 
            && interaction.member.voice.channelId !== undefined
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_1
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_2
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_3
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_4){
                interaction.reply({ content: "Impossibile utilizzare questo comando in questo canale vocale.", ephemeral: true });
        } else {
            try {                
                const connection_old = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection_old !== null 
                    && connection_old !== undefined
                    && connection_old.joinConfig.channelId !== interaction.member.voice.channelId){
                      connection_old.destroy();
                } 
                await new Promise(resolve => setTimeout(resolve, 2000));

                connection = joinVoiceChannel({
                    channelId: interaction.member.voice.channelId,
                    guildId: interaction.guildId,
                    adapterCreator: interaction.guild.voiceAdapterCreator,
                    selfDeaf: false,
                    selfMute: false
                });

                interaction.reply({ content: 'Il pezzente è entrato nel canale', ephemeral: true });
            } catch (error) {
                console.error(error);
            }
        }
    }
};