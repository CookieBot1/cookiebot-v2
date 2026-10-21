from resources.mrcookie import instance as bot
import discord
from discord import app_commands

from resources.checks import lookup_counter, lookup_server, new_counter

@bot.tree.command(name="stats", description="View this server's statistics and top players.")
@app_commands.guild_only()
async def stats(interaction: discord.Interaction):
    try:
        await interaction.response.defer()

        guildID = interaction.guild.id
        guild = interaction.guild

        counterData = await lookup_counter(guildID)
        if counterData is False:
            await new_counter(guildID)
            counterData = await lookup_counter(guildID)

        ## get high score from counter data
        highScore = counterData["settings"]["counter"]["highScore"]

        ## this block fetches their data from the database
        userData = await lookup_server(guildID)
        if userData == False:
            raise Exception("Insufficient server data found, try again later.")

        ## figure out who's #1 in each category
        guild_users: dict = userData.get("users", {})

        stats = ["Cookies", "RobCount", "RobGains", "Counter"]
        leaders = {}
        for stat in stats:
            if not guild_users:
                leaders[stat] = (None, 0)
            else:
                uid, data = max(
                    guild_users.items(),
                    key=lambda item: item[1].get(stat, 0)
                )
                leaders[stat] = (uid, data.get(stat, 0))

        ## send the embed
        stats_embed = discord.Embed(
            title = guild.name + " Stats",
            color = 0x7289da,
            )

        stats_embed.add_field(name = "🧮 Highest Number Counted", value = "Server Record: **" + str(highScore) + "**", inline = False)

        # Ranking stuff for Numbers Counted
        count_uid, count_val = leaders["Counter"]
        if count_uid is None:
            count_name = "Insufficient Data"
        else:
            user = bot.get_user(int(count_uid)) or await bot.fetch_user(int(count_uid))
            count_name = user.global_name or user.name
        stats_embed.add_field(name = "🧐 Most Numbers Counted", value = f"**{count_name}** has counted **{count_val}** time{'s' if count_val != 1 else ''}", inline = False)

        # Ranking stuff for Cookies
        top_uid, top_cookies = leaders["Cookies"]
        if top_uid is None:
            top_name = "Insufficient Data"
        else:
            user = bot.get_user(int(top_uid)) or await bot.fetch_user(int(top_uid))
            top_name = user.global_name or user.name
        stats_embed.add_field(name = "🍪 Richest In Cookies", value = f"**{top_name}** has **{top_cookies}** cookie{'s' if top_cookies != 1 else ''}", inline = False)

        # Ranking stuff for RobCount
        rob_uid, rob_val = leaders["RobCount"]
        if rob_uid is None:
            rob_name = "Insufficient Data"
        else:
            user = bot.get_user(int(rob_uid)) or await bot.fetch_user(int(rob_uid))
            rob_name = user.global_name or user.name
        stats_embed.add_field(name = "🎭 Most Notorious Criminal", value = f"**{rob_name}** committed **{rob_val}** robber{'ies' if rob_val != 1 else 'y'}", inline = False)

        # Ranking stuff for RobGains
        rich_rob_uid, rich_rob_val = leaders["RobGains"]
        if rich_rob_uid is None:
            rich_rob_name = "Insufficient Data"
        else:
            user = bot.get_user(int(rich_rob_uid)) or await bot.fetch_user(int(rich_rob_uid))
            rich_rob_name = user.global_name or user.name
        stats_embed.add_field(name = "💰 Richest Thief", value = f"**{rich_rob_name}** stole **{rich_rob_val}** cookie{'s' if rich_rob_val != 1 else ''}", inline = False)

        if guild.icon:
            stats_embed.set_thumbnail(url=guild.icon.url)

        await interaction.followup.send(embed=stats_embed)

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error), ephemeral=True)
        else:
            await interaction.response.send_message(str(Error), ephemeral=True)