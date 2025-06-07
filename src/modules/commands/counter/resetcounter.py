from resources.mrcookie import instance as bot
from resources.checks import update_counter
import discord

@bot.command()
async def resetcounter(ctx):
    guildID = ctx.guild.id
    await update_counter(guildID, "Channel", 0)
    await update_counter(guildID, "Counter", 0)
    await update_counter(guildID, "lastUser", 0)

    counter_embed = discord.Embed(
        title = "Counter Channel Reset.",
        description = "Want to set your counter channel? Run ```.setcounter``` in that channel.",
        color = 0x2ecc71,
        )

    counter_embed.set_footer(text = 'To find out how counting works, run ".help counter"')
    await ctx.send(embed=counter_embed)