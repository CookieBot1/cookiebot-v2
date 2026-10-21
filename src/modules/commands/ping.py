from resources.mrcookie import instance as bot
import discord

@bot.tree.command(name="ping", description="Check CookieBot's latency.")
async def ping(interaction: discord.Interaction):
    latency = round((interaction.client.latency) * 1000)
    await interaction.response.send_message("Pong! - " + str(latency) + "ms")