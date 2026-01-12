import discord
from discord.ext import commands

from resources.mrcookie import instance as bot
from resources.checks import lookup_counter, new_counter

@bot.command(aliases = ["config", "setting"])
async def settings(ctx, category = "general"):
    try:
        guildID = ctx.guild.id

        if ctx.guild is None:
            return await ctx.message.reply(content="This commands only works in servers!", delete_after=5)

        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.message.reply(content="You can't use this command.", delete_after=5)

        counterData = await lookup_counter(guildID)
        if counterData is False:
            await new_counter(guildID)
            counterData = await lookup_counter(guildID)
        
        if category == "general":
            # send the basic settings embed
            settings_embed = discord.Embed(
                description = "Use ``.settings (category)`` for more information!",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            settings_embed.set_author(name = ctx.guild.name + " Settings Page", icon_url = ctx.guild.icon.url)

            settings_embed.add_field(name = "💯 Counter", value = 
            "Counter Channel: <#" + str(counterData["settings"]["counter"]["Channel"]) + ">" + "\n" +
            "Allow Math: **" + str(counterData["settings"]["counter"]["AllowMath"]) + "**\n" +
            "Bad Counter Role: **WIP**" + "\n" +
            "Assign Counter Role Every: **WIP**" + "\n"
            ,inline = False)

            ##ID_list = "<#, <#".join(counterData["settings"]["server"]["IgnoredChannelDrops"])
            ##settings_embed.add_field(name = "🍪 Cookies", value = 
            ##"Ignored Drop Channels: " + str(ID_list) + "\n"
            ##,inline = False)

            settings_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=settings_embed)

    except Exception as Error:
        await ctx.send(Error)