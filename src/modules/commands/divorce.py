from resources.mrcookie import instance as bot
import discord
from discord.ext import commands

from resources.checks import lookup_database, new_database, update_value, is_blacklisted

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


@bot.command(aliases=['separate', 'split'])
async def divorce(ctx):
    try:
        guildID = ctx.guild.id
        senderID = str(ctx.author.id)

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
        partner = ctx.guild.get_member(int(partnerID)) or await ctx.guild.fetch_member(int(partnerID))

        ## confirmation view
        view = DivorceView(ctx.author)

        confirm_embed = discord.Embed(
            title="💔 Divorce Confirmation",
            description=f"Are you sure you want to divorce with {partner.mention} ({partner.display_name})?",
            color=0xe74c3c
        )

        confirm_message = await ctx.send(embed=confirm_embed, view=view)
        await view.wait()

        ## delete confirmation message
        try:
            await confirm_message.delete()
        except:
            pass

        ## handle result
        if view.confirmed is None:
            return await ctx.send("Divorce timed out")

        if view.confirmed == False:
            return await ctx.send("Divorce cancelled")

        ## update BOTH users
        await update_value(senderID, guildID, "Married", 0)
        await update_value(partnerID, guildID, "Married", 0)

        ## success message
        divorce_embed = discord.Embed(
            title="💔 Divorce Finalized..",
            description=f"{ctx.author.mention} is now divorced from {partner.mention}.",
            color=0x95a5a6
        )
        await ctx.send(embed=divorce_embed)

    except Exception as Error:
        await ctx.send(str(Error))