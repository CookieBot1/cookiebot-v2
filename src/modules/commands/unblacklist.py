import time
import discord
from discord import app_commands
from resources.mrcookie import instance as bot
from resources.checks import is_admin, is_blacklisted

@bot.tree.command(name="unblacklist", description="Remove a user from CookieBot's global blacklist.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(user_id="The Discord user ID to unblacklist.")
async def unblacklist(interaction: discord.Interaction, user_id: str):
    try:
        await interaction.response.defer(ephemeral=True)

        if await is_admin(interaction.user.id) == False:
            raise Exception("You don't have permission to run this command.")

        userID = user_id.strip()
        if not userID.isdigit():
            raise Exception("Invalid user.")

        if await is_blacklisted(userID) == False:
            raise Exception("User is not blacklisted.")

        # writing in db
        await bot.db.del_blacklist({"_id": str(userID)})

        # cache update
        bot.blacklist_cache[userID] = (False, time.time())

        await interaction.followup.send("Unblacklisted " + str(userID))

    except Exception as Error:
        await interaction.followup.send(str(Error))
