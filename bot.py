
import os
import re
import discord
from discord.ext import commands

# Discord intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# Temporary warning storage
warnings = {}

# Basic moderation words — baad mein customize kar sakte ho
BAD_WORDS = {
    "galiword1",
    "galiword2",
}

# Baad mein apne Discord channel IDs yahan add karna
CHANNEL_IDS = {
    "registration": 0,
    "result": 0,
    "qualifiers": 0,
}


def channel_mention(channel_name):
    channel_id = CHANNEL_IDS.get(channel_name, 0)

    if channel_id:
        return f"<#{channel_id}>"

    return f"#{channel_name}"


def get_reply(message):
    text = message.lower().strip()

    if any(word in text for word in [
        "registration",
        "register",
        "reg kaise",
        "register kaha",
        "registration kaha"
    ]):
        return (
            f"Registration ke liye {channel_mention('registration')} "
            "channel check karo. Wahan complete process diya hoga."
        )

    if any(word in text for word in [
        "scrim kab",
        "scrims kab",
        "match kab",
        "matches kab",
        "schedule kya"
    ]):
        return (
            "Scrims aur matches ka latest schedule server ke "
            "announcement/schedule channel mein check karo."
        )

    if any(word in text for word in [
        "idp kab",
        "idp time",
        "idp"
    ]):
        return (
            "IDP time ke liye latest match schedule check karo. "
            "Agar schedule nahi mila, admin ko tag karo."
        )

    if any(word in text for word in [
        "result",
        "results",
        "score"
    ]):
        return (
            f"Match results ke liye {channel_mention('result')} "
            "channel check karo."
        )

    if any(word in text for word in [
        "qualifier",
        "qualifiers",
        "qualified"
    ]):
        return (
            f"Qualifiers ki information {channel_mention('qualifiers')} "
            "channel mein milegi."
        )

    if any(word in text for word in [
        "hello",
        "hi",
        "hlo",
        "hey"
    ]):
        return "Hello! 👋 ASTRAV ESPORTS mein welcome!"

    if any(word in text for word in [
        "help",
        "madad",
        "guide"
    ]):
        return (
            "Main in topics par help kar sakta hoon:\n"
            "• Registration\n"
            "• Scrim schedule\n"
            "• IDP timing\n"
            "• Match results\n"
            "• Qualifiers\n"
            "• Server information"
        )

    return None


@bot.event
async def on_ready():
    print(f"Scrim Bot online hai: {bot.user}")
    print(f"Bot ID: {bot.user.id}")


@bot.event
async def on_message(message):
    # Bot ke messages ignore karo
    if message.author.bot:
        return

    content = message.content.lower()

    # Moderation: admin/moderator ko exempt rakho
    is_staff = (
        message.author.guild_permissions.manage_messages
        or message.author.guild_permissions.administrator
    )

    if not is_staff:
        found_bad_word = any(
            re.search(rf"\b{re.escape(word)}\b", content)
            for word in BAD_WORDS
        )

        if found_bad_word:
            try:
                await message.delete()
            except discord.Forbidden:
                pass

            user_id = message.author.id
            warnings[user_id] = warnings.get(user_id, 0) + 1

            await message.channel.send(
                f"{message.author.mention}, abusive language allowed nahi hai. "
                f"Warning **{warnings[user_id]}** ⚠️",
                delete_after=8
            )
            return

    # Normal keyword reply
    reply = get_reply(message.content)

    if reply:
        await message.channel.send(
            f"{message.author.mention} {reply}"
        )

    # Commands ko process karo
    await bot.process_commands(message)


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 {round(bot.latency * 1000)}ms")


@bot.command()
async def helpme(ctx):
    await ctx.send(
        "Available commands:\n"
        "`!ping` - Bot response check\n"
        "`!helpme` - Help menu"
    )


# Token hosting ke Environment Variables mein add hoga
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable missing hai.")

bot.run(TOKEN)
