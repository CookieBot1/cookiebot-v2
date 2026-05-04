import discord
from resources.mrcookie import instance as bot

@bot.command()
async def invite(ctx):
    invite_embed = discord.Embed(
        title = "Add CookieBot to your server",
        description = "Invite CookieBot by clicking [here!](https://discord.com/oauth2/authorize?client_id=1133155318117957643)",
        color = 0x9b59b6
        )
    invite_embed.set_author(name = ctx.bot.user.name, icon_url = ctx.bot.user.avatar)

    await ctx.send(embed=invite_embed)