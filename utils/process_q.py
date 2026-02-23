import discord
import json
import logging
from utils.send import send_to_agent, send_to_target, send_answer
from pathlib import Path

logger = logging.getLogger('DTF-Bot.ProcessQuestion')
LOADER_GIF_PATH = Path("assets/loader.gif")


# ┌─────────────────────────────────────────────────────────────────────────┐
# │                      MESSAGE HANDLER                                    │
# └─────────────────────────────────────────────────────────────────────────┘


async def process_question(ctx, question):
    """
    Process a single question asynchronously.
    This function runs independently for each question, enabling parallel processing.

    Args:
        ctx: Discord message context
        question: User's question text
    """
    thinking_msg = None
    thread = None
    try:
        logger.info(f"Starting to process question from {ctx.author}: '{question[:50]}...'")
        
        # Setup thread
        if isinstance(ctx.channel, discord.Thread):
            thread = ctx.channel
            thread_id = str(thread.id)
            logger.info(f"Reusing existing thread {thread_id}")
        else:
            thread = await ctx.create_thread(
                name=f"{question[:20]}..." if len(question) > 20 else question,
            )
            thread_id = str(thread.id)
            logger.info(f"Created new thread {thread_id} for question")

        # Send loader GIF
        logger.info(f"Sending loader GIF to thread {thread_id}")
        thinking_msg = await thread.send(file=discord.File(LOADER_GIF_PATH))

        # Get answer from agent
        logger.info(f"Sending question to agent (thread: {thread_id})")
        answer = await send_to_agent(question, thread_id)

        logger.info("=" * 50)
        logger.info(json.dumps(answer, indent=2, default=str))
        logger.info("=" * 50)

        # Delete loader and send answer
        logger.info(f"Deleting loader message in thread {thread_id}")
        await thinking_msg.delete()
        
        if answer:
            logger.info(f"Sending answer to user (thread: {thread_id})")
            await send_answer(ctx, thread, answer)
            logger.info(f"Successfully processed question for {ctx.author} in thread {thread_id}")
        else:
            logger.error(f"No answer received from agent for question: {question[:50]}...")
            await send_to_target(
                thread,
                content=f"❌ Sorry {ctx.author.mention}, I couldn't get an answer. There is a problem with the agent.",
            )

    except Exception as e:
        logger.error(f"Error processing question from {ctx.author}: {e}", exc_info=True)
        target = ctx if isinstance(ctx.channel, discord.Thread) else thread
        if target:
            await send_to_target(target, content=f"❌ Error processing question.")
        else:
            logger.error("Could not send error message - no valid target channel")
