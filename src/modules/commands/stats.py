from resources.mrcookie import instance as bot
import discord

from resources.checks import lookup_counter, lookup_database, new_database

@bot.command(aliases = ["serverstats", "guildstats"])
async def stats(ctx):
    try:
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)

        counterData = await lookup_counter(guildID)
        if counterData is False:
            await new_counter(guildID)
            counterData = await lookup_counter(guildID)

        highScore = counterData["settings"]["counter"]["highScore"]

        ## send the embed
        stats_embed = discord.Embed(
            title = guild.name + " Stats",
            color = 0x7289da,
            )

        stats_embed.add_field(name = "🧮 Highest Number Counted", value = "Server Record: **" + str(highScore) + "**", inline = False)
        stats_embed.add_field(name = "💰 Richest In Cookies", value = "**WIP Name** has **WIP** Cookies", inline = False)
        stats_embed.add_field(name = "😯 Highest Robberies", value = "**WIP Name** stole **WIP** Total Cookies", inline = False)
        stats_embed.add_field(name = "❔ WIP Title", value = "WIP Data", inline = False)

        stats_embed.set_thumbnail(url = guild.icon.url)

        await ctx.send(embed=stats_embed)

    except Exception as Error:
        await ctx.send(Error)
