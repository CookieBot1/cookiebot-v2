from datetime import datetime, timedelta, timezone
import time

import discord

from resources.constants import ADMIN_USERS
from resources.mrcookie import instance as bot


async def is_admin(userID):
    for value in ADMIN_USERS:
        if userID == value:
            return True
    return False


BLACKLIST_TTL = 300

if not hasattr(bot, "blacklist_cache"):
    bot.blacklist_cache = {}

async def is_blacklisted(userID) -> bool:
    userID = int(userID)
    now = time.time()

    cached = bot.blacklist_cache.get(userID)
    if cached is not None:
        value, ts = cached
        if (now - ts) < BLACKLIST_TTL:
            return value

    doc = await bot.db.find_blacklist({"_id": str(userID)})
    value = doc is not None
    bot.blacklist_cache[userID] = (value, now)
    return value


async def validate_user(userID):
    userID = userID.strip("<@!>")
    if userID == "0" or userID.isdigit() == False or len(userID) < 17:
        return None
    else:
        return int(userID)


# bot_central data
async def lookup_bot_central():
    data = await bot.db.find_bot_central({"_id": "bot_central"})
    if data != None:
        return data
    else:
        return False

async def update_devalerts(date, message: dict, expires_at=None):
    alert = {
        "date": date,
        "expiresAt": expires_at.isoformat() if expires_at else None,
        "message": message
    }

    await bot.db.update_bot_central({"$push": {"DevAlerts": alert}})

# user data
async def lookup_database(userID, guildID):
    data = await bot.db.find_user({"_id": str(guildID), f"users.{userID}": {"$exists": True}})
    if data != None:
        return data
    else:
        return False
    

## REMOVE AFTER COOKIE TRANSFERS - this looks at OLD DB!!!!!!!!!
async def lookup_old_database(userID, guildID):
    data = await bot.db.find_old_user({"_id": str(guildID), f"users.{userID}": {"$exists": True}})
    if data != None:
        return data
    else:
        return False
async def update_old_database(userID, guildID, updated_dict):
    await bot.db.update_old_one({"_id": str(guildID)}, {"$set": {"users." + str(userID): {**updated_dict}}})
## -----------


async def new_database(userID, guildID):
    newUser = {
        "Cookies": 0,
        "Streaks": 0,
        "DailyExpire": datetime.now() - timedelta(hours=24),
        "DailyMultiplier": 0,
        "DailyMultExpire": datetime.now(),
        "RobExpire": datetime.now() - timedelta(hours=24),
        "RobChances": 7,  ## default rob chance, 70% failure
        "RobProtection": datetime.now() - timedelta(hours=24),
        "RobCount": 0,
        "RobGains": 0,
        "Counter": 0,
        "CountSaves": 0,
        "FailCounter": 0,
        "Inventory": "Empty",
        "Bio": "No bio set. Run ``.customize profile`` to set one!",
        "ProfileOptions": {"Cookies": True, "Streaks": True, "Counting": True, "Robbery": True, "Inventory": False},
        "ProfileColor": 0x7289da,
        "DevAlerts": True,
        "AlertState": {
            "readId": None,
            "pingForId": None,
            "pingCount": 0
        },
        "Married": 0
    }
    await bot.db.update_one({"_id": str(guildID)}, {"$set": {"users." + str(userID): {**newUser}}})


async def update_database(userID, guildID, updated_dict):
    await bot.db.update_one({"_id": str(guildID)}, {"$set": {"users." + str(userID): {**updated_dict}}})


async def update_value(userID, guildID, item, new_value):
    await bot.db.update_one({"_id": str(guildID)}, {"$set": {"users." + str(userID) + "." + item: new_value}})


# Update multiple values for user db data using kwargs
async def update_many_values(userID, guildID, **kwargs):
    base_str = f"users.{str(userID)}."
    set_dict = {base_str + key: val for key, val in kwargs.items()}  # expand kwargs to format

    await bot.db.update_one({"_id": str(guildID)}, {"$set": set_dict})


# counter data
async def lookup_counter(guildID):
    data = await bot.db.find_user({"_id": str(guildID), "settings.counter": {"$exists": True}})
    if data == None:
        return False
    else:
        return data


async def new_counter(guildID):
    newGuild = {
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
    await bot.db.update_one({"_id": str(guildID)}, {"$set": {"settings." + "counter": {**newGuild}}})


async def update_counter(guildID, item, new_value):
    await bot.db.update_one(
        {"_id": str(guildID)}, {"$set": {"settings." + "counter" + "." + item: new_value}}
    )

SERVER_TTL = 300

if not hasattr(bot, "server_cache"):
    bot.server_cache = {}  # guildID -> (data, ts)

async def lookup_server(guildID):
    now = time.time()

    cached = bot.server_cache.get(guildID)
    if cached is not None:
        data, ts = cached
        if (now - ts) < SERVER_TTL:
            return data

    data = await bot.db.find_user({"_id": str(guildID), "settings.server": {"$exists": True}})
    if data is None:
        return False

    bot.server_cache[guildID] = (data, now)
    return data

def invalidate_server_cache(guildID: int):
    bot.server_cache.pop(guildID, None)

async def new_server(guildID):
    newGuild = {
        "IgnoredChannels": [],
        "IgnoredChannelDrops": [],
    }
    await bot.db.update_one({"_id": str(guildID)}, {"$set": {"settings.server": {**newGuild}}})
    invalidate_server_cache(int(guildID))

async def update_server(guildID, item, new_value):
    await bot.db.update_one({"_id": str(guildID)}, {"$set": {"settings.server." + item: new_value}})
    invalidate_server_cache(int(guildID))


async def update_ignored_drops(guildID, new_value: list):
    await bot.db.update_one(
        {"_id": str(guildID)}, {"$set": {"settings.server.IgnoredChannelDrops": new_value}}
    )
    invalidate_server_cache(int(guildID))

async def update_ignored_channels(guildID, new_value: list):
    await bot.db.update_one(
        {"_id": str(guildID)}, {"$set": {"settings.server.IgnoredChannels": new_value}}
    )
    invalidate_server_cache(int(guildID))