import discord
from resources.mrcookie import instance as bot
from discord.ext import commands

from resources.checks import lookup_database, new_database, update_value, is_blacklisted, validate_user, is_admin

@bot.command(aliases = ["gen"])
@commands.cooldown(1, 30)
async def generate(ctx, userID = '0', amount = "0"):
    try:
        if ctx.author.guild_permissions.manage_guild == False: 
            if await is_admin(ctx.author.id) == False: 
                raise Exception("You don't have permission to use this command.")

        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)
        userID = await validate_user(userID, guild)

        if userID == None or guild.get_member(int(userID)) is None: raise Exception("Invalid user, try again!")
        if await is_blacklisted(userID): raise Exception("Illegal activity! You can't generate for a blacklisted user!")
        if amount == "0": raise Exception("Invalid amount, try again!")
        
        amount = int(amount)
        user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))

        ## this block fetches user data from the database
        userData = await lookup_database(userID, guildID) 
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userCookies = userData["users"][userID]["Cookies"] 

        ## bot admins bypass the checks
        if await is_admin(ctx.author.id) == False:
            if userCookies + amount < 0:
                raise Exception("You can't put the user in a negative balance!")
            if amount > 300 or amount < -300:
                raise Exception("You can't generate more/less than 300 cookies at a time.")
            else:
                userCookies += amount

        ## send the embed
        give_embed = discord.Embed(
            title = "🪄 Generating Cookies..",
            color = 0x9b59b6,
            )

        if amount > 0:
            give_embed.add_field(name = "", value = "Added **" + str(amount) + " cookies** to " + user.display_name + "'s balance!", inline = False)
        if amount < 0:
            give_embed.add_field(name = "", value = "Removed **" + str(amount) + " cookies** from " + user.display_name + "'s balance!", inline = False)

        give_embed.set_footer(text = user.display_name + " now has " + str(userCookies) + " cookies.")
        await ctx.send(embed=give_embed)

        ## update the database
        await update_value(userID, guildID, "Cookies", userCookies)

    except ValueError:
        await ctx.send("Invalid amount, try again!")
    except Exception as Error:
        await ctx.send(Error)

@generate.error
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandOnCooldown):
        # send the cooldown embed
        timer = f"{error.retry_after:.0f}"
        cooldown_embed = discord.Embed(
            description="You're on cooldown, please try again in ``" + timer + " seconds``.", color=0x992D22
        )

        await ctx.send(embed=cooldown_embed)