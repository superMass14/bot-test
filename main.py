# ╔═══════════════════════════════════════════════════════════════════════╗
# ║                                                                       ║
# ║                         DATA TEAM FORCE                               ║
# ║                     Discord Bot - EPSILONAI                           ║
# ║                                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════╝
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from utils.process_q import process_question

load_dotenv()

# ┌─────────────────────────────────────────────────────────────────────────┐
# │                       DISCORD BOT CONFIGURATION                         │
# └─────────────────────────────────────────────────────────────────────────┘

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)
TOKEN = os.getenv("DISCORD_TOKEN")

# ┌─────────────────────────────────────────────────────────────────────────┐
# │                          BOT EVENTS                                     │
# └─────────────────────────────────────────────────────────────────────────┘


@bot.event
async def on_ready():
    """
    Event triggered when bot successfully connects to Discord.
    Prints login confirmation with bot username.
    """
    if bot.user:
        print(f"Logged in as {bot.user.name}")


@bot.event
async def on_message(ctx):
    """
    Main message handler for processing bot mentions and queries.

    This handler spawns async tasks for each question, enabling concurrent processing.
    Multiple users can ask questions simultaneously without blocking each other.

    Workflow:
    1. Ignore bot's own messages
    2. Check if bot is mentioned
    3. Extract question from message
    4. Spawn async task to process question in parallel

    Args:
        ctx: Discord message context
    """
    if ctx.author == bot.user:
        return

    if not (bot.user and bot.user in ctx.mentions):
        return

    question = ctx.content.replace(f"<@{bot.user.id}>", "").strip()
    if not question:
        await ctx.channel.send("❌ Please provide a question when you mention me!")
        await bot.process_commands(ctx)
        return

    # Create async task for parallel processing
    bot.loop.create_task(process_question(ctx, question))


# ┌─────────────────────────────────────────────────────────────────────────┐
# │                        BOT INITIALIZATION                               │
# └─────────────────────────────────────────────────────────────────────────┘

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is not missing")
bot.run(TOKEN)
