import time
import discord
from discord import app_commands
from resources.mrcookie import instance as bot
from resources.checks import is_admin, validate_user, is_blacklisted

@bot.tree.command(name="blacklist", description="Blacklist a user from CookieBot.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(temp_id="The Discord ID of the user to blacklist.")
async def blacklist(interaction: discord.Interaction, temp_id: str):
    try:
        if await is_admin(interaction.user.id) == False:
            raise Exception("You don't have permission to run this command.")

        userID = await validate_user(temp_id)
        if userID == None:
            raise Exception("Invalid user.")

        if interaction.user.id == int(userID):
            raise Exception("You can't blacklist yourself.")

        if await is_blacklisted(userID) == True:
            raise Exception("User is already blacklisted.")

        # writing in DB
        await bot.db.add_blacklist({"_id": str(userID)})

        # cache update
        bot.blacklist_cache[userID] = (True, time.time())

        await interaction.response.send_message("Blacklisted " + str(userID))

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error), ephemeral=True)
        else:
            await interaction.response.send_message(str(Error), ephemeral=True)