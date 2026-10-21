from resources.mrcookie import instance as bot
import discord
from discord import app_commands

from resources.checks import lookup_database, new_database, update_value

class DivorceView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=30)
        self.user = user
        self.confirmed = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "This is not your decision!",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.red, emoji="💔")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        await interaction.response.defer()
        self.stop()


@bot.tree.command(name="divorce", description="Divorce your current partner.")
@app_commands.guild_only()
async def divorce(interaction: discord.Interaction):
    try:
        await interaction.response.defer()

        guildID = interaction.guild.id
        senderID = str(interaction.user.id)

        ## get sender data
        senderData = await lookup_database(senderID, guildID)
        if senderData == False:
            await new_database(senderID, guildID)
            senderData = await lookup_database(senderID, guildID)

        senderThing = senderData["users"].get(senderID, {})
        senderStatus = senderThing.get("Married")

        senderMarried = 0 if senderStatus is None else int(senderStatus)

        ## check if married
        if senderMarried == 0:
            raise Exception("bro you're not married..")

        ## get partner
        partnerID = str(senderMarried)
        partner = interaction.guild.get_member(int(partnerID))

        if partner is None:
            try:
                partner = await interaction.guild.fetch_member(int(partnerID))
            except discord.NotFound:
                partner = None

        ## confirmation view
        view = DivorceView(interaction.user)

        confirm_embed = discord.Embed(
            title="💔 Divorce Confirmation",
            description=f"Are you sure you want to divorce with <@{partnerID}> ({partner.display_name if partner else 'User not in server'})?",
            color=0xe74c3c
        )

        confirm_message = await interaction.followup.send(embed=confirm_embed, view=view, wait=True)
        await view.wait()

        ## delete confirmation message
        try:
            await confirm_message.delete()
        except:
            pass

        ## handle result
        if view.confirmed is None:
            return await interaction.followup.send("Divorce timed out")

        if view.confirmed == False:
            return await interaction.followup.send("Divorce cancelled")

        ## update BOTH users
        await update_value(senderID, guildID, "Married", 0)
        await update_value(partnerID, guildID, "Married", 0)

        ## success message
        divorce_embed = discord.Embed(
            title="💔 Divorce Finalized..",
            description=f"{interaction.user.mention} is now divorced from <@{partnerID}>.",
            color=0x95a5a6
        )
        await interaction.followup.send(embed=divorce_embed)

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error), ephemeral=True)
        else:
            await interaction.response.send_message(str(Error), ephemeral=True)