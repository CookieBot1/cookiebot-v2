from resources.mrcookie import instance as bot
from discord.ext import commands

old_col = bot.db.cookieDict
new_col = bot.db.master_data


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
        "Counter": 0,
        "FailCounter": 0,
        "Inventory": "Empty",
        "RobGains": 0,
        "RobCount": 0,
        "Bio": "",
        "ProfileColor": 65535,
        "ProfileOptions": {
            "Cookies": True,
            "Streaks": True,
            "Counting": True,
            "Robbery": True,
            "Inventory": False
        },
        "DevAlerts": True,
        "AlertState": {
            "readId": None,
            "pingForId": None,
            "pingCount": 0
        },
        "Married": None
    }


@bot.command()
@commands.is_owner()
async def transferdata(ctx):
    await ctx.send("Starting data transfer...")

    server_count = 0
    user_count = 0
    beta_bonus_count = 0

    for old_server in old_col.find({}):
        serverID = str(old_server["_id"])
        old_users = old_server.get("users", {})

        new_server = new_col.find_one({"_id": serverID}) or {}
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

            # Old cookies replace new cookies.
            # If user already had cookies in master_data, add beta bonus.
            if current_cookies > 0:
                merged_data["Cookies"] = old_cookies + 1000
                beta_bonus_count += 1
            else:
                merged_data["Cookies"] = old_cookies

            # Keep whichever streak value is higher.
            merged_data["Streaks"] = max(old_streaks, current_streaks)

            new_col.update_one(
                {"_id": serverID},
                {"$set": {f"users.{userID}": merged_data}},
                upsert=True
            )

            user_count += 1

        server_count += 1

    await ctx.send(
        f"Transfer complete!\n"
        f"Updated `{user_count}` users across `{server_count}` servers.\n"
        f"Beta bonus added to `{beta_bonus_count}` existing users."
    )