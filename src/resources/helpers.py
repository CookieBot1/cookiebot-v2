import discord
from discord.ext import commands
from resources.mrcookie import instance as bot

from datetime import datetime, timezone
import asyncio


YES = {"yes", "y", "true", "on", "enable", "enabled"}
NO  = {"no", "n", "false", "off", "disable", "disabled"}



class SetupCancelled(Exception):
    pass

CANCEL_WORDS = {"cancel", "stop", "quit", "exit", "abort"}

async def handle_cancel(msg):
    if msg.content and msg.content.strip().lower() in CANCEL_WORDS:
        raise SetupCancelled()

async def ask_yes_no(ctx, question: str, *, timeout: float = 30.0, default: bool = False, cleanup=None) -> bool:
    if question:
        qmsg = await ctx.send(question + " Type `cancel` to stop setup.")
        if cleanup is not None:
            cleanup.append(qmsg)

        def check(m: discord.Message) -> bool:
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.guild is not None

        try:
            msg: discord.Message = await bot.wait_for("message", timeout=timeout, check=check)
            if cleanup is not None:
                cleanup.append(msg)

            await handle_cancel(msg)

            content = msg.content.strip().lower()

            if content in YES:
                return True
            if content in NO:
                return False

            await ctx.send(f"Invalid response - Using default: **{default}**.")
            return default

        except asyncio.TimeoutError:
            await ctx.send(f"No response — using default: **{default}**.")
            return default


async def ask_role(ctx, question: str, *, timeout: float = 45.0, cleanup=None):
    qmsg = await ctx.send(question + " Type `cancel` to stop setup.")
    if cleanup is not None:
        cleanup.append(qmsg)

    def check(m: discord.Message) -> bool:
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.guild is not None

    try:
        msg: discord.Message = await bot.wait_for("message", timeout=timeout, check=check)
        if cleanup is not None:
            cleanup.append(msg)

        await handle_cancel(msg)

        ## mention
        if msg.role_mentions:
            return msg.role_mentions[0]

        raw = msg.content.strip()

        ## ID
        if raw.isdigit():
            role = ctx.guild.get_role(int(raw))
            if role:
                return role

        ## name
        role = discord.utils.get(ctx.guild.roles, name=raw)
        if role:
            return role

        await ctx.send("Couldn’t find that role.")
        return None

    except asyncio.TimeoutError:
        await ctx.send("No response.")
        return None

def make_check(ctx):
    def _check(m: discord.Message) -> bool:
        return (
            m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id
            and m.guild is not None
        )
    return _check

def get_latest_active_alert():
    alert = bot.latest_alert
    if not alert:
        return None

    exp = alert.get("expiresAt")
    if exp and datetime.fromisoformat(exp) <= datetime.now(timezone.utc):
        bot.latest_alert = None
        return None

    return alert

def get_guild_icon(ctx):
    try:
        return ctx.guild.icon.url
    except AttributeError:
        return ctx.bot.user.display_avatar.url