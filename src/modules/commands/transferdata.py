from resources.mrcookie import instance as bot
from discord.ext import commands


def default_user_data():
    return {
        "Cookies": 0,
        "Streaks": 0,
        "DailyExpire": None,
        "DailyMultiplier": 0,
        "DailyMultExpire": None,
        "RobExpire": None,
        "RobChances": 7,
        "RobProtection": None,
        "RobCount": 0,
        "RobGains": 0,
        "Counter": 0,
        "CountSaves": 0,
        "FailCounter": 0,
        "Inventory": "Empty",
        "Bio": "No bio set. Run ``.customize profile`` to set one!",
        "ProfileOptions": {
            "Cookies": True,
            "Streaks": True,
            "Counting": True,
            "Robbery": True,
            "Inventory": False
        },
        "ProfileColor": 0x7289da,
        "DevAlerts": True,
        "AlertState": {
            "readId": None,
            "pingForId": None,
            "pingCount": 0
        },
        "Married": 0
    }


@bot.command()
@commands.is_owner()
async def transferdata(ctx):
    await ctx.send("Starting data transfer...")

    server_count = 0
    user_count = 0
    beta_bonus_count = 0

    old_servers = await bot.db.get_old_guilds()

    for old_server in old_servers:
        guildID = str(old_server["_id"])
        old_users = old_server.get("users", {})

        new_server = await bot.db.find_user({"_id": guildID}) or {}
        new_users = new_server.get("users", {})

        for userID, old_data in old_users.items():
            userID = str(userID)

            old_cookies = old_data.get("Cookies", 0)
            old_streaks = old_data.get("Streaks", 0)

            current_data = new_users.get(userID, {})
            current_cookies = current_data.get("Cookies", 0)
            current_streaks = current_data.get("Streaks", 0)

            merged_data = default_user_data()
            merged_data.update(current_data)

            # Transfer old cookies.
            # If they already had cookies in master_data, add beta bonus.
            if current_cookies > 0:
                merged_data["Cookies"] = old_cookies + 1000
                beta_bonus_count += 1
            else:
                merged_data["Cookies"] = old_cookies

            # Use whichever streak is higher.
            merged_data["Streaks"] = max(old_streaks, current_streaks)

            await bot.db.update_one(
                {"_id": guildID},
                {"$set": {f"users.{userID}": merged_data}}
            )

            user_count += 1

        server_count += 1

    await ctx.send(
        f"Transfer complete!\n"
        f"Updated `{user_count}` users across `{server_count}` servers.\n"
        f"Beta bonus added to `{beta_bonus_count}` existing users."
    )