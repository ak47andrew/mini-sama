import re
import discord
import asyncio
from discord.ext import commands
from old import get_response
import config

current_task = None
THINKING_REGEX = re.compile(r"<think>(?:.|\n)+<\/think>\n*")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Started :3")


@bot.event
async def on_message(message: discord.Message):
    global current_task
    if message.author.bot: return
    if message.channel.id != config.CHANNEL: return


    # Cancel the previous task if it's still running
    if current_task and not current_task.done():
        current_task.cancel()
        try:
            await current_task # type: ignore
        except asyncio.CancelledError:
            pass

    # Start a new task
    current_task = asyncio.create_task(handle_message(message))


async def handle_message(message: discord.Message):
    try:
        content = message.content
        if content == "": return
        print(f"Got message from {message.author.name}: {content}")

        history = [{
            "role": "assistant",
            "content": msg.content
        } if msg.author.id == bot.user.id else {  # type: ignore
            "role": "user",
            "content": f"{msg.author.display_name}: {msg.content}"
        } async for msg in message.channel.history(limit=config.HISTORY_LIMIT) if msg.content != ""]
        history.reverse()
        history = [{
            "role": "system",
            "content": config.SYSTEM_PROMPT
        }] + history

        resp = await get_response(history)
        print(resp)
        resp = THINKING_REGEX.sub("", resp)
        print(resp)
        await message.channel.send(resp)
    except asyncio.CancelledError:
        print("Canceled the prev one")
        raise

bot.run(config.TOKEN)
