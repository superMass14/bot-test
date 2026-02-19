import discord
import json
from utils.send import send_to_agent, send_to_target, send_answer
from pathlib import Path

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
        # Setup thread
        if isinstance(ctx.channel, discord.Thread):
            thread = ctx.channel
            thread_id = str(thread.id)
        else:
            thread = await ctx.create_thread(
                name=f"{question[:20]}..." if len(question) > 20 else question,
            )
            thread_id = str(thread.id)

        # Send loader GIF
        thinking_msg = await thread.send(file=discord.File(LOADER_GIF_PATH))

        # Get answer from agent
        answer = await send_to_agent(question, thread_id)

        print("=" * 50)
        print(json.dumps(answer, indent=2, default=str))
        print("=" * 50)

        # Delete loader and send answer
        await thinking_msg.delete()
        if answer:
            await send_answer(ctx, thread, answer)
        else:
            await send_to_target(
                thread,
                content=f"❌ Sorry {ctx.author.mention}, I couldn't get an answer. There is a problem with the agent.",
            )
            print(f"Error: No answer received from agent for question: {question}")

    except Exception as e:
        target = ctx if isinstance(ctx.channel, discord.Thread) else thread
        if target:
            await send_to_target(target, content=f"❌ Error processing question.")
        print(f"Error processing question: {e}")
