import math
from datetime import datetime, timezone
from typing import Optional

import discord
from attrs import define, field
from discord.ext import commands

from resources.constants import UNICODE_LEFT, UNICODE_RIGHT
from resources.mrcookie import instance as bot

import traceback

MAX_USERS_PER_PAGE = 10


@define()
class SimpleUser:
    uid: str
    cookies: int
    lbtype: str = field(default="cookies", kw_only=True)
    position: Optional[int] = field(default=0, kw_only=True)

    async def lb_output(self) -> str:
        user = bot.get_user(int(self.uid)) or await bot.fetch_user(int(self.uid))
        if user.global_name == None: lb_user = user.name
        else: lb_user = user.global_name

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


@bot.command(aliases=["lb"])
@commands.cooldown(1, 20, commands.BucketType.member)
async def leaderboard(ctx: commands.Context, lbtype: str = "cookies"):
    if ctx.guild is None:
        return await ctx.reply("This command can only be run in a server!", delete_after=7)

    lbtype = lbtype.lower()
    aliases = {
        "counter": "count",
        "countfail": "countfails",
        "fails": "countfails",
    }
    lbtype = aliases.get(lbtype, lbtype)
    if lbtype not in ["count", "cookies", "countfails"]:
        leaderboard.reset_cooldown(ctx)  # refund cooldown for typos
        return await ctx.reply(
            "Invalid leaderboard type! Please use: `cookies`, `count`, `countfails`.",
            delete_after=7
        )

    guild_data = await bot.db.get_guild_users(ctx.guild.id)
    if guild_data is None:
        return await ctx.reply("No data for this guild was found!", delete_after=7)

    guild_users: dict = guild_data.get("users", {})
    if not guild_users:
        return await ctx.reply("No users have cookies here!", delete_after=7)

    # ----- Build new Embed -----
    embed = await build_embed(guild_users, str(ctx.author.id), lbtype=lbtype)
    embed.set_thumbnail(url=ctx.guild.icon)

    # ----- Add Buttons -----
    max_pages = math.ceil(len(guild_users) / MAX_USERS_PER_PAGE)
    view = discord.ui.View(timeout=None)

    left_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label=UNICODE_LEFT,
        disabled=True,
        custom_id=f"lb-button:{ctx.author.id}:{lbtype}:0:{max_pages}",
    )

    right_button = discord.ui.Button(
        style=discord.ButtonStyle.secondary,
        label=UNICODE_RIGHT,
        disabled=True if max_pages == 1 else False,
        custom_id=f"lb-button:{ctx.author.id}:{lbtype}:1:{max_pages}",
    )

    view.add_item(left_button)
    view.add_item(right_button)

    await ctx.send(embed=embed, view=view)


@leaderboard.error
async def leaderboard_error(ctx: commands.Context, error: commands.CommandError):
    # 1) cooldown error
    if isinstance(error, commands.CommandOnCooldown):
        timer = f"{error.retry_after:.0f}"
        cooldown_embed = discord.Embed(
            description=f"You're on cooldown, please try again in ``{timer} seconds``.",
            color=0x992D22
        )
        return await ctx.send(embed=cooldown_embed)

    # 2) parameter errors, doesn't cooldown
    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        return await ctx.send("Usage: `.lb <cookies|count|countfails>`")

    # 3) real errors that caused cooldowns
    leaderboard.reset_cooldown(ctx)

    original = getattr(error, "original", error)
    await ctx.send(f"Error: `{type(original).__name__}: {original}`")



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

    # ----- Build new embed -----
    guild_data = await bot.db.get_guild_users(interaction.guild.id)
    if guild_data is None:
        return await interaction.response.send_message("No data for this guild was found!", ephemeral=True)

    guild_users: dict = guild_data.get("users", {})
    if not guild_users:
        return await interaction.response.send_message("No users have cookies here!", ephemeral=True)

    embed = await build_embed(guild_users, str(interaction.user.id), lbtype = lbtype, page_num=new_page_index)
    embed.set_thumbnail(url=interaction.guild.icon)

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

    view.add_item(left_button)
    view.add_item(right_button)

    await interaction.response.edit_message(embed=embed, view=view)


async def build_embed(guild_users: dict, author_id: str, lbtype: str, page_num: int = 0) -> discord.Embed:
    if lbtype == "cookies":
        simplified_users: list[SimpleUser] = [
            SimpleUser(uid, data["Cookies"], lbtype=lbtype) for uid, data in guild_users.items()
        ]
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
        if user.uid == str(author_id):
            this_user = user

    embed = await build_view_page(all_users=simplified_users, page_num=page_num)
    if this_user:
        embed.description = f"Your position: **#{this_user.position}**\n**{'━' * 13}**"

    return embed


async def build_view_page(all_users: list[SimpleUser], page_num: int = 0) -> discord.Embed:
    max_pages = math.ceil(len(all_users) / MAX_USERS_PER_PAGE)
    # Grab the 10 elements that we care about
    offset = page_num * MAX_USERS_PER_PAGE
    selected_items = all_users[offset : offset + MAX_USERS_PER_PAGE]

    # Build the embed.
    embed = discord.Embed(title="Leaderboard", color=0x7688D4)

    user_strs = [await user.lb_output() for user in selected_items]

    embed.add_field(name=" ", value="\n\n".join(user_strs[:5]))
    if user_strs[5:]:
        embed.add_field(name=" ", value="\n\n".join(user_strs[5:]))

    # footer
    embed.set_footer(text=f"Page {page_num + 1}/{max_pages}")

    # return the entire embed
    return embed
