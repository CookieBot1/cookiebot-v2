import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from resources.mrcookie import instance as bot
from resources.checks import is_admin, update_devalerts
from datetime import datetime, timezone, timedelta


class AlertModal(discord.ui.Modal, title="🧱 Let's build your embed!"):
    embed_title = discord.ui.TextInput(
        label="Embed Title",
        placeholder="What should the title of the embed be?",
        max_length=256
    )

    embed_desc = discord.ui.TextInput(
        label="Embed Description",
        placeholder="What should the description of the embed be?",
        style=discord.TextStyle.paragraph,
        max_length=4000
    )

    async def on_submit(self, interaction: discord.Interaction):
        view = AuthorView(self.embed_title.value, self.embed_desc.value)
        await interaction.response.send_message(
            "Do you want your name to be the **author** of the embed?\nIf no, CookieBot will be written as the author.",
            view=view,
            ephemeral=True
        )


class AuthorView(discord.ui.View):
    def __init__(self, embed_title, embed_desc):
        super().__init__(timeout=180)
        self.embed_title = embed_title
        self.embed_desc = embed_desc

    async def show_preview(self, interaction, embed_author):
        build_embed = discord.Embed(
            title=self.embed_title,
            description=self.embed_desc,
            color=0x3498db,
            timestamp=datetime.now(timezone.utc)
        )

        if embed_author == -1:
            build_embed.set_footer(text="Sent by " + bot.user.name + " Team.")
        if embed_author == 0:
            build_embed.set_footer(text="Sent by " + interaction.user.name + ".")

        if bot.user.display_avatar:
            build_embed.set_thumbnail(url=bot.user.display_avatar.url)

        if embed_author == -1:
            build_embed.set_author(name="Developer Alert", icon_url=bot.user.display_avatar.url)
        if embed_author == 0:
            build_embed.set_author(name="Developer Alert", icon_url=interaction.user.display_avatar.url)

        view = PreviewView(build_embed)

        await interaction.response.edit_message(
            content="Let's confirm your embed, does this look correct?",
            embed=build_embed,
            view=view
        )

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_preview(interaction, 0)

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_preview(interaction, -1)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Prompt cancelled.", view=None)


class PreviewView(discord.ui.View):
    def __init__(self, build_embed):
        super().__init__(timeout=180)
        self.build_embed = build_embed

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = SendView(self.build_embed)
        await interaction.response.edit_message(
            content="This embed will be sent to **all alert subscribers**, would you like to send this?",
            view=view
        )

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Prompt cancelled. Please run the command to try again.",
            embed=None,
            view=None
        )


class SendView(discord.ui.View):
    def __init__(self, build_embed):
        super().__init__(timeout=180)
        self.build_embed = build_embed

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ExpireModal(self.build_embed)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Prompt cancelled. Please run the command to try again.",
            embed=None,
            view=None
        )


class ExpireModal(discord.ui.Modal, title="Alert Expiration"):
    expire_input = discord.ui.TextInput(
        label="When should this message expire?",
        placeholder="6h, 3d, or none",
        max_length=20
    )

    def __init__(self, build_embed):
        super().__init__()
        self.build_embed = build_embed

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if await is_admin(interaction.user.id) == False:
                raise Exception("You don't have permission to run this command.")

            expire_input = self.expire_input.value.lower().strip()
            now = datetime.now(timezone.utc)

            if expire_input == "none":
                expires_at = None
            else:
                try:
                    value = int(expire_input[:-1])
                    unit = expire_input[-1]

                    if value <= 0:
                        raise Exception("Expiration must be greater than zero.")

                    if unit == "h":
                        expires_at = now + timedelta(hours=value)
                    elif unit == "d":
                        expires_at = now + timedelta(days=value)
                    else:
                        raise Exception("Invalid format. Use like 6h or 3d.")

                except ValueError:
                    raise Exception("Invalid expiration format.")

            await interaction.response.defer(ephemeral=True)

            now_iso = datetime.now(timezone.utc).isoformat()

            await update_devalerts(now_iso, self.build_embed.to_dict(), expires_at)

            bot.latest_alert = {
                "date": now_iso,
                "expiresAt": expires_at.isoformat() if expires_at else None,
                "message": self.build_embed.to_dict()
            }

            await interaction.followup.send("Message sent to alert subscribers!", ephemeral=True)

        except Exception as Error:
            if interaction.response.is_done():
                await interaction.followup.send(str(Error), ephemeral=True)
            else:
                await interaction.response.send_message(str(Error), ephemeral=True)


@bot.tree.command(name="sendalert", description="Send a developer alert to all subscribers.")
async def sendalert(interaction: discord.Interaction):
    try:
        if await is_admin(interaction.user.id) == False:
            raise Exception("You don't have permission to run this command.")

        modal = AlertModal()
        await interaction.response.send_modal(modal)

    except Exception as Error:
        await interaction.response.send_message(str(Error), ephemeral=True)