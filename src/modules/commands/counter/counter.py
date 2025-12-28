import discord

from resources.checks import lookup_counter, update_counter, update_value, lookup_database, new_database
from resources.mrcookie import instance as bot


import ast
import operator as op

# Allowed operators
_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,          # optional (you can remove if you don't want **)
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def safe_eval_int(expr: str) -> int | None:
    """
    Safely evaluate a math expression and return an int if it is exactly an integer.
    Returns None if invalid / not an integer.
    """
    expr = expr.strip().replace("×", "*").replace("÷", "/")

    # quick reject of long spam
    if len(expr) > 32:
        return None

    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError:
        return None

    def _eval(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Num):  # older AST nodes (safe)
            return n.n
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(n.op)](_eval(n.operand))
        raise ValueError("disallowed expression")

    try:
        value = _eval(node)
    except Exception:
        return None

    # Only accept results that are mathematically integers (2.0 ok, 2.5 not ok)
    if isinstance(value, float) and not value.is_integer():
        return None

    return int(value)


@bot.listen()
async def on_message(message: discord.Message):
    if message.guild is None or message.author.bot:
        return

    counterData = await lookup_counter(message.guild.id)
    if counterData is False:
        return

    channelID = counterData["settings"]["counter"]["Channel"]
    if channelID == 0:
        return  # Channel could not be found.
    channel = bot.get_channel(channelID) or await bot.fetch_channel(channelID)
    if not channel:
        return  # Channel could not be found.

    guild = bot.get_guild(message.guild.id)
    userID = str(message.author.id)
    user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))
    guildID = message.guild.id
    try:
        allow_math = counterData["settings"]["counter"]["AllowMath"]

        if message.channel.id != channelID:
            return

        raw = message.content.strip()

        # always accept normal numbers
        parsed = int(raw) if raw.isdigit() else None

        # optionally accept calculator expressions
        allow_math = counterData["settings"]["counter"].get("AllowMath", False)
        if parsed is None and allow_math:
            parsed = safe_eval_int(raw)

        if parsed is None:
            return

        ## setting vars
        savedCounter = counterData["settings"]["counter"]["Counter"]  # last accepted number
        lastUser = counterData["settings"]["counter"]["lastUser"]  # user who sent last message
        userData = await lookup_database(userID, guildID) 
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userCounter = userData["users"][userID]["Counter"]
        userFailCounter = userData["users"][userID]["FailCounter"]
        highScore = counterData["settings"]["counter"]["highScore"]

        if parsed == savedCounter + 1:
            if userID != lastUser:
                savedCounter = parsed
                userCounter += 1
                await update_counter(guildID, "Counter", savedCounter)
                await update_counter(guildID, "lastUser", userID)
                await update_value(userID, guildID, "Counter", userCounter)
                await message.add_reaction("✅")

                if savedCounter > highScore:
                    highScore = savedCounter
                    await update_counter(guildID, "highScore", highScore)
            else:
                raise ValueError(user.mention + " FAILED AT **" + str(savedCounter) + "**!! You can't count two times in a row.")
        else:
            raise ValueError(user.mention + " FAILED AT **" + str(savedCounter) + "**!! You said the wrong number.")
    
    except ValueError as Error:
        userFailCounter += 1
        await update_value(userID, guildID, "FailCounter", userFailCounter)
        await channel.send(str(Error))

        failedCount_embed = discord.Embed(
            title = "❌ Counter Reset",
            description = "Start counting back at **1** again. Want to save the count? You can buy saves with cookies in ``.shop``",
            color = 0x992d22
            )

        failedCount_embed.set_footer(text = 'Want to see a leaderboard of who failed the most? Run ".failboard"')
        await channel.send(embed=failedCount_embed)

        await update_counter(guildID, "Counter", 0)
        await update_counter(guildID, "lastUser", 0)