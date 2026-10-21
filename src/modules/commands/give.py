from resources.mrcookie import instance as bot
import discord
from discord import app_commands

from resources.checks import lookup_database, new_database, update_value, is_blacklisted

@bot.tree.command(name="give", description="Give cookies to another user.")
@app_commands.guild_only()
@app_commands.describe(user="The user to give cookies to.", amount="The number of cookies to give.")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    try:
        await interaction.response.defer()

        guildID = interaction.guild.id
        userID = str(user.id)
        senderID = str(interaction.user.id)

        sender = interaction.user

        ## validation
        if user.id == interaction.user.id:
            raise Exception("Invalid user, you can't give cookies to yourself!")

        if await is_blacklisted(userID):
            raise Exception("Illegal activity! You can't give to a blacklisted user!")

        if amount <= 0:
            raise Exception("Invalid amount, try again!")

        ## fetching userData
        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userCookies = userData["users"][userID]["Cookies"]

        ## fetching senderData
        senderData = await lookup_database(senderID, guildID)
        if senderData == False:
            await new_database(senderID, guildID)
            senderData = await lookup_database(senderID, guildID)
        senderCookies = senderData["users"][senderID]["Cookies"]

        ## check if sender has enough cookies
        if senderCookies < amount:
            raise Exception("Ahem- you don't have that many cookies..")

        ## transfer the cookies
        userCookies += amount
        senderCookies -= amount

        ## update the database
        await update_value(userID, guildID, "Cookies", userCookies)
        await update_value(senderID, guildID, "Cookies", senderCookies)

        ## send the embed
        give_embed = discord.Embed(
            title="💨 " + str(amount) + " Cookies Transferring..",
            color=0x2ecc71,
        )

        give_embed.add_field(
            name="",
            value="🍪 " + user.display_name + " now has **" + str(userCookies) + " cookies!**",
            inline=False
        )

        give_embed.set_author(name="", icon_url=sender.display_avatar)
        give_embed.set_footer(text="Cookies delivered by Sam")

        await interaction.followup.send(embed=give_embed)

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error), ephemeral=True)
        else:
            await interaction.response.send_message(str(Error), ephemeral=True)