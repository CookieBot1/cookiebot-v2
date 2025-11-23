from resources.mrcookie import instance as bot
import discord

from resources.checks import lookup_database, new_database, update_value, is_blacklisted, validate_user

@bot.command(aliases = ["transfer", "send"])
async def give(ctx, userID = '0', amount = "0"):
    try:
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)
        userID = await validate_user(userID)

        if userID == None or userID == str(ctx.author.id) or guild.get_member(int(userID)) is None: raise Exception("Invalid user, try again!")
        if await is_blacklisted(userID): raise Exception("Illegal activity! You can't give to a blacklisted user!")
        if amount.isdigit() == False or int(amount) <= 0: raise Exception("Invalid amount, try again!")
        
        amount = int(amount)
        user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))
        senderID = str(ctx.author.id)
        sender = guild.get_member(int(senderID)) or await guild.fetch_member(int(senderID))

        ## fetching userData
        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userCookies = userData["users"][senderID]["Cookies"]

        ## fetching senderData
        senderData = await lookup_database(senderID, guildID) 
        if senderData == False:
            await new_database(senderID, guildID)
            senderData = await lookup_database(senderID, guildID)
        senderCookies = senderData["users"][senderID]["Cookies"]

        ## check if sender has enough cookies
        if userCookies < amount: raise Exception("Ahem- you don't have that many cookies..")
        
        ## transfer the cookies
        userCookies += amount
        senderCookies -= amount

        ## send the embed
        give_embed = discord.Embed(
            title = "💨 " + str(amount) + " Cookies Transferring..",
            color = 0x2ecc71,
            )

        give_embed.add_field(name = "", value = "🍪 " + user.display_name + " now has **" + str(userCookies) + " cookies!**", inline = False)
        give_embed.set_author(name = "", icon_url = sender.display_avatar)
        give_embed.set_footer(text = "Cookies delivered by Sam")
        await ctx.send(embed=give_embed)

        ## update the database
        await update_value(userID, guildID, "Cookies", userCookies)
        await update_value(senderID, guildID, "Cookies", senderCookies)

    except Exception as Error:
        await ctx.send(Error)