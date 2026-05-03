from resources.mrcookie import instance as bot
from discord.ext import commands


def default_settings():
    return {
        "server": {
            "IgnoredChannels": [],
            "IgnoredChannelDrops": []
        },
        "counter": {
            "Channel": 0,
            "Counter": 0,
            "lastUser": 0,
            "highScore": 0,
            "AllowMath": True,
            "badCounterRoleEnabled": False,
            "badCounterRoleID": 0,
            "badCounterRoleDelete": False,
            "badCounterRoleFails": 0
        }
    }


@bot.command()
@commands.is_owner()
async def fixserversettings(ctx):
    await ctx.send("Fixing missing server settings...")

    guilds = await bot.db.get_guilds()
    fixed_count = 0

    for guild in guilds:
        guildID = str(guild["_id"])

        data = await bot.db.find_user({"_id": guildID}) or {}
        current_settings = data.get("settings", {})

        settings = default_settings()

        if "server" in current_settings:
            settings["server"].update(current_settings["server"])

        if "counter" in current_settings:
            settings["counter"].update(current_settings["counter"])

        await bot.db.update_one(
            {"_id": guildID},
            {"$set": {"settings": settings}}
        )

        fixed_count += 1

    await ctx.send(f"Done! Fixed settings for `{fixed_count}` servers.")