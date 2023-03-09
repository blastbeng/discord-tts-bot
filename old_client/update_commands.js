const {
    REST
} = require('@discordjs/rest');
const {
    Routes
} = require('discord-api-types/v9');

const config = require("./config.json");
const fs = require('fs');

const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));

const commands = [];

for (const file of commandFiles) {
    const command = require(`./commands/${file}`);
    commands.push(command.data.toJSON());
}

const TOKEN = config.BOT_TOKEN;
const BOT_ID = config.BOT_ID;
const GUILD_ID = config.GUILD_ID;


const rest = new REST({ version: '9' }).setToken(TOKEN);

(async () => {
	try {
		console.log('Started refreshing application (/) commands.');

		await rest.put(
			Routes.applicationGuildCommands(BOT_ID, GUILD_ID),
			{ body: commands },
		);

		console.log('Successfully reloaded application (/) commands.');
	} catch (error) {
		console.error(error);
	}
})();