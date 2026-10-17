import discord
from discord import app_commands
from resources.mrcookie import instance as bot

from resources.checks import lookup_database, new_database, update_value


COLORS = {
    "red": "0xFF0000",
    "green": "0x00FF00",
    "blue": "0x0000FF",
    "yellow": "0xFFFF00",
    "purple": "0x800080",
    "orange": "0xFFA500",
    "pink": "0xFFC0CB",
    "black": "0x000000",
    "white": "0xFFFFFF",
    "cyan": "0x00FFFF",
}

PROFILE_OPTIONS = {
    "cookies": "Cookies",
    "streaks": "Streaks",
    "count": "Counting",
    "rob": "Robbery",
    # "inventory": "Inventory",
}

SHOWN_LIST = ["Cookies", "Streaks", "Counting", "Robbery"]  # keep in sync with allowed


class OwnerView(discord.ui.View):
    def __init__(self, userID, guildID, timeout=180):
        super().__init__(timeout=timeout)
        self.userID = str(userID)
        self.guildID = str(guildID)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.userID:
            await interaction.response.send_message("This customization menu isn't yours!", ephemeral=True)
            return False
        return True


class BioModal(discord.ui.Modal, title="Edit your profile bio"):
    bio = discord.ui.TextInput(
        label="New bio (max 200 characters)",
        style=discord.TextStyle.paragraph,
        max_length=200,
        required=True,
        placeholder="Enter your new bio...",
    )

    def __init__(self, userID, guildID):
        super().__init__(timeout=120)
        self.userID = str(userID)
        self.guildID = str(guildID)

    async def on_submit(self, interaction: discord.Interaction):
        bio = str(self.bio.value).strip()
        if bio.lower() in {"cancel", "exit"}:
            return await interaction.response.send_message("❌ Bio update cancelled. No changes made.", ephemeral=True)
        if len(bio) > 200:
            return await interaction.response.send_message("Bio is too long! Please keep it under 200 characters.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        await update_value(self.userID, self.guildID, "Bio", bio)
        await interaction.followup.send("✅ Your bio has been updated successfully!", ephemeral=True)


class ColorSelect(discord.ui.Select):
    def __init__(self, userID, guildID):
        self.userID = str(userID)
        self.guildID = str(guildID)
        super().__init__(
            placeholder="Choose your profile color",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=c.title(), value=c) for c in COLORS],
        )

    async def callback(self, interaction: discord.Interaction):
        chosen_color = self.values[0]
        await interaction.response.defer(ephemeral=True)
        await update_value(self.userID, self.guildID, "ProfileColor", int(COLORS[chosen_color], 16))
        await interaction.followup.send(
            f"✅ Your profile color has been updated to **{chosen_color.title()}**!", ephemeral=True
        )


class ColorView(OwnerView):
    def __init__(self, userID, guildID):
        super().__init__(userID, guildID)
        self.add_item(ColorSelect(userID, guildID))


class StatsSelect(discord.ui.Select):
    def __init__(self, userID, guildID):
        self.userID = str(userID)
        self.guildID = str(guildID)
        super().__init__(
            placeholder="Choose stats to display (none = hide all)",
            min_values=0,
            max_values=4,
            options=[discord.SelectOption(label=k, value=k) for k in SHOWN_LIST],
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        userData = await lookup_database(self.userID, self.guildID)
        if userData is False:
            await new_database(self.userID, self.guildID)
            userData = await lookup_database(self.userID, self.guildID)

        # Load current options so we don't wipe fields you didn't include (like Inventory)
        current = userData["users"][self.userID].get("ProfileOptions", {})
        updated = dict(current)  # copy
        for k in SHOWN_LIST:
            updated[k] = (k in self.values)

        await update_value(self.userID, self.guildID, "ProfileOptions", updated)
        await interaction.followup.send("✅ Your profile display options have been updated!", ephemeral=True)


class StatsView(OwnerView):
    def __init__(self, userID, guildID):
        super().__init__(userID, guildID)
        self.add_item(StatsSelect(userID, guildID))


class ProfileView(OwnerView):
    @discord.ui.button(label="Edit Bio", emoji="✏️", style=discord.ButtonStyle.secondary)
    async def edit_bio(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BioModal(self.userID, self.guildID))

    @discord.ui.button(label="Profile Color", emoji="🎨", style=discord.ButtonStyle.secondary)
    async def edit_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "**Choose a color:** " + ", ".join(c.title() for c in COLORS),
            view=ColorView(self.userID, self.guildID), ephemeral=True
        )

    @discord.ui.button(label="Displayed Stats", emoji="📊", style=discord.ButtonStyle.secondary)
    async def edit_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Choose which stats to show. Select none to hide all four. (Inventory stays unchanged.)",
            view=StatsView(self.userID, self.guildID), ephemeral=True
        )

    @discord.ui.button(label="Done", emoji="✅", style=discord.ButtonStyle.success)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        self.stop()
        await interaction.response.edit_message(content="🎉 Profile customization complete!", view=self)


@app_commands.guild_only()
@bot.tree.command(name="customize", description="Customize your CookieBot profile and settings.")
@app_commands.describe(category="General information or profile customization", section="Optional profile section to edit directly")
@app_commands.choices(
    category=[
        app_commands.Choice(name="General", value="general"),
        app_commands.Choice(name="Profile", value="profile"),
    ],
    section=[
        app_commands.Choice(name="Bio", value="bio"),
        app_commands.Choice(name="Color", value="color"),
        app_commands.Choice(name="Stats", value="stats"),
    ],
)
async def customize(interaction: discord.Interaction, category: str = "general", section: str | None = None):
    ## options include: general, profile
    try:
        if category not in ["general", "profile"]:
            return await interaction.response.send_message(
                "Invalid customize type! Please use: `general`, `profile`.", ephemeral=True
            )

        ## if no option is specified, show general customize options
        if category == "general":
            # send the general customize embed
            general_embed = discord.Embed(
                description="Here's a list of all the user customization options!",
                color=0x9b59b6,
            )

            # title and profile icon
            general_embed.set_author(name="Customize Page", icon_url=interaction.user.display_avatar.url)

            general_embed.add_field(name="👤 Profile", value="Edit your profile page by using the following command:" + "\n" + "`/customize category:Profile` (optional section: Bio, Color, Stats)", inline=False)
            general_embed.add_field(name="🔔 Alerts", value="Edit your alert settings by using the following command:" + "\n" + "`/alerts`", inline=False)

            general_embed.set_footer(text="More options coming soon!")
            return await interaction.response.send_message(embed=general_embed)

        ## profile flow
        userID = str(interaction.user.id)
        guildID = str(interaction.guild.id)

        userData = await lookup_database(userID, guildID)
        if userData is False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)

        ## ---- PROFILE CUSTOMIZATION CMD ----
        if category == "profile":
            # Jump routing:
            if section == "bio":
                return await interaction.response.send_modal(BioModal(userID, guildID))
            elif section == "color":
                return await interaction.response.send_message(
                    "**Choose a color:** " + ", ".join(c.title() for c in COLORS),
                    view=ColorView(userID, guildID), ephemeral=True
                )
            elif section == "stats":
                return await interaction.response.send_message(
                    "Choose which stats to show. Select none to hide all four. (Inventory stays unchanged.)",
                    view=StatsView(userID, guildID), ephemeral=True
                )

            # Wizard flow — edit any or all sections using interaction components
            await interaction.response.send_message(
                "✏️ **Profile customization**\nChoose what you'd like to edit, then press Done when finished.",
                view=ProfileView(userID, guildID), ephemeral=True
            )

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error), ephemeral=True)
        else:
            await interaction.response.send_message(str(Error), ephemeral=True)