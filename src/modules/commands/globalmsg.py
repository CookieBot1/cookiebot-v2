import asyncio

import discord
from discord.ext import commands

from resources.checks import is_admin
from resources.mrcookie import instance as bot


@bot.command(aliases = ["globalmessage"])
async def globalmsg(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    def prompt(var):
        prompt_embed = discord.Embed(
            title = "🧱 Let's build your embed!",
            description = var,
            color = 0x9b59b6
            )
        
        prompt_embed.set_footer(text = "You can end this prompt at anytime by saying ``cancel``.")
        return (prompt_embed)

    try:
        if await is_admin(ctx.author.id) == False: raise Exception("You don't have permission to run this command.")

        prompt_embed = prompt("What should the **title** of the embed be?") ## embed builder prompt
        await ctx.send(embed=prompt_embed)
        response = await bot.wait_for("message", check=check, timeout=120.0)
        if response.content.lower() == "cancel":
            raise Exception("Prompt cancelled.")
        embed_title = response.content

        prompt_embed = prompt("What should the **description** of the embed be?")
        await ctx.send(embed=prompt_embed)
        response = await bot.wait_for("message", check=check, timeout=180.0)
        if response.content.lower() == "cancel":
            raise Exception("Prompt cancelled.")
        embed_desc = response.content

        prompt_embed = prompt("Do you want your name to be as the **author** of the embed? Say ``yes`` or ``no``.\n If no, MrCookie will be written as the author.")
        await ctx.send(embed=prompt_embed)
        response = await bot.wait_for("message", check=check, timeout=60.0)
        if response.content.lower() == "cancel":
            raise Exception("Prompt cancelled.")
        elif response.content.lower() == "no":
            embed_author = -1
        elif response.content.lower() == "yes":
            embed_author = 0
        else:
            raise Exception("Invalid response, cancelling prompt.")

        await ctx.send("Let's confirm your embed, does this look correct? Say ``yes`` or ``no``.")

        ## send the embed
        build_embed = discord.Embed(
            title = embed_title,
            description = embed_desc,
            color = 0x3498db
            )
        
        if embed_author == -1:
            build_embed.set_footer(text = "✏️ Message written by " + bot.user.name + " Team.")
        if embed_author == 0:
            build_embed.set_footer(text = "✏️ Message written by " + ctx.author.name + ".")
        build_embed.set_thumbnail(url=bot.user.avatar.url)
        
        if embed_author == -1:
            build_embed.set_author(name= "GLOBAL ANNOUNCEMENT", icon_url=bot.user.avatar.url)
        if embed_author == 0:
            build_embed.set_author(name= "GLOBAL ANNOUNCEMENT", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=build_embed)

        response = await bot.wait_for("message", check=check, timeout=120.0) ## confirm again to send the message
        if response.content.lower() == "no":
            await ctx.send("Prompt cancelled. Please run the command to try again.")
            return
        if response.content.lower() != "yes":
            raise Exception("Invalid response, cancelling prompt.")

        await ctx.send("This embed will be sent to **all servers**, would you like to send this?\nPlease type ``yes`` or ``no``." )
        response = await bot.wait_for("message", check=check, timeout=60.0)
        if response.content.lower() == "no":
            await ctx.send("Prompt cancelled. Please run the command to try again.")
            return
        if response.content.lower() != "yes":
            raise Exception("Invalid response, cancelling prompt.")
        
        await ctx.send("Message sending to all servers..")


        data = await bot.db.get_guilds() # get the servers from database
        total_servers = 0

        for guild in data: # add up all the servers
            guildID = guild["_id"]

            try:
                guild = bot.get_guild(guildID) or await bot.fetch_guild(guildID)
            except discord.HTTPException:
                continue

            channels = await guild.fetch_channels()
            for channel in channels: ## loop through channels looking for only text_channels
                if isinstance(channel, discord.TextChannel):
                    await channel.send(embed=build_embed)
                    total_servers += 1
                    break
        await ctx.send("Message has been sent to **" + str(total_servers) + " servers**.")

    except asyncio.TimeoutError:
        await ctx.send("Message timed out.")
    except Exception as Error:
        await ctx.send(Error)
