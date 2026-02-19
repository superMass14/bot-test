# ┌─────────────────────────────────────────────────────────────────────────┐
# │                           DEBUG                                         │
# └─────────────────────────────────────────────────────────────────────────┘


def debug(ctx):
    """
    Debug logging function to print message context.

    Args:
        ctx: Discord context object containing message information
    """
    print(f"Received /hello command from {ctx.author}")
    print(
        f"Context: {ctx.channel},\
           \n\r-Server: {ctx.guild}, \
           \n\r-Content: {ctx.content}, \
           \n\r-Author: {ctx.author},"
    )


# ┌─────────────────────────────────────────────────────────────────────────┐
# │                      ANSWER FORMATTING                                  │
# └─────────────────────────────────────────────────────────────────────────┘


def format_answer(answer: dict, author=None) -> str:
    """
    Format agent answer into a Discord-friendly message.

    Extracts query, explanation, and preview from answer dict and formats
    them as a Discord message with proper markdown code blocks.

    Args:
        answer (dict): Response from agent containing 'query', 'explanation', 'head'
        author: Discord user object for mention

    Returns:
        str: Formatted message ready to send to Discord
    """
    # query = answer.get("query", "N/A")
    # explanation = answer.get("explanation", "N/A")
    head = answer.get("head", {})
    preview = head.get("preview", False)
    result = head.get("result", "N/A")
    mention = f"{author.mention}" if author else ""
    if preview:
        output = f"{mention} Here is the result of your query:\n## Preview:\n{result}\n"
    else:
        output = f"{mention} **{result}**\n\n"
    return output
