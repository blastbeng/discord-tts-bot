const { SlashCommandBuilder } = require('@discordjs/builders');
const { getVoiceConnection } = require('@discordjs/voice');
require( 'console-stamp' )( console );
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
                const connection = getVoiceConnection(interaction.member.voice.guild.id);
                if (connection){
                    if ( connection !== null
                        && connection !== undefined
                        && connection.state !== null
                        && connection.state !== undefined
                        && connection.state.subscription !== null
                        && connection.state.subscription !== undefined
                        && connection.state.subscription.player !== null
                        && connection.state.subscription.player !== undefined){
                            connection.state.subscription.player.stop();
                            connection.state.subscription.unsubscribe();
                    }
                    interaction.reply({ content: 'Il pezzente ha smesso di parlare', ephemeral: true });
                } 
            } catch (error) {
                console.error(error);
            }
        }
    }
};