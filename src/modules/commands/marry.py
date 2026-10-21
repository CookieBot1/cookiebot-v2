from resources.mrcookie import instance as bot
import discord
from discord import app_commands
from datetime import datetime, timezone

from resources.checks import lookup_database, new_database, update_value, is_blacklisted

BELLA_ID = 846544080111665182
JOHN_ID = 194962036784889858


class MarriageView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=30)
        self.user = user
        self.accepted = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "This proposal is not for you!",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="💍")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.accepted = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="💔")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.accepted = False
        await interaction.response.defer()
        self.stop()


@bot.tree.command(name="marry", description="Propose marriage to another user.")
@app_commands.guild_only()
@app_commands.describe(user="The user you want to marry.")
@app_commands.checks.cooldown(1, 15, key=lambda interaction: interaction.user.id)
async def marry(interaction: discord.Interaction, user: discord.Member):
    try:
        await interaction.response.defer()

        guildID = interaction.guild.id
        userID = str(user.id)
        senderID = str(interaction.user.id)

        ## Bella is only allowed to marry John 💜
        if senderID == str(BELLA_ID) and userID != str(JOHN_ID):
            await interaction.followup.send(
                "You must've been hacked bellita, because you're already married to Johnny. 💜\n"
                "Request denied. You already have your man."
            )
            return
        if userID == str(BELLA_ID) and senderID != str(JOHN_ID):
            await interaction.followup.send(
                "Absolutely not. Bella is already reserved for Johnny. 💜"
            )
            return

        sender = interaction.user

        ## validation
        if user.id == interaction.user.id:
            raise Exception("Invalid user, you can't marry yourself!")

        if await is_blacklisted(userID):
            raise Exception("Illegal activity! You can't marry a blacklisted user!")

        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)

        senderData = await lookup_database(senderID, guildID)
        if senderData == False:
            await new_database(senderID, guildID)
            senderData = await lookup_database(senderID, guildID)

        ## db check
        userThing = userData["users"].get(userID, {})
        senderThing = senderData["users"].get(senderID, {})

        userStatus = userThing.get("Married")
        senderStatus = senderThing.get("Married")

        userMarried = 0 if userStatus is None else int(userStatus)
        senderMarried = 0 if senderStatus is None else int(senderStatus)

        ## checks
        if userMarried != 0:
            raise Exception("This user is already married!")

        if senderMarried != 0:
            raise Exception("You are already married!")

        ## ask user first
        view = MarriageView(user)

        proposal_embed = discord.Embed(
            title="💍 Marriage Proposal",
            description=f"{user.mention}, {sender.mention} wants to marry you!\n\nDo you accept?",
            color=0xf1c40f
        )

        proposal_message = await interaction.followup.send(embed=proposal_embed, view=view, wait=True)

        await view.wait()

        try:
            await proposal_message.delete()
        except:
            pass

        if view.accepted is None:
            return await interaction.followup.send("⏰ Marriage proposal timed out!")

        if view.accepted == False:
            return await interaction.followup.send("💔 Marriage proposal declined.")

        ## marry them
        userMarried = senderID
        senderMarried = userID

        ## embed
        marry_embed = discord.Embed(
            title="💍 Marrying " + user.display_name + "..",
            description=f"{sender.mention} and {user.mention} are now **MARRIED**!",
            color=0x00ff00
        )
        await interaction.followup.send(embed=marry_embed)

        ## update db
        await update_value(userID, guildID, "Married", userMarried)
        await update_value(senderID, guildID, "Married", senderMarried)

        marriage_date = datetime.now(timezone.utc)

        await update_value(userID, guildID, "MarriageDate", marriage_date)
        await update_value(senderID, guildID, "MarriageDate", marriage_date)

        await update_value(userID, guildID, "PartnerCookiesGiven", 0)
        await update_value(senderID, guildID, "PartnerCookiesGiven", 0)

        await update_value(userID, guildID, "CoupleCookiesEarned", 0)
        await update_value(senderID, guildID, "CoupleCookiesEarned", 0)

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error), ephemeral=True)
        else:
            await interaction.response.send_message(str(Error), ephemeral=True)


@marry.error
async def marry_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Slow down! Try again in **{round(error.retry_after)} seconds**.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"An error occurred: {str(error)}",
            ephemeral=True
        )