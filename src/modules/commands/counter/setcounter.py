from resources.mrcookie import instance as bot
from resources.checks import update_counter, lookup_counter, new_counter
import discord

@bot.command()
async def setcounter(ctx):
    guildID = ctx.guild.id

    counterData = await lookup_counter(guildID)
    if counterData is False:
        await new_counter(guildID)
        counterData = await lookup_counter(guildID)

    # resets data to default incase they run .setcounter after already having an existing counting channel
    await update_counter(guildID, "Channel", ctx.channel.id)
    await update_counter(guildID, "Counter", 0)
    await update_counter(guildID, "lastUser", 0)

    counter_embed = discord.Embed(
        title = "✅ Counter Channel Set!",
        description = "Want to change your counter channel? Run ``.setcounter`` again in that channel.",
        color = 0x2ecc71,
        )

    counter_embed.set_footer(text = 'To find out how counting works, run ".help counter"')
    await ctx.send(embed=counter_embed)