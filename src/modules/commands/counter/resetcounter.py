from resources.mrcookie import instance as bot
from resources.checks import update_counter, lookup_counter
import discord

@bot.command(aliases = ["disablecounter"])
async def resetcounter(ctx):
    guildID = ctx.guild.id
    counterData = await lookup_counter(ctx.guild.id)
    channelID = counterData["settings"]["counter"]["Channel"]

    if ctx.guild is None:
        return await ctx.message.reply(content="This commands only works in servers!", delete_after=5)

    if not ctx.author.guild_permissions.manage_guild:
        return await ctx.message.reply(content="You can't use this command.", delete_after=5)

    if channelID == 0:
        counter_embed = discord.Embed(
            title = "😵‍💫 Nothing To Reset!",
            description = "There's no counter channel set, want to set one? Run ``.setcounter`` in that channel.",
            color = 0x992d22,
            )

        counter_embed.set_footer(text = 'To find out how counting works, run ".help counter"')
        await ctx.send(embed=counter_embed)
    else:
        await update_counter(guildID, "Channel", 0)
        await update_counter(guildID, "Counter", 0)
        await update_counter(guildID, "lastUser", 0)
        await update_counter(guildID, "AllowMath", False)
        await update_counter(guildID, "badCounterRoleEnabled", False)

        counter_embed = discord.Embed(
            title = "🧽 Counter Channel Cleared",
            description = "Want to set another counter channel? Run ``.setcounter`` in that channel.",
            color = 0x2ecc71,
            )

        counter_embed.set_footer(text = 'To find out how counting works, run ".help counter"')
        await ctx.send(embed=counter_embed)