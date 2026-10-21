import discord
from discord import app_commands
from resources.mrcookie import instance as bot

from resources.checks import lookup_database, new_database, update_value, is_blacklisted, validate_user, is_admin

@bot.tree.command(name="generate", description="Generate or remove cookies from a user's balance.")
@app_commands.default_permissions(administrator=True)
@app_commands.guild_only()
@app_commands.describe(user_id="The Discord ID of the user.", amount="The amount of cookies to generate or remove.")
@app_commands.checks.cooldown(1, 5.0)
async def generate(interaction: discord.Interaction, user_id: str, amount: str):
    try:
        await interaction.response.defer()

        ## this will only be for premium or whitelisted servers, for now it's locked to bot admins
        ##if ctx.author.guild_permissions.manage_guild == False:
        if await is_admin(interaction.user.id) == False:
            raise Exception("You don't have permission to use this command.")

        guildID = interaction.guild.id
        guild = interaction.guild
        userID = await validate_user(user_id)
        if userID is None:
            raise Exception("Invalid user, try again!")

        userID = int(userID)
        userKey = str(userID)

        try:
            user = await guild.fetch_member(userID)
        except discord.NotFound:
            raise Exception("Invalid user, try again!")
        if await is_blacklisted(userID): raise Exception("Illegal activity! You can't generate for a blacklisted user!")
        if amount == "0": raise Exception("Invalid amount, try again!")

        amount = int(amount)

        ## this block fetches user data from the database
        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userCookies = userData["users"][userKey]["Cookies"]

        ## bot admins bypass the checks
        '''if await is_admin(interaction.user.id) == False:
            if userCookies + amount < 0:
                raise Exception("You can't put the user in a negative balance!")
            if amount > 300 or amount < -300:
                raise Exception("You can't generate more/less than 300 cookies at a time.")
            else:
                userCookies += amount
        else:'''
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
        await interaction.followup.send(embed=give_embed)

        ## update the database
        await update_value(userKey, guildID, "Cookies", userCookies)

    except ValueError:
        await interaction.followup.send("Invalid amount, try again!", ephemeral=True)
    except Exception as Error:
        await interaction.followup.send(f"`{type(Error).__name__}`: {Error}", ephemeral=True)


@generate.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        # send the cooldown embed
        timer = f"{error.retry_after:.0f}"
        cooldown_embed = discord.Embed(
            description="You're on cooldown, please try again in ``" + timer + " seconds``.", color=0x992D22
        )

        if interaction.response.is_done():
            await interaction.followup.send(embed=cooldown_embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=cooldown_embed, ephemeral=True)