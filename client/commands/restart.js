const { SlashCommandBuilder } = require('@discordjs/builders');
const wait = require('node:timers/promises').setTimeout;
const config = require("../config.json");
require( 'console-stamp' )( console );

module.exports = {
    data: new SlashCommandBuilder()
        .setName('restart')
        .setDescription('Riavvia il pezzente'),
    async execute(interaction) {       
        
            
        if (!interaction.member._roles.includes(config.ENABLED_ROLE)){
            interaction.reply({ content: "Non sei abilitato all'utilizzo di questo bot.", ephemeral: true });
        } else {
            try {
                interaction.reply({ content: 'Il pezzente si sta riavviando', ephemeral: true });
                await wait(10000);
                process.exit();
            } catch (error) {
                console.error(error);
            }
            
        } 
    }
};