from resources.mrcookie import instance as bot
import discord

@bot.command()
async def shop(ctx):
    try:
        await ctx.send("Welcome to the shop! Here you can spend your cookies on various items and perks. More items coming soon!")
        give_embed = discord.Embed(
            title = "Shop Coming Soon..",
            color = 0x2ecc71,
            )

        give_embed.add_field(name = "", value = "test", inline = False)
        give_embed.set_author(name = "", icon_url = ctx.author.display_avatar)
        give_embed.set_footer(text = "test")
        await ctx.send(embed=give_embed)

    except Exception as Error:
        await ctx.send(Error)