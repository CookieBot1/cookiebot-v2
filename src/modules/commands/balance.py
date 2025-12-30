from resources.mrcookie import instance as bot
import discord

from resources.checks import lookup_database, new_database, validate_user, is_blacklisted
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

@bot.command(aliases = ["bal", "wallet"])
async def balance(ctx, userID = '0'):
    try:
        ## set vars
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)

        ## if another user was mentioned, check if they're legit, else use sender ID
        if userID != '0':
            userID = await validate_user(userID)
            if userID == None or guild.get_member(int(userID)) is None: raise Exception("Invalid user, try again!")
            if await is_blacklisted(userID): raise Exception("Can't show stats, user is blacklisted.")
        else:
            userID = ctx.author.id
        
        ## set vars
        user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))
        
        ## this block fetches their data from the database
        userData = await lookup_database(userID, guildID) 
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        
        userID = str(userID)
        userStreaks = userData["users"][userID]["Streaks"]
        userCookies = userData["users"][userID]["Cookies"]
        userDailyMultiplier = userData["users"][userID]["DailyMultiplier"]

        guild_users: dict = userData.get("users", {})
    
        simplified_users: list[SimpleUser] = [
            SimpleUser(uid, data["Cookies"]) for uid, data in guild_users.items()
        ]
        simplified_users.sort(key=(lambda x: x.cookies), reverse=True)

        this_user = None
        for n, su in enumerate(simplified_users):
            su.position = n + 1
            if su.uid == str(userID):
                this_user = su

        ## send the embed
        bal_embed = discord.Embed(
            title = str(user.global_name) + "'s Cookie Balance",
            color = 0x7289da,
            )
    
        bal_embed.add_field(name = "Cookies", value = userCookies, inline = True)

        rank_value = this_user.position if this_user else "Unranked"
        bal_embed.add_field(name = "Rank", value = rank_value, inline = True)
        if userDailyMultiplier != 0:
            bal_embed.add_field(name = "Daily Multiplier", value = str(userDailyMultiplier) + " Cookie Multiplier Active!", inline = False)

        bal_embed.set_thumbnail(url = user.display_avatar)
        await ctx.send(embed=bal_embed)
    
    except Exception as Error:
        await ctx.send(Error)