import discord
from discord.ext import commands

from resources.mrcookie import instance as bot
from resources.checks import lookup_server, new_server, update_server
from resources.constants import JUNO_ID

@bot.command(aliases = ["junomode", "diddy", "diddymode"])
async def juno(ctx, state: str = "on"):
    try:
        guildID = ctx.guild.id

        if ctx.guild is None:
            return await ctx.message.reply(content="This commands only works in servers!", delete_after=5)

        if ctx.author.id == JUNO_ID:
            await ctx.message.reply(content="**Disabling Juno Mode- SIKEEEE!**")
            await ctx.message.reply(content="You CANTTT disable your OWN COMMANDD.. CMON JUNO... LLLL HAHAHA 🫵🤣🤣🤣")
            await ctx.message.reply(content="https://tenor.com/view/ill-be-missing-you-missing-you-p-diddy-puff-daddy-big-gif-22616397")
            return
        elif not ctx.author.guild_permissions.manage_guild:
            return await ctx.message.reply(content="You can't use this command.", delete_after=5)

        state = str(state).lower()

        TRUE_VALUES = {"true", "on", "enable", "enabled", "yes", "1"}
        FALSE_VALUES = {"false", "off", "disable", "disabled", "no", "0"}

        if state in TRUE_VALUES:
            state_bool = True
        elif state in FALSE_VALUES:
            state_bool = False
        else:
            return await ctx.send("❌ Invalid value. Use: `on/off`, `true/false`, `enable/disable`, `yes/no`")

        serverData = await lookup_server(guildID)
        if serverData is False:
            await new_server(guildID)

        await update_server(guildID, "juno", state_bool)
        await ctx.send(f"Juno Mode has been set to **{state_bool}**!")

    except Exception as Error:
        await ctx.send(Error)