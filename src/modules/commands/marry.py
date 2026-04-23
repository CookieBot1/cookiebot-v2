from resources.mrcookie import instance as bot
import discord

from resources.checks import lookup_database, new_database, update_value, is_blacklisted

## ASK IF USER WANTS TO ACC GET MARRIED!!

@bot.command()
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