import discord
from discord import app_commands
from resources.mrcookie import instance as bot

from resources.checks import lookup_database, new_database, update_value

@bot.tree.command(name="eat", description="Eat one of your cookies.")
@app_commands.guild_only()
async def eat(interaction: discord.Interaction):
    try:
        await interaction.response.defer()

        userID = str(interaction.user.id)
        guildID = interaction.guild.id

        ## this block fetches user data from the database
        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userCookies = userData["users"][userID]["Cookies"]

        if userCookies < 1:
            raise Exception("You have no cookies to eat!")
        else:
            userCookies -= 1
            await update_value(userID, guildID, "Cookies", userCookies)
            await interaction.followup.send("Nom nom, you ate 1 cookie 🍪")

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error), ephemeral=True)
        else:
            await interaction.response.send_message(str(Error), ephemeral=True)