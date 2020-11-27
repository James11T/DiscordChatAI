from bot import client, chat_bot


@client.command(pass_context=True)
async def entrycount(ctx):
    if str(ctx.channel.id) in config["CHANNEL_PERSONALITIES"]:
        personality = config["CHANNEL_PERSONALITIES"][str(ctx.channel.id)]
        entries = chat_bot.get_personality_entries(personality)
        await ctx.send(f"{ctx.author.mention} The `{personality}` personality has `{len(entries)}` entries")
    else:
        await ctx.send(ctx.author.mention + " This is not an AI channel")
