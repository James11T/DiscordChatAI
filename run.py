from bot import client, chat_bot, config

chat_bot.connect()
client.run(config["BOT_TOKEN"])
