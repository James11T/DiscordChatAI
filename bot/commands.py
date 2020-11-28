from bot import client, chat_bot
from bot.config import config


@client.command(pass_context=True)
async def entrycount(ctx):
    if str(ctx.channel.id) in config["CHANNEL_PERSONALITIES"]:
        personality = config["CHANNEL_PERSONALITIES"][str(ctx.channel.id)]
        entries = chat_bot.get_personality_entries(personality)
        await ctx.send(f"{ctx.author.mention} The `{personality}` personality has `{len(entries)}` entries")
    else:
        await ctx.send(ctx.author.mention + " This is not an AI channel")


@client.command(pass_context=True)
async def normalise(ctx):
    if str(ctx.author.id) != str(client.owner_id):
        return
    await ctx.send("Normalising database")
    chat_bot.normalise_database()
    await ctx.send("Database normalisation finished")
