# ╔═══════════════════════════════════════════════════════════════════════╗
# ║                                                                       ║
# ║                         DATA TEAM FORCE                               ║
# ║                     Discord Bot - EPSILONAI                           ║
# ║                                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════╝
import os
import asyncio
import logging
import asyncio
import discord
from aiohttp import web
from dotenv import load_dotenv
from discord.ext import commands
from utils.process_q import process_question

load_dotenv()

# ┌─────────────────────────────────────────────────────────────────────────┐
# │                          LOGGER CONFIGURATION                           │
# └─────────────────────────────────────────────────────────────────────────┘

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DTF-Bot')

# ┌─────────────────────────────────────────────────────────────────────────┐
# │                       DISCORD BOT CONFIGURATION                         │
# └─────────────────────────────────────────────────────────────────────────┘

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN_TEST")

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
        logger.info(f"Bot successfully logged in as {bot.user.name} (ID: {bot.user.id})")


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
    
    logger.info(f"Message received from {ctx.author} (ID: {ctx.author.id}) in {ctx.channel}")
    logger.debug(f"Full message content: {ctx.content}")
    
    if not question:
        logger.warning(f"Empty question from {ctx.author}")
        await ctx.channel.send("❌ Please provide a question when you mention me!")
        await bot.process_commands(ctx)
        return

    logger.info(f"Processing question: '{question[:100]}...' from {ctx.author}")
    # Create async task for parallel processing
    asyncio.create_task(process_question(ctx, question))


async def handle_health(_request):
    return web.Response(text="OK")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    print(f"Web server listening on 0.0.0.0:{port}")
    return runner


async def main():
    if TOKEN is None:
        logger.critical("DISCORD_TOKEN is missing from environment variables")
        raise ValueError("DISCORD_TOKEN is missing")

    runner = await start_web_server()
    try:
        logger.info("Starting DTF Discord Bot...")
        await bot.start(TOKEN)
    except Exception as e:
        logger.critical(f"Fatal error running bot: {e}", exc_info=True)

    finally:
        await runner.cleanup()


# ┌─────────────────────────────────────────────────────────────────────────┐
# │                        BOT INITIALIZATION                               │
# └─────────────────────────────────────────────────────────────────────────┘

if __name__ == "__main__":
    asyncio.run(main())
