const { SlashCommandBuilder } = require('@discordjs/builders');
const wait = require('node:timers/promises').setTimeout;
require( 'console-stamp' )( console );

module.exports = {
    data: new SlashCommandBuilder()
        .setName('restart')
        .setDescription('Riavvia il pezzente'),
    async execute(interaction) {       
        try {
            interaction.reply({ content: 'Il pezzente si sta riavviando', ephemeral: true });
            await wait(10000);
            process.exit();
        } catch (error) {
            console.error(error);
        }
    }
};