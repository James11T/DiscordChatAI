from bot import client, chat_bot
from discord import Game

from bot.config import config

import time
import asyncio

good_response = "🟢"
bad_response = "🔴"
neutral_response = "🔵"
response_timeout = config["RESPONSE_TIMEOUT"]

message_buffer = {}


async def remove_reactions(mes):
    await mes.clear_reaction(bad_response)
    await mes.clear_reaction(neutral_response)
    await mes.clear_reaction(good_response)


async def add_reactions(mes):
    await mes.add_reaction(good_response)
    await mes.add_reaction(neutral_response)
    await mes.add_reaction(bad_response)


@client.event
async def on_ready():
    print("Bot ready")
    await client.change_presence(activity=Game(name=config["BOT_STATUS"]))


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(client.command_prefix):
        return await client.process_commands(message)

    if not str(message.channel.id) in config["CHANNEL_PERSONALITIES"]:
        return

    if len(message.content) > 255:
        return

    if str(message.author.id) in message_buffer:
        # Ensure that the bot is not waiting for a response from the user
        if time.time() - message_buffer[str(message.author.id)] < response_timeout:
            return

    personality = config["CHANNEL_PERSONALITIES"][str(message.channel.id)]

    response = chat_bot.get_response(personality, message.content)

    response_message = await message.channel.send(response)
    await add_reactions(response_message)

    def check(new_reaction, new_user):
        return (new_user == message.author and
                str(new_reaction.emoji) in [good_response, bad_response, neutral_response] and
                new_reaction.message == response_message)

    try:
        # Wait for reaction
        reaction, user = await client.wait_for("reaction_add", timeout=response_timeout, check=check)
    except asyncio.TimeoutError:
        pass
    else:
        if str(reaction.emoji) in [bad_response, neutral_response]:
            # Ask for better response
            invoke_time = time.time()
            message_buffer[str(message.author.id)] = invoke_time

            better_response_message = await message.channel.send(message.author.mention +
                                                                 " please tell me what a good response to `" +
                                                                 message.content + "` would have been!")

            def check2(m):
                return m.author == message.author

            try:
                # Wait for better response
                better_message = await client.wait_for("message", timeout=response_timeout, check=check2)
            except asyncio.TimeoutError:
                # Stop waiting
                if invoke_time == message_buffer[str(message.author.id)]:
                    # Reset waiter
                    message_buffer[str(message.author.id)] = 0
                await better_response_message.delete()
            else:
                chat_bot.learn_response(personality, message.content, better_message.content)
                chat_bot.disencourage_response(personality, message.content, response)
                message_buffer[str(message.author.id)] = 0
                await response_message.edit(content=better_message.content)
                await better_message.delete()
                await better_response_message.delete()
        elif str(reaction.emoji) == good_response:
            chat_bot.learn_response(personality, message.content, response)
        # Remove reactions
        await remove_reactions(response_message)
