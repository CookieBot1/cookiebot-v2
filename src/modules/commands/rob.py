import random
from datetime import datetime

import discord

from modules.commands.robbing.messages import success_list
from resources.checks import is_blacklisted, lookup_database, new_database, update_database, validate_user
from resources.mrcookie import instance as bot


@bot.command(aliases=["steal"])
async def rob(ctx, userID="0"):
    try:
        guildID = ctx.guild.id
        senderID = ctx.author.id
        guild = ctx.bot.get_guild(guildID)
        sender = guild.get_member(int(senderID)) or await guild.fetch_member(int(senderID))

        ## this block fetches user data from the database
        guildData = await lookup_database(senderID, guildID)
        if guildData == False:
            await new_database(senderID, guildID)
            guildData = await lookup_database(senderID, guildID)

        strSenderID = str(senderID)
        senderCookies = guildData["users"].get(strSenderID, {}).get("Cookies", 0)
        senderRobExpire = guildData["users"].get(strSenderID, {}).get("RobExpire")

        ## sender checks
        if senderCookies < 15:
            raise Exception("Whoops, you need at least 15 cookies to rob someone!")
        if senderRobExpire > datetime.now():
            raise ValueError()

        ## validate the pinged user, if any
        if userID != "0":
            userID = await validate_user(userID, guild)
            if userID == None or guild.get_member(int(userID)) is None or userID == ctx.author.id:
                raise Exception("Invalid user, try again!")
            if await is_blacklisted(userID):
                raise Exception("Unable to rob, that user is blacklisted.")
        else:
            database_users: dict = guildData["users"]
            database_users.pop(strSenderID)
            database_users = list(database_users.keys())
            userID = database_users[random.randrange(0, len(database_users))]

        ## pinged/random user checks
        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)

        userID = str(userID)
        userCookies = userData["users"][userID]["Cookies"]
        userRobProt = userData["users"][userID]["RobProtection"]
        userRobChances = userData["users"][userID]["RobChances"]

        ## user checks
        if userCookies < 15:
            raise Exception("Woah there! User needs at least 15 cookies to be robbed.")
        if userRobProt > datetime.now():
            raise Exception("User has an active rob shield, try again later!")

        randomNum = random.choice(range(0, 11))
        ## successful rob calculation
        if randomNum > userRobChances:
            successMessage = success_list[random.choice(range(0, len(success_list)))]

        # TODO: actually rob someone

    ## rob cooldown active message
    except ValueError as Error:
        timer = int(senderRobExpire.timestamp())
        timeout_embed = discord.Embed(
            description="You can rob someone again " + "<t:" + str(timer) + ":R>",
            color=0x992D22,
            timestamp=senderRobExpire,
        )

        timeout_embed.set_author(
            name="Easy there " + str(sender.display_name) + "!", icon_url=sender.display_avatar
        )
        await ctx.send(embed=timeout_embed)
    except Exception as Error:
        await ctx.send(f"{type(Error)}: {Error}")
