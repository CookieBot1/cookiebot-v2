from resources.mrcookie import instance as bot
import discord
from discord import app_commands

from resources.checks import lookup_database, new_database, is_blacklisted
from typing import Optional
from attrs import define, field


@define()
class SimpleUser:
    uid: str
    cookies: int
    position: Optional[int] = field(default=0, kw_only=True)

    async def lb_output(self) -> str:
        user = bot.get_user(int(self.uid)) or await bot.fetch_user(int(self.uid))
        if user.global_name == None: lb_user = user.name
        else: lb_user = user.global_name

        return (
        f"**#{self.position}. {lb_user}**"
        f"\n{self.cookies} Cookie{'s' if self.cookies != 1 else ''}"
        )

@bot.tree.command(name="balance", description="Check your cookie balance or another user's balance.")
@app_commands.describe(user="The user whose cookie balance you want to view.")
@app_commands.guild_only()
async def balance(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    try:
        ## set vars
        guildID = interaction.guild.id
        guild = interaction.guild

        ## if another user was mentioned, check if they're legit, else use sender ID
        if user is not None:
            userID = user.id

            if await is_blacklisted(userID): raise Exception("Can't show stats, user is blacklisted.")
        else:
            userID = interaction.user.id

        ## set vars
        user = interaction.user if int(userID) == interaction.user.id else user

        await interaction.response.defer()

        ## this block fetches their data from the database
        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userID = str(userID)

        ## THIS IS TEMPORARY SINCE OLD DB MIGHT HAVE NO Bio/ProfileColor, REMOVE LATER!!!!!!
        userThing = userData["users"].get(userID, {})

        marriedStatus = userThing.get("Married")
        userProfileColor = userThing.get("ProfileColor")
        userProfileBio = userThing.get("Bio")

        userMarried = 0 if marriedStatus is None else int(marriedStatus)
        userProfileColor = 0x7289da if userProfileColor is None else int(userProfileColor)
        userProfileBio = "This user has no bio set." if userProfileBio is None else str(userProfileBio)
        ## ------------------------------------------------------------
        userCookies = userData["users"][userID]["Cookies"]

        ## check if married
        if userMarried != 0:
            married_user = bot.get_user(userMarried) or await bot.fetch_user(userMarried)
            embed_title = f"💍 {user.display_name} & {married_user.display_name}'s Cookie Balance"
            marriedCookies = userData["users"][str(userMarried)]["Cookies"]
            userCookies = userCookies + marriedCookies
        else:
            embed_title = f"{user.display_name}'s Cookie Balance"

        guild_users: dict = userData.get("users", {})

        rank_list = []
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

                rank_id = f"{uid}+{married_id}"
            else:
                rank_id = uid

            already_counted.add(uid)
            rank_list.append({
                "rank_id": rank_id,
                "cookies": cookies
            })

        rank_list.sort(key=lambda x: x["cookies"], reverse=True)
        this_user = None
        for n, entry in enumerate(rank_list):
            entry["position"] = n + 1
            if str(userID) in entry["rank_id"].split("+"):
                this_user = entry


        ## send the embed
        bal_embed = discord.Embed(
            title = embed_title,
            color = userProfileColor,
            )

        bal_embed.add_field(name = "Cookies", value = userCookies, inline = True)

        rank_value = this_user["position"] if this_user else "Unranked"
        bal_embed.add_field(name = "Rank", value = rank_value, inline = True)
        bal_embed.set_thumbnail(url = user.display_avatar.url)
        await interaction.followup.send(embed=bal_embed)

    except Exception as Error:
        if interaction.response.is_done():
            await interaction.followup.send(str(Error))
        else:
            await interaction.response.send_message(str(Error))
