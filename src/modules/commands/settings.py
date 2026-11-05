import discord
from discord import app_commands
from discord.ext import commands

from resources.helpers import get_guild_icon
from resources.mrcookie import instance as bot
from resources.checks import lookup_counter, new_counter

@bot.tree.command(name="settings", description="View your server settings.")
@app_commands.describe(category="Choose which settings to view.")
@app_commands.choices(category=[
    app_commands.Choice(name="General", value="general"),
    app_commands.Choice(name="Counter", value="counter"),
    app_commands.Choice(name="Channels", value="channels")
])
@app_commands.guild_only()
async def settings(interaction: discord.Interaction, category: str = "general"):
    try:
        if interaction.guild is None:
            return await interaction.response.send_message(content="This command only works in servers!", ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(content="You can't use this command.", ephemeral=True)

        guildID = interaction.guild.id

        counterData = await lookup_counter(guildID)
        if counterData is False:
            await new_counter(guildID)
            counterData = await lookup_counter(guildID)

        if category == "general":
            # send the basic settings embed
            settings_embed = discord.Embed(
                description = "Use ``/settings`` and select a category for more information!",
                color = 0x9b59b6,
                )

            # title and profile icon
            settings_embed.set_author(name = interaction.guild.name + " Settings Page", icon_url = get_guild_icon(interaction))

            if str(counterData["settings"]["counter"]["Channel"]) == "0":
                counter_channel = "**Not Set**"
            else:
                counter_channel = "<#" + str(counterData["settings"]["counter"]["Channel"]) + ">"

            if counterData["settings"]["counter"]["badCounterRoleID"] is None or str(counterData["settings"]["counter"]["badCounterRoleID"]) == "0":
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
            await interaction.response.send_message(embed=settings_embed)

        if category == "counter":
            # send the counter settings embed
            counter_embed = discord.Embed(
                description = "Use ``/editcounter`` to edit the following counter settings.",
                color = 0x9b59b6,
                )

            # title and profile icon
            counter_embed.set_author(name = interaction.guild.name + " Counter Settings", icon_url = get_guild_icon(interaction))

            if str(counterData["settings"]["counter"]["Channel"]) == "0":
                counter_channel = "**Not Set**"
            else:
                counter_channel = "<#" + str(counterData["settings"]["counter"]["Channel"]) + ">"

            if counterData["settings"]["counter"]["badCounterRoleID"] is None or str(counterData["settings"]["counter"]["badCounterRoleID"]) == "0":
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

            await interaction.response.send_message(embed=counter_embed)

        if category == "channels":
            # send the channel settings embed
            channel_embed = discord.Embed(
                description = "Choose the channels where the bot should ignore commands or cookie drops",
                color = 0x9b59b6,
                )

            # title and profile icon
            channel_embed.set_author(name = interaction.guild.name + " Channel Settings", icon_url = get_guild_icon(interaction))

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
            value = "To edit these channels, run ``/ignoredrops``." + "\n" +
            "Ignored Cookie Drop Channels: " + "\n" + str(ID_list),
            inline = False)

            channel_embed.add_field(name = "🔒 Ignored Command Channels",
            value = "To edit these channels, run ``/ignorechannels``." + "\n" +
            "Ignored Command Channels: " + "\n" + str(ID_list_commands),
            inline = False)

            await interaction.response.send_message(embed=channel_embed)

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error), ephemeral=True)
        else:
            await interaction.response.send_message(str(Error), ephemeral=True)