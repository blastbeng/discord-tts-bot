const { SlashCommandBuilder } = require('@discordjs/builders');
const { getVoiceConnection, NoSubscriberBehavior, createAudioPlayer } = require('@discordjs/voice');
require( 'console-stamp' )( console );
const player = createAudioPlayer({
	behaviors: {
		noSubscriber: NoSubscriberBehavior.Play,
	},
});
const fetch = require('node-fetch');
const config = require("../config.json");


module.exports = {
    data: new SlashCommandBuilder()
        .setName('stop')
        .setDescription('Il pezzente smette di parlare'),
    async execute(interaction) {
       
        if (!interaction.member._roles.includes(config.ENABLED_ROLE)){
            interaction.reply({ content: "Non sei abilitato all'utilizzo di questo bot.", ephemeral: true });
        } else {
            try {
                const connection_old = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection_old !== null && connection_old !== undefined){
                    connection_old.subscribe(player);
                    player.stop();
                    if(subscription) {
                        setTimeout(() => subscription.unsubscribe(), 15000)
                    }      
                    interaction.reply({ content: 'Il pezzente ha smesso di parlare', ephemeral: true });
                }  
            } catch (error) {
                console.error(error);
            }
        }
    }
};