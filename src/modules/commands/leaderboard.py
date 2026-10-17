import asyncio
import math
from datetime import datetime, timezone
from typing import Optional

import discord
from discord import app_commands
from attrs import define, field

from resources.constants import UNICODE_LEFT, UNICODE_RIGHT
from resources.mrcookie import instance as bot

import traceback

MAX_USERS_PER_PAGE = 10


username_cache = {}
username_locks = {}
username_fetch_limit = asyncio.Semaphore(3)

async def get_cached_username(uid: str) -> str:
    uid = str(uid)

    if uid in username_cache:
        return username_cache[uid]

    if uid not in username_locks:
        username_locks[uid] = asyncio.Lock()

    async with username_locks[uid]:
        if uid in username_cache:
            return username_cache[uid]

        # check MongoDB cache first
        cached = await bot.db.get_cached_username(uid)

        if cached:
            username = cached.get("username")

            if username:
                username_cache[uid] = username
                return username

        # check Discord's existing cache without making an API request
        user = bot.get_user(int(uid))

        if user:
            username = user.global_name if user.global_name is not None else user.name

            username_cache[uid] = username
            await bot.db.save_cached_username(uid, username)

            return username

        # fallback to a Discord mention instead of fetching from the API
        return f"<@{uid}>"

@define()
class SimpleUser:
    uid: str
    cookies: int
    lbtype: str = field(default="cookies", kw_only=True)
    position: Optional[int] = field(default=0, kw_only=True)
    display_name: Optional[str] = field(default=None, kw_only=True)
    married_id: Optional[str] = field(default=None, kw_only=True)

    async def lb_output(self) -> str:
        if self.display_name:
            lb_user = self.display_name
        else:
            lb_user = await get_cached_username(self.uid)

            if self.married_id:
                married_name = await get_cached_username(self.married_id)
                lb_user = f"{lb_user} & {married_name}"

        label_map = {
            "cookies": "Cookie",
            "count": "Number",
            "countfails": "Fail",
        }
        label = label_map.get(self.lbtype, "Value")
        plural = "s" if self.cookies != 1 else ""
        return (
            f"**#{self.position}. {lb_user}**\n"
            f"{self.cookies} {label}{plural}"
        )


@app_commands.guild_only()
@bot.tree.command(name="leaderboard", description="View the server's cookie or counter leaderboard.")
@app_commands.describe(lbtype="Choose which leaderboard to view.")
@app_commands.choices(lbtype=[
    app_commands.Choice(name="Cookies", value="cookies"),
    app_commands.Choice(name="Count", value="count"),
    app_commands.Choice(name="Count Fails", value="countfails")
])
@app_commands.checks.cooldown(1, 20, key=lambda interaction: (interaction.guild_id, interaction.user.id))
async def leaderboard(interaction: discord.Interaction, lbtype: str = "cookies"):
    if interaction.guild is None:
        return await interaction.response.send_message("This command can only be run in a server!", ephemeral=True)

    await interaction.response.defer()

    guild_data = await bot.db.get_guild_users(interaction.guild.id)
    if guild_data is None:
        return await interaction.followup.send("No data for this guild was found!", ephemeral=True)

    guild_users: dict = guild_data.get("users", {})
    if not guild_users:
        return await interaction.followup.send("No users have cookies here!", ephemeral=True)

    # ----- Build new Embed -----
    embed = await build_embed(guild_users, str(interaction.user.id), lbtype=lbtype)
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    # ----- Add Buttons -----
    max_pages = await get_max_pages(guild_users, lbtype)
    view = discord.ui.View(timeout=None)

    left_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label=UNICODE_LEFT,
        disabled=True,
        custom_id=f"lb-button:{interaction.user.id}:{lbtype}:0:{max_pages}",
    )

    right_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label=UNICODE_RIGHT,
        disabled=True if max_pages == 1 else False,
        custom_id=f"lb-button:{interaction.user.id}:{lbtype}:1:{max_pages}",
    )

    my_rank_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label="My Rank",
        emoji="👤",
        custom_id=f"lb-rank:{interaction.user.id}:{lbtype}",
    )

    view.add_item(left_button)
    view.add_item(right_button)
    view.add_item(my_rank_button)

    await interaction.followup.send(embed=embed, view=view)


@leaderboard.error
async def leaderboard_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    # 1) cooldown error
    if isinstance(error, app_commands.CommandOnCooldown):
        timer = f"{error.retry_after:.0f}"
        cooldown_embed = discord.Embed(
            description=f"You're on cooldown, please try again in ``{timer} seconds``.",
            color=0x992D22
        )
        return await interaction.response.send_message(embed=cooldown_embed, ephemeral=True)

    # 2) parameter errors, doesn't cooldown
    if isinstance(error, (app_commands.TransformerError, app_commands.CommandSignatureMismatch)):
        return await interaction.response.send_message("Usage: `/leaderboard lbtype:<cookies|count|countfails>`", ephemeral=True)

    # 3) real errors that caused cooldowns
    original = getattr(error, "original", error)
    if interaction.response.is_done():
        await interaction.followup.send(f"Error: `{type(original).__name__}: {original}`", ephemeral=True)
    else:
        await interaction.response.send_message(f"Error: `{type(original).__name__}: {original}`", ephemeral=True)



# Ref: https://github.com/One-Nub/helper-bot/blob/main/src/modules/auto_response/autoresponder.py
@bot.add_button_handler("lb-button")
async def page_buttons(interaction: discord.Interaction, view: discord.ui.View | None):
    custom_id_data = interaction.data["custom_id"].split(":")  # type: ignore
    custom_id_data.pop(0)
    original_author_id = custom_id_data[0]
    lbtype = custom_id_data[1]
    new_page_index = int(custom_id_data[2])
    max_pages = int(custom_id_data[3])

    if not interaction.message or not interaction.guild:
        return

    # Disable after 5 mins.
    if (datetime.now(timezone.utc) - interaction.message.created_at).seconds > 300:
        if view:
            for x in view.children:
                # Ignored because this is how d.py says to do it.
                x.disabled = True  # pyright: ignore[reportAttributeAccessIssue]

        return await interaction.response.edit_message(
            content="-# This prompt was disabled because 5 minutes have passed since its creation.",
            view=view,
        )

    if str(interaction.user.id) != original_author_id:
        return await interaction.response.send_message(
            f"You're not allowed to flip through this embed!", ephemeral=True
        )

    await interaction.response.defer(thinking=False)

    # ----- Build new embed -----
    guild_data = await bot.db.get_guild_users(interaction.guild.id)
    if guild_data is None:
        return await interaction.followup.send("No data for this guild was found!", ephemeral=True)

    guild_users: dict = guild_data.get("users", {})
    if not guild_users:
        return await interaction.followup.send("No users have cookies here!", ephemeral=True)

    embed = await build_embed(guild_users, str(interaction.user.id), lbtype = lbtype, page_num=new_page_index)
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    # ----- Update buttons -----
    prev_page_index = 0 if new_page_index - 1 < 0 else new_page_index - 1
    next_page_index = max_pages if new_page_index + 1 >= max_pages else new_page_index + 1

    view = discord.ui.View()
    left_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label=UNICODE_LEFT,
        disabled=True if prev_page_index <= 0 and new_page_index != 1 else False,
        custom_id=f"lb-button:{interaction.user.id}:{lbtype}:{prev_page_index}:{max_pages}",
    )

    right_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label=UNICODE_RIGHT,
        disabled=True if next_page_index == max_pages else False,
        custom_id=f"lb-button:{interaction.user.id}:{lbtype}:{next_page_index}:{max_pages}",
    )

    my_rank_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label="My Rank",
        emoji="👤",
        custom_id=f"lb-rank:{interaction.user.id}:{lbtype}",
    )

    view.add_item(left_button)
    view.add_item(right_button)
    view.add_item(my_rank_button)

    await interaction.edit_original_response(embed=embed, view=view)


@bot.add_button_handler("lb-rank")
async def my_rank_buttons(interaction: discord.Interaction, view: discord.ui.View | None):
    custom_id_data = interaction.data["custom_id"].split(":")  # type: ignore
    original_author_id = custom_id_data[1]
    lbtype = custom_id_data[2]

    if not interaction.message or not interaction.guild:
        return

    # Disable after 5 mins.
    if (datetime.now(timezone.utc) - interaction.message.created_at).seconds > 300:
        if view:
            for x in view.children:
                x.disabled = True  # pyright: ignore[reportAttributeAccessIssue]

        return await interaction.response.edit_message(
            content="-# This prompt was disabled because 5 minutes have passed since its creation.",
            view=view,
        )

    if str(interaction.user.id) != original_author_id:
        return await interaction.response.send_message(
            "You're not allowed to flip through this embed!", ephemeral=True
        )

    await interaction.response.defer(thinking=False)

    guild_data = await bot.db.get_guild_users(interaction.guild.id)
    if guild_data is None:
        return await interaction.followup.send("No data for this guild was found!", ephemeral=True)

    guild_users: dict = guild_data.get("users", {})
    if not guild_users:
        return await interaction.followup.send("No users have cookies here!", ephemeral=True)

    position = await get_user_position(guild_users, original_author_id, lbtype)
    if position is None:
        return await interaction.followup.send("You don't have a ranking on this leaderboard!", ephemeral=True)
    if position > 100:
        return await interaction.followup.send(
            "You're outside the top 100! Check /balance for your rank.",
            ephemeral=True
        )

    new_page_index = (position - 1) // MAX_USERS_PER_PAGE
    max_pages = await get_max_pages(guild_users, lbtype)

    embed = await build_embed(guild_users, original_author_id, lbtype=lbtype, page_num=new_page_index)
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    prev_page_index = max(0, new_page_index - 1)
    next_page_index = min(max_pages, new_page_index + 1)

    view = discord.ui.View()

    left_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label=UNICODE_LEFT,
        disabled=new_page_index == 0,
        custom_id=f"lb-button:{interaction.user.id}:{lbtype}:{prev_page_index}:{max_pages}",
    )

    right_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label=UNICODE_RIGHT,
        disabled=new_page_index >= max_pages - 1,
        custom_id=f"lb-button:{interaction.user.id}:{lbtype}:{next_page_index}:{max_pages}",
    )

    my_rank_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label="My Rank",
        emoji="👤",
        custom_id=f"lb-rank:{interaction.user.id}:{lbtype}",
    )

    view.add_item(left_button)
    view.add_item(right_button)
    view.add_item(my_rank_button)

    await interaction.edit_original_response(embed=embed, view=view)


async def get_user_position(guild_users: dict, author_id: str, lbtype: str) -> Optional[int]:
    if lbtype == "cookies":
        simplified_users = []
        already_counted = set()

        for uid, data in guild_users.items():
            if uid in already_counted:
                continue

            cookies = data.get("Cookies", 0)
            married_id = data.get("Married")

            if married_id is not None and int(married_id) != 0:
                married_id = str(married_id)

                if married_id in guild_users:
                    cookies += guild_users[married_id].get("Cookies", 0)
                    already_counted.add(married_id)

            already_counted.add(uid)
            simplified_users.append((uid, cookies, married_id))

        simplified_users.sort(key=lambda x: x[1], reverse=True)

        for n, (uid, cookies, married_id) in enumerate(simplified_users):
            if uid == author_id or married_id == author_id:
                return n + 1

    elif lbtype in ("count", "countfails"):
        key = "Counter" if lbtype == "count" else "FailCounter"
        simplified_users = sorted(
            guild_users.items(),
            key=lambda x: x[1][key],
            reverse=True
        )

        for n, (uid, data) in enumerate(simplified_users):
            if uid == author_id:
                return n + 1

    return None


async def get_max_pages(guild_users: dict, lbtype: str) -> int:
    if lbtype == "cookies":
        already_counted = set()
        total = 0

        for uid, data in guild_users.items():
            if uid in already_counted:
                continue

            married_id = data.get("Married")
            if married_id is not None and int(married_id) != 0:
                married_id = str(married_id)
                if married_id in guild_users:
                    already_counted.add(married_id)

            already_counted.add(uid)
            total += 1

        return min(10, max(1, math.ceil(total / MAX_USERS_PER_PAGE)))

    return min(10, max(1, math.ceil(len(guild_users) / MAX_USERS_PER_PAGE)))


async def build_embed(guild_users: dict, author_id: str, lbtype: str, page_num: int = 0) -> discord.Embed:
    if lbtype == "cookies":
        simplified_users = []
        already_counted = set()

        for uid, data in guild_users.items():
            if uid in already_counted:
                continue

            cookies = data.get("Cookies", 0)
            married_id = data.get("Married")

            if married_id is not None and int(married_id) != 0:
                married_id = str(married_id)

                if married_id in guild_users:
                    cookies += guild_users[married_id].get("Cookies", 0)
                    already_counted.add(married_id)

                rank_id = uid
            else:
                rank_id = uid

            already_counted.add(uid)

            # build display name
            display_married_id = married_id if married_id is not None and int(married_id) != 0 and married_id in guild_users else None

            simplified_users.append(
                SimpleUser(uid, cookies, lbtype=lbtype, married_id=display_married_id)
            )

    elif lbtype == "count":
        simplified_users: list[SimpleUser] = [
            SimpleUser(uid, data["Counter"], lbtype=lbtype) for uid, data in guild_users.items()
        ]
    elif lbtype =="countfails":
        simplified_users: list[SimpleUser] = [
            SimpleUser(uid, data["FailCounter"], lbtype=lbtype) for uid, data in guild_users.items()
        ]

    simplified_users.sort(key=(lambda x: x.cookies), reverse=True)

    this_user = None
    for n, user in enumerate(simplified_users):
        user.position = n + 1
        if user.uid == str(author_id) or (lbtype == "cookies" and user.married_id == str(author_id)):
            this_user = user

    embed = await build_view_page(all_users=simplified_users, page_num=page_num)
    if this_user:
        embed.description = f"Your position: **#{this_user.position}**\n**{'━' * 13}**"

    return embed


async def build_view_page(all_users: list[SimpleUser], page_num: int = 0) -> discord.Embed:
    max_pages = min(10, math.ceil(len(all_users) / MAX_USERS_PER_PAGE))
    # Grab the 10 elements that we care about
    offset = page_num * MAX_USERS_PER_PAGE
    selected_items = all_users[offset : offset + MAX_USERS_PER_PAGE]

    # Build the embed.
    embed = discord.Embed(title="Leaderboard", color=0x7688D4)

    user_strs = await asyncio.gather(*(user.lb_output() for user in selected_items))

    embed.add_field(name=" ", value="\n\n".join(user_strs[:5]))
    if user_strs[5:]:
        embed.add_field(name=" ", value="\n\n".join(user_strs[5:]))

    # footer
    embed.set_footer(text=f"Page {page_num + 1}/{max_pages}")

    # return the entire embed
    return embed