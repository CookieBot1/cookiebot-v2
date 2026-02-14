import asyncio

import discord
from discord.ext import commands
from resources.mrcookie import instance as bot
from resources.checks import is_admin, update_devalerts
from datetime import datetime, timezone, timedelta

@bot.command(alias = ["sendalerts"])
async def sendalert(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    def prompt(var):
        prompt_embed = discord.Embed(
            title = "🧱 Let's build your embed!",
            description = var,
            color = 0x9b59b6
            )
        
        prompt_embed.set_footer(text = "You can end this prompt at anytime by saying 'cancel'.")
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

        prompt_embed = prompt("Do you want your name to be as the **author** of the embed? Say ``yes`` or ``no``.\n If no, CookieBot will be written as the author.")
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
            color = 0x3498db,
            timestamp=datetime.now(timezone.utc)
            )
        
        if embed_author == -1:
            build_embed.set_footer(text = "Sent by " + bot.user.name + " Team.")
        if embed_author == 0:
            build_embed.set_footer(text = "Sent by " + ctx.author.name + ".")
        build_embed.set_thumbnail(url=bot.user.avatar.url)
        
        if embed_author == -1:
            build_embed.set_author(name= "Developer Alert", icon_url=bot.user.avatar.url)
        if embed_author == 0:
            build_embed.set_author(name= "Developer Alert", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=build_embed)

        response = await bot.wait_for("message", check=check, timeout=120.0) ## confirm again to send the message
        if response.content.lower() == "no":
            await ctx.send("Prompt cancelled. Please run the command to try again.")
            return
        if response.content.lower() != "yes":
            raise Exception("Invalid response, cancelling prompt.")

        await ctx.send("This embed will be sent to **all alert subscribers**, would you like to send this?\nPlease type ``yes`` or ``no``." )
        response = await bot.wait_for("message", check=check, timeout=60.0)
        if response.content.lower() == "no":
            await ctx.send("Prompt cancelled. Please run the command to try again.")
            return
        if response.content.lower() != "yes":
            raise Exception("Invalid response, cancelling prompt.")

        prompt_embed = prompt(
            "When should this message expire?\n\n"
            "Type a number followed by:\n"
            "`h` for hours\n"
            "`d` for days\n\n"
            "Example: `6h` or `3d`\n"
            "Type `none` if it should not expire."
        )
        await ctx.send(embed=prompt_embed)

        response = await bot.wait_for("message", check=check, timeout=120.0)

        if response.content.lower() == "cancel":
            raise Exception("Prompt cancelled.")

        expire_input = response.content.lower()

        now = datetime.now(timezone.utc)

        if expire_input == "none":
            expires_at = None
        else:
            try:
                value = int(expire_input[:-1])
                unit = expire_input[-1]

                if unit == "h":
                    expires_at = now + timedelta(hours=value)
                elif unit == "d":
                    expires_at = now + timedelta(days=value)
                else:
                    raise Exception("Invalid format. Use like 6h or 3d.")

            except ValueError:
                raise Exception("Invalid expiration format.")

        
        await ctx.send("Sending message to central database...")
        now_iso = datetime.now(timezone.utc).isoformat()
        
        await update_devalerts(now_iso, build_embed.to_dict(), expires_at)
        await ctx.send("Message sent to alert subscribers!")
    
        bot.latest_alert = {
            "date": now_iso,
            "expiresAt": expires_at.isoformat() if expires_at else None,
            "message": build_embed.to_dict()
        }


    except asyncio.TimeoutError:
        await ctx.send("Message timed out.")
    except Exception as Error:
        await ctx.send(Error)