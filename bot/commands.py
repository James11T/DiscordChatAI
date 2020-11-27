from bot import client, chat_bot, channel_to_personality


@client.command(pass_context=True)
async def entrycount(ctx):
    if str(ctx.channel.id) in channel_to_personality:
        personality = channel_to_personality[str(ctx.channel.id)]
        entries = chat_bot.get_personality_entries(personality)
        await ctx.send(f"{ctx.author.mention} The `{personality}` personality has `{len(entries)}` entries")
    else:
        await ctx.send(ctx.author.mention + " This is not an AI channel")
