import discord
from discord import app_commands
from resources.mrcookie import instance as bot

@bot.tree.command(name="invite", description="Invite CookieBot to your server.")
async def invite(interaction: discord.Interaction):
    invite_embed = discord.Embed(
        title = "Add CookieBot to your server",
        description = "Invite CookieBot by clicking [here!](https://discord.com/oauth2/authorize?client_id=1133155318117957643)",
        color = 0x9b59b6
        )
    invite_embed.set_author(name = interaction.client.user.name, icon_url = interaction.client.user.avatar)

    await interaction.response.send_message(embed=invite_embed)