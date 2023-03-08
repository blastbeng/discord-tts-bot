const { SlashCommandBuilder } = require('@discordjs/builders');
const { getVoiceConnection } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const config = require("../config.json");

module.exports = {
    data: new SlashCommandBuilder()
        .setName('leave')
        .setDescription('Il pezzente esce dal canale'),
    async execute(interaction) {
      
            
        if (!interaction.member._roles.includes(config.ENABLED_ROLE)){
            interaction.reply({ content: "Non sei abilitato all'utilizzo di questo bot.", ephemeral: true });
        } else if (interaction.member.voice === null 
            || interaction.member.voice === undefined 
            || interaction.member.voice.channelId === null 
            || interaction.member.voice.channelId === undefined ){
                interaction.reply({ content: 'Devi prima entrare in un canale vocale', ephemeral: true });
        } else if (interaction.member.voice
            && interaction.member.voice.channelId
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_1
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_2
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_3
            && interaction.member.voice.channelId !== config.ENABLED_CHANNEL_ID_4){
                interaction.reply({ content: "Impossibile utilizzare questo comando in questo canale vocale.", ephemeral: true });
        } else {
            try {                
                const connection = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection !== null
                    && connection !== undefined){
                        if ( connection 
                            && connection.state 
                            && connection.state.subscription
                            && connection.state.subscription.player){
                                connection.state.subscription.player.stop();
                                connection.state.subscription.unsubscribe();
                        }
                        connection.disconnect();
                        connection.destroy();
                    interaction.reply({ content: 'Il pezzente è uscito dal canale', ephemeral: true });
                } else {
                    interaction.reply({ content: 'Il pezzente non è in nessun canale vocale', ephemeral: true });                    
                }
            } catch (error) {
                console.error(error);
            }
        }
    }
};