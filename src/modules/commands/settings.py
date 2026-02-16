import discord
from discord.ext import commands

from resources.helpers import get_guild_icon
from resources.mrcookie import instance as bot
from resources.checks import lookup_counter, new_counter

@bot.command(aliases = ["setting"])
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
        
        if category == "general" or category == "gen" or category == "view":
            # send the basic settings embed
            settings_embed = discord.Embed(
                description = "Use ``.settings (category)`` for more information!",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            settings_embed.set_author(name = ctx.guild.name + " Settings Page", icon_url = get_guild_icon(ctx))

            if str(counterData["settings"]["counter"]["Channel"]) == "0":
                counter_channel = "**Not Set**"
            else:
                counter_channel = "<#" + str(counterData["settings"]["counter"]["Channel"]) + ">"

            if str(counterData["settings"]["counter"]["badCounterRoleID"]) == None or str(counterData["settings"]["counter"]["badCounterRoleID"]) == "0":
                bad_role = "**Not Set**"
            else:
                bad_role = "<@&" + str(counterData["settings"]["counter"]["badCounterRoleID"]) + ">"

            if str(counterData["settings"]["counter"]["badCounterRoleFails"]) == "0" or counterData["settings"]["counter"]["badCounterRoleFails"] == None:
                bad_role_fails = "**Not Set**"
            else:
                bad_role_fails = "**" + str(counterData["settings"]["counter"]["badCounterRoleFails"]) + " fails**"            

            settings_embed.add_field(name = "💯 Counter", value = 
            "Counter Channel: " + counter_channel + "\n" +
            "Bad Counter Role: " + bad_role + "\n" +
            "Allow Math: **" + str(counterData["settings"]["counter"]["AllowMath"]) + "**\n" +
            "Assign Bad Counter Role Every: " + bad_role_fails
            ,inline = False)

            ignored = counterData["settings"]["server"].get("IgnoredChannelDrops", [])
            if not ignored:
                ID_list = "**No Channels Set**"
            else:
                ID_list = ", ".join(f"<#{int(ch_id)}>" for ch_id in ignored)

            ignored_commands = counterData["settings"]["server"].get("IgnoredChannels", [])
            if not ignored_commands:
                ID_list_commands = "**No Channels Set**"
            else:
                ID_list_commands = ", ".join(f"<#{int(ch_id)}>" for ch_id in ignored_commands)

            settings_embed.add_field(name = " 📌 Channels", 
            value = "Ignored Cookie Drop Channels: " + "\n" + str(ID_list) + "\n" +
            "Ignored Command Channels: " + "\n" + str(ID_list_commands),
            inline = False)

            settings_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=settings_embed)

        if category == "counter" or category == "count":
            # send the counter settings embed
            counter_embed = discord.Embed(
                description = "Use ``.editcounter <category>`` to edit the following counter settings.",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            counter_embed.set_author(name = ctx.guild.name + " Counter Settings", icon_url = get_guild_icon(ctx))

            if str(counterData["settings"]["counter"]["Channel"]) == "0":
                counter_channel = "**Not Set**"
            else:
                counter_channel = "<#" + str(counterData["settings"]["counter"]["Channel"]) + ">"

            if str(counterData["settings"]["counter"]["badCounterRoleID"]) == None or str(counterData["settings"]["counter"]["badCounterRoleID"]) == "0":
                bad_role = "**Not Set**"
            else:
                bad_role = "<@&" + str(counterData["settings"]["counter"]["badCounterRoleID"]) + ">"

            if str(counterData["settings"]["counter"]["badCounterRoleFails"]) == "0" or counterData["settings"]["counter"]["badCounterRoleFails"] == None:
                bad_role_fails = "**Not Set**"
            else:
                bad_role_fails = "**" + str(counterData["settings"]["counter"]["badCounterRoleFails"]) + " fails**"         

            counter_embed.add_field(name = "💯 Channel", value = 
            "Counter Channel: " + counter_channel, inline = False)

            counter_embed.add_field(name = "🔵 Role", value =
            "Bad Counter Role: " + bad_role + "\n" +
            "Assign Bad Counter Role Every: " + bad_role_fails, inline = False)

            counter_embed.add_field(name = "🧮 Math", value =
            "Allow Math: **" + str(counterData["settings"]["counter"]["AllowMath"]) + "**", inline = False)

            await ctx.send(embed=counter_embed)

        if category == "channels" or category == "channel":
            # send the channel settings embed
            channel_embed = discord.Embed(
                description = "Choose the channels where the bot should ignore commands or cookie drops",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            channel_embed.set_author(name = ctx.guild.name + " Channel Settings", icon_url = get_guild_icon(ctx))

            ignored = counterData["settings"]["server"].get("IgnoredChannelDrops", [])
            if not ignored:
                ID_list = "**No Channels Set**"
            else:
                ID_list = ", ".join(f"<#{int(ch_id)}>" for ch_id in ignored)

            ignored_commands = counterData["settings"]["server"].get("IgnoredChannels", [])
            if not ignored_commands:
                ID_list_commands = "**No Channels Set**"
            else:
                ID_list_commands = ", ".join(f"<#{int(ch_id)}>" for ch_id in ignored_commands)

            channel_embed.add_field(name = "🍪 Ignored Cookie Drops", 
            value = "To edit these channels, run ``.ignoredrops <optional: #channel>``." + "\n" +
            "Ignored Cookie Drop Channels: " + "\n" + str(ID_list),
            inline = False)

            channel_embed.add_field(name = "🔒 Ignored Command Channels", 
            value = "To edit these channels, run ``.ignorechannels <optional: #channel>``." + "\n" +
            "Ignored Command Channels: " + "\n" + str(ID_list_commands),
            inline = False)

            await ctx.send(embed=channel_embed)

    except Exception as Error:
        await ctx.send(Error)