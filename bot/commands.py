from bot import client, chat_bot
from bot.config import config

from discord import Embed


def get_good_color(user):
    if user.color != "#000000":
        return user.color
    else:
        return "#FFFFFF"


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
    if str(ctx.author.id) != config["OWNER_ID"]:
        return
    await ctx.send("Normalising database")
    chat_bot.normalise_database()
    await ctx.send("Database normalisation finished")


@client.command(pass_context=True)
async def status(ctx):
    new_em = Embed(title="AI Status", description="In " + ctx.guild.name, color=get_good_color(ctx.author))

    personality = config["CHANNEL_PERSONALITIES"][str(ctx.channel.id)]
    entries = chat_bot.get_personality_entries(personality)

    new_em.add_field(name=personality + " entries", value=str(len(entries)))
    new_em.add_field(name="Total entries", value=str(chat_bot.get_total_entries()))
    new_em.add_field(name="Minimum confidence", value=str(chat_bot.min_similarity * 100) + "%")
    new_em.add_field(name="Maximum confidence", value=str(chat_bot.max_similarity * 100) + "%")
    new_em.add_field(name="Total personalities", value=str(chat_bot.get_total_personalities()))
    await ctx.send(embed=new_em)
