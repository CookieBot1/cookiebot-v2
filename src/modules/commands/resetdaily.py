from datetime import datetime, timedelta

import discord
from discord import app_commands

from resources.constants import ADMIN_USERS
from resources.mrcookie import instance as bot


@bot.tree.command(name="resetdaily", description="Restore daily streak eligibility across all servers.")
@app_commands.default_permissions(administrator=True)
async def resetdaily(interaction: discord.Interaction):
    if interaction.user.id not in ADMIN_USERS:
        return await interaction.response.send_message(
            "Only bot administrators can use this command.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    reset_time = datetime.now() - timedelta(seconds=5)

    total_users = 0
    total_servers = 0

    for guild in bot.guilds:
        guild_data = await bot.db.get_guild_users(guild.id)

        if not guild_data:
            continue

        guild_users = guild_data.get("users", {})
        updates = {}

        for userID, userData in guild_users.items():
            if userData.get("Streaks", 0) <= 0:
                continue

            updates[f"users.{userID}.DailyExpire"] = reset_time
            total_users += 1

        if updates:
            await bot.db.update_one(
                {"_id": str(guild.id)},
                {"$set": updates}
            )
            total_servers += 1

    await interaction.followup.send(
        f"Daily streak eligibility restored!\n"
        f"**Users updated:** {total_users}\n"
        f"**Servers updated:** {total_servers}\n\n"
        "Everyone with an existing streak can now claim `/daily` without losing it, "
        "provided they claim within approximately 24 hours.",
        ephemeral=True
    )