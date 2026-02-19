from aiohttp import ClientTimeout, ClientSession
import os
from dotenv import load_dotenv
import discord
import base64
import io
from utils.tools import format_answer

load_dotenv()

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
        print("N8N_WEBHOOK_URL not set in environment variables")
        return {"error": "❌ Error, cannot contact agent."}

    payload = {
        "question": question,
        "thread_id": thread_id,
    }
    try:
        async with ClientSession() as session:
            async with session.post(
                n8n_webhook_url, json=payload, timeout=ClientTimeout(total=180)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    print(f"Agent returned status {response.status}: {error_text}")
                    return {"error": f"❌ Oops, agent is down..."}

    except Exception as e:
        print(f"Error communicating with agent: {str(e)}")
        return {"error": "❌ Error, an unexpected error occurred with agent."}


# ┌─────────────────────────────────────────────────────────────────────────┐
# │                      DISCORD MESSAGE UTILITIES                          │
# └─────────────────────────────────────────────────────────────────────────┘


async def send_to_target(target, content="", files=None):
    """Send message to either thread or reply, depending on context."""
    kwargs = {}
    kwargs["content"] = content
    if files:
        kwargs["files"] = files

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

    if answer["type"] == "no-sql-query":
        await send_to_target(
            target, content=f"{ctx.author.mention} {answer['response']}"
        )

    elif answer["type"] == "sql-query":
        content = format_answer(answer, author=ctx.author)

        files = []
        if "file" in answer and "markdown" in answer["file"]:
            markdown_file = answer["file"]["markdown"]
            markdown_data = base64.b64decode(markdown_file["data"])
            markdown_file_name = markdown_file.get("fileName", "query_explanation.csv")
            files.append(
                discord.File(io.BytesIO(markdown_data), filename=markdown_file_name)
            )

            if "csv" in answer["file"]:
                csv_file = answer["file"]["csv"]
                if csv_file and "data" in csv_file:
                    csv_data = base64.b64decode(csv_file["data"])
                    csv_file_name = csv_file.get("fileName", "query_results.csv")
                    files.append(
                        discord.File(io.BytesIO(csv_data), filename=csv_file_name)
                    )

        if files:
            await send_to_target(
                target,
                content=content,
                files=files,
            )
        else:
            await send_to_target(target, content=content)
