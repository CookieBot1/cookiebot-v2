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


@bot.command(aliases=["steal", "mug"])
async def rob(ctx, userID="0"):
    try:
        guild_id = ctx.guild.id
        guild = ctx.bot.get_guild(guild_id)
        sender_id = ctx.author.id
        sender = guild.get_member(int(sender_id)) or await guild.fetch_member(int(sender_id))

        ## this block fetches user data from the database
        guild_data = await lookup_database(sender_id, guild_id)
        if guild_data == False:
            await new_database(sender_id, guild_id)
            guild_data = await lookup_database(sender_id, guild_id)

        sender_cookies = guild_data["users"].get(str(sender_id), {}).get("Cookies", 0)
        sender_rob_cooldown = guild_data["users"].get(str(sender_id), {}).get("RobExpire", datetime.now())

        ## sender checks
        if sender_cookies < 15:
            raise Exception("Whoops, you need at least 15 cookies to rob someone!")
        if sender_rob_cooldown > datetime.now():
            raise ValueError()

        ## validate the pinged user, if any. if empty user parameter, get random user from database
        if userID != "0":
            userID = await validate_user(userID)
            if userID == None or guild.get_member(int(userID)) is None or userID == ctx.author.id:
                raise Exception("Invalid user, try again!")
            if await is_blacklisted(userID):
                raise Exception("Unable to rob, that user is blacklisted.")
            
            ## checks for the user being robbed
            user_data = await lookup_database(userID, guild_id)
            if user_data == False:
                await new_database(userID, guild_id)
                user_data = await lookup_database(userID, guild_id)
            
        ## find a random user from database
        else:
            database_users: dict = guild_data["users"]
            database_users.pop(str(sender_id))
            database_users = list(database_users.keys())

            if not database_users:
                raise Exception("There are no other users to rob! 😶")
            
            ## assign a random user to be robbed if no user parameter is given
            counter = 0
            user_found = False
            while counter < len(database_users): 
                userID = database_users[random.randrange(0, len(database_users))]
                user_data = await lookup_database(userID, guild_id)

                if user_data["users"][userID]["Cookies"] >= 15:
                    user_found = True
                    break
                counter += 1
            
            if user_found == False:
                raise Exception("No other user has enough cookies! 😶")
        userID = str(userID)
        user_cookies = user_data["users"][userID]["Cookies"]
        user_rob_prot = user_data["users"][userID]["RobProtection"]
        user_rob_chances = user_data["users"][userID]["RobChances"]  # likelihood target user is to be robbed

        ## THIS IS TEMPORARY SINCE OLD DB MIGHT HAVE NO RobCount/RobGains, REMOVE LATER!!!!!!
        user = user_data["users"].get(userID, {})
        rob_count = user.get("RobCount")
        rob_gains = user.get("RobGains")

        if rob_count is None or rob_gains is None:
            user_rob_count = 0
            user_rob_gains = 0
        else:
            user_rob_count = rob_count
            user_rob_gains = rob_gains
        ## ------------------------------------------------------------

        ## user checks
        if user_cookies < 15:
            raise Exception(
                "Woah there! That user needs at least 15 cookies to be robbed. Leave the poor alone!"
            )
        if user_rob_prot > datetime.now():
            raise Exception("This user's currently at home watching their vault, try again later!")

        random_num = round(random.uniform(0.0, 11.0), 2)  # random float from 0, up to 11, 2 decimal places.

        # setup embed variables
        embed_title = None
        embed_desc = None
        embed_color = None

        ## update user rob stats
        user_rob_count += 1

        if random_num > user_rob_chances:
            # success
            success_msg = success_list[random.choice(range(0, len(success_list)))]
            stolen_cookies = random.randint(5, 10)  # Base of 5-10 cookies to steal

            match user_cookies:
                case user_cookies if user_cookies <= 100:
                    stolen_cookies += random.randint(1, 5)  # Additional 1-5 cookies
                case user_cookies if user_cookies <= 1500:
                    stolen_cookies += int(user_cookies * 0.0016)  # Additional 0.16%
                case user_cookies:
                    stolen_cookies += int(user_cookies * 0.008)  # Additional 0.8%

            embed_title = "🥷 Robbery Successful!"
            embed_desc = f"Mission Accomplished. You stole `{stolen_cookies}` of their (<@{userID}>) cookies by {success_msg}!"
            embed_color = EMBED_GREEN

            # Make it more difficult to rob the user again + remove cookies
            await update_many_values(
                userID,
                guild_id,
                Cookies=user_cookies - stolen_cookies,
                RobChances=urc if (urc := user_rob_chances + 0.2) < 11 else 11,
            )
            await update_value(sender_id, guild_id, "Cookies", sender_cookies + stolen_cookies)
            user_rob_gains += stolen_cookies
            await update_value(sender_id, guild_id, "RobGains", user_rob_gains)

        else:
            # fail
            embed_title = "🚓 Robbery Fumbled"
            embed_color = EMBED_RED

            lost_cookies = random.randint(5, 10)  # Base of 5-10 cookies to lose
            lost_cookies += int(sender_cookies * 0.008)  # Additional 0.8%
            await update_value(
                sender_id, guild_id, "Cookies", sender_cookies - lost_cookies
            )  # remove cookies from sender

            # TODO: Put in fun fail messages
            embed_desc = "SCRAM, IT'S THE COPS  - u failed. SO you lost "

            gift_chance = random.randint(1, 10)
            if gift_chance <= 2:
                user_cookies += lost_cookies
                embed_desc += f"`{lost_cookies}` cookies and YOUR TARGET BLACKMAILED YOU FOR THEM INSTEAD."
            else:
                embed_desc += (
                    f"`{lost_cookies}` cookies AND your cookies became stale, losing their value forever."
                )

            # Make it easier to rob user until we reach the base count again
            await update_many_values(
                userID,
                guild_id,
                RobChances=urc if (urc := user_rob_chances - 0.2) > 7 else 7,
                Cookies=user_cookies,
            )  # Update rob chance + update user cookies

        cooldown = datetime.now() + timedelta(hours=4)
        await update_value(sender_id, guild_id, "RobExpire", cooldown)
        await update_value(sender_id, guild_id, "RobCount", user_rob_count)

        embed = discord.Embed(color=embed_color, description=embed_desc)
        embed.set_author(name=embed_title, icon_url=sender.display_avatar)
        embed.timestamp = cooldown
        embed.set_footer(text=f"Your crew will be ready again by")
        await ctx.send(embed=embed)


    ## rob cooldown active message
    except ValueError:
        timer = int(sender_rob_cooldown.timestamp())
        timeout_embed = discord.Embed(
            description="You can rob someone again " + "<t:" + str(timer) + ":R>",
            color=EMBED_RED,
            timestamp=sender_rob_cooldown,
        )

        timeout_embed.set_author(
            name="Easy there " + str(sender.display_name) + "!", icon_url=sender.display_avatar
        )
        await ctx.send(embed=timeout_embed)
    except Exception as error:
        await ctx.send(error)