from resources.mrcookie import instance as bot
import discord
from discord.ext import commands

from resources.checks import lookup_database, new_database, update_value, is_blacklisted


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


@bot.command(aliases=['propose'])
@commands.cooldown(1, 60, commands.BucketType.user)
async def marry(ctx, user: discord.Member):
    try:
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)

        userID = str(user.id)
        senderID = str(ctx.author.id)

        sender = guild.get_member(int(senderID)) or await guild.fetch_member(int(senderID))

        ## validation
        if user.id == ctx.author.id:
            raise Exception("Invalid user, you can't marry yourself!")

        if guild.get_member(int(userID)) is None:
            raise Exception("Invalid user, try again!")

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

        proposal_message = await ctx.send(embed=proposal_embed, view=view)

        await view.wait()

        try:
            await proposal_message.delete()
        except:
            pass

        if view.accepted is None:
            return await ctx.send("⏰ Marriage proposal timed out!")

        if view.accepted == False:
            return await ctx.send("💔 Marriage proposal declined.")

        ## marry them
        userMarried = senderID
        senderMarried = userID

        ## embed
        marry_embed = discord.Embed(
            title="💍 Marrying " + user.display_name + "..",
            description=f"{sender.mention} and {user.mention} are now **MARRIED**!",
            color=0x00ff00
        )
        await ctx.send(embed=marry_embed)

        ## update db
        await update_value(userID, guildID, "Married", userMarried)
        await update_value(senderID, guildID, "Married", senderMarried)

    except Exception as Error:
        await ctx.send(str(Error))


@marry.error
async def marry_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Slow down! Try again in **{round(error.retry_after)} seconds**.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")