from aiohttp import ClientTimeout, ClientSession
import os
import logging
from dotenv import load_dotenv
import discord
import base64
import io
from utils.tools import format_answer

load_dotenv()
logger = logging.getLogger('DTF-Bot.Send')

# ┌─────────────────────────────────────────────────────────────────────────┐
# │                      DATA TEAM FORCE - AGENT API                        │
# └─────────────────────────────────────────────────────────────────────────┘


async def send_to_agent(question: str, thread_id: str) -> dict:
    """
    Send question and thread ID to epsilonAI agent

    Args:
        question: The user's question
        thread_id: The Discord thread ID

    Returns:
        The response from agent or error message
    """
    n8n_webhook_url = f"{os.getenv("N8N_WEBHOOK_URL")}"

    if not n8n_webhook_url:
        logger.error("N8N_WEBHOOK_URL not set in environment variables")
        return {"error": "❌ Error, cannot contact agent."}

    payload = {
        "question": question,
        "thread_id": thread_id,
    }
    
    logger.info(f"Sending request to agent - Thread: {thread_id}, Question length: {len(question)}")
    logger.info(f"Webhook URL: {n8n_webhook_url}")
    
    try:
        async with ClientSession() as session:
            async with session.post(
                n8n_webhook_url, json=payload, timeout=ClientTimeout(total=180)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully received response from agent (Thread: {thread_id})")
                    if data is None:
                        logger.warning(f"Agent returned empty response for thread {thread_id}")
                        return data
                    else:
                        logger.info(f"Response : {data}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"Agent returned status {response.status} for thread {thread_id}: {error_text}")
                    return {"error": f"❌ Oops, agent is down..."}

    except Exception as e:
        logger.error(f"Error communicating with agent (Thread: {thread_id}): {str(e)}", exc_info=True)
        return {"error": "❌ Error, an unexpected error occurred with agent."}


# ┌─────────────────────────────────────────────────────────────────────────┐
# │                      DISCORD MESSAGE UTILITIES                          │
# └─────────────────────────────────────────────────────────────────────────┘


async def send_to_target(target, content="", file=None, files=None):
    """Send message to either thread or reply, depending on context."""
    kwargs = {}
    kwargs["content"] = content
    if file:
        kwargs["file"] = file
    if files:
        kwargs["files"] = files
    
    logger.info(f"Sending message to {type(target).__name__} - has file: {file is not None}, has files: {files is not None}")

    if isinstance(target, discord.Thread):
        return await target.send(**kwargs)
    else:
        return await target.reply(**kwargs)


# ┌─────────────────────────────────────────────────────────────────────────┐
# │                        ANSWER FORMATTING                                │
# └─────────────────────────────────────────────────────────────────────────┘


async def send_answer(ctx, thread, answer):
    """Handle different answer types and send to appropriate channel."""
    target = ctx if isinstance(ctx.channel, discord.Thread) else thread
    
    logger.info(f"Preparing to send answer of type: {answer.get('type', 'unknown')}")

    if answer["type"] == "no-sql-query":
        logger.info(f"Sending no-SQL response to {ctx.author}")
        await send_to_target(
            target, content=f"{ctx.author.mention} {answer['response']}"
        )

    elif answer["type"] == "sql-query":
        content = format_answer(answer, author=ctx.author)
        logger.info(f"Sending SQL query response to {ctx.author}")

        files = []
        if "file" in answer and "markdown" in answer["file"]:
            markdown_file = answer["file"]["markdown"]
            markdown_data = base64.b64decode(markdown_file["data"])
            markdown_file_name = markdown_file.get("fileName", "query_explanation.csv")
            logger.info(f"Adding markdown file: {markdown_file_name} ({len(markdown_data)} bytes)")
            files.append(
                discord.File(io.BytesIO(markdown_data), filename=markdown_file_name)
            )

            if "csv" in answer["file"]:
                csv_file = answer["file"]["csv"]
                if csv_file and "data" in csv_file:
                    csv_data = base64.b64decode(csv_file["data"])
                    csv_file_name = csv_file.get("fileName", "query_results.csv")
                    logger.info(f"Adding CSV file: {csv_file_name} ({len(csv_data)} bytes)")
                    files.append(
                        discord.File(io.BytesIO(csv_data), filename=csv_file_name)
                    )

        if files:
            logger.info(f"Sending response with {len(files)} file(s)")
            await send_to_target(
                target,
                content=content,
                files=files,
            )
        else:
            logger.info("Sending response without files")
            await send_to_target(target, content=content)
