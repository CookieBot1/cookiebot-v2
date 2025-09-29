import random
from datetime import datetime, timedelta

import discord

from modules.commands.robbing.messages import success_list
from resources.checks import (
    is_blacklisted,
    lookup_database,
    new_database,
    update_many_values,
    update_value,
    validate_user,
)
from resources.constants import EMBED_GREEN, EMBED_RED
from resources.mrcookie import instance as bot


@bot.command(aliases=["steal"])
async def rob(ctx, userID="0"):
    try:
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)
        senderID = ctx.author.id
        sender = guild.get_member(int(senderID)) or await guild.fetch_member(int(senderID))

        ## this block fetches user data from the database
        guildData = await lookup_database(senderID, guildID)
        if guildData == False:
            await new_database(senderID, guildID)
            guildData = await lookup_database(senderID, guildID)

        strSenderID = str(senderID)
        senderCookies = guildData["users"].get(strSenderID, {}).get("Cookies", 0)
        senderRobExpire = guildData["users"].get(strSenderID, {}).get("RobExpire", datetime.now())

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

            if not database_users:
                raise Exception("There are no other users to rob! 😶")

            userID = database_users[random.randrange(0, len(database_users))]

        ## pinged/random user checks
        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)

        userID = str(userID)
        userCookies = userData["users"][userID]["Cookies"]
        userRobProt = userData["users"][userID]["RobProtection"]
        userRobChances = userData["users"][userID]["RobChances"]  # likelihood target user is to be robbed

        ## user checks
        if userCookies < 15:
            raise Exception("Woah there! User needs at least 15 cookies to be robbed.")
        if userRobProt > datetime.now():
            raise Exception("User has an active rob shield, try again later!")

        randomNum = round(random.uniform(0.0, 11.0), 2)  # random float from 0, up to 11, 2 decimal places.

        # setup embed variables
        embed_title = None
        embed_desc = None
        embed_color = None

        if randomNum > userRobChances:
            # success
            successMessage = success_list[random.choice(range(0, len(success_list)))]
            baseStolenCookies = random.randint(5, 15)

            # TODO: Apply higher amount of cookies stolen based on number of cookies the victim has

            embed_title = "🥷 Robbery Successful!"
            embed_desc = f"Mission Accomplished. You stole `{baseStolenCookies}` of their (<@{userID}>) cookies by {successMessage}!"
            embed_color = EMBED_GREEN

            # Make it more difficult to rob the user again + remove cookies
            await update_many_values(
                userID,
                guildID,
                Cookies=userCookies - baseStolenCookies,
                RobChances=urc if (urc := userRobChances + 0.2) < 11 else 11,
            )
            await update_value(senderID, guildID, "Cookies", senderCookies + baseStolenCookies)
        else:
            # fail
            embed_title = "🚓 Robbery Fumbled"
            embed_desc = r"SCRAM, IT'S THE COPS  - u failed \*womp womp\*"
            embed_color = EMBED_RED

            # Decrease rob chance back until we reach 7 again
            await update_many_values(
                userID, guildID, RobChances=urc if (urc := userRobChances - 0.2) > 7 else 7
            )

            # TODO: Remove cookies from the robber for fumbling their attempt (& give to victim?)

        cooldown = datetime.now() + timedelta(hours=4)
        await update_value(senderID, guildID, "RobExpire", cooldown)

        embed = discord.Embed(color=embed_color, description=embed_desc)
        embed.set_author(name=embed_title, icon_url=sender.display_avatar)
        embed.timestamp = cooldown
        embed.set_footer(text=f"Your crew will be ready again by")
        await ctx.send(embed=embed)

    ## rob cooldown active message
    except ValueError:
        timer = int(senderRobExpire.timestamp())
        timeout_embed = discord.Embed(
            description="You can rob someone again " + "<t:" + str(timer) + ":R>",
            color=EMBED_RED,
            timestamp=senderRobExpire,
        )

        timeout_embed.set_author(
            name="Easy there " + str(sender.display_name) + "!", icon_url=sender.display_avatar
        )
        await ctx.send(embed=timeout_embed)
    except Exception as error:
        await ctx.send(f"{type(error)}: {error}")
