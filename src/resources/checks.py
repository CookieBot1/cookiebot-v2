from datetime import datetime, timedelta

import discord

from resources.constants import ADMIN_USERS
from resources.mrcookie import instance as bot


async def is_admin(userID):
    for value in ADMIN_USERS:
        if userID == value:
            return True
    return False


async def is_blacklisted(userID):
    if await bot.db.find_blacklist({"_id": str(userID)}) != None:
        return True
    else:
        return False


async def validate_user(userID):
    userID = userID.strip("<@!>")
    if userID == "0" or userID.isdigit() == False or len(userID) < 17:
        return None
    else:
        return userID


# user data
async def lookup_database(userID, guildID):
    data = await bot.db.find_user({"_id": str(guildID), f"users.{userID}": {"$exists": True}})
    if data != None:
        return data
    else:
        return False


async def new_database(userID, guildID):
    newUser = {
        "Cookies": 0,
        "Streaks": 0,
        "DailyExpire": datetime.now() - timedelta(hours=24),
        "DailyMultiplier": 0,
        "DailyMultExpire": datetime.now(),
        "RobExpire": datetime.now() - timedelta(hours=24),
        "RobChances": 7, ## default rob chance, 70% failure
        "RobExpire": datetime.now(),
        "RobProtection": datetime.now() - timedelta(hours=24),
        "Counter": 0,
        "FailCounter": 0,
        "Inventory": "Empty",
    }
    await bot.db.update_user({"_id": str(guildID)}, {"$set": {"users." + str(userID): {**newUser}}})


async def update_database(userID, guildID, updated_dict):
    await bot.db.update_user({"_id": str(guildID)}, {"$set": {"users." + str(userID): {**updated_dict}}})


async def update_value(userID, guildID, item, new_value):
    await bot.db.update_user(
        {"_id": str(guildID)}, {"$set": {"users." + str(userID) + "." + item: new_value}}
    )

# Update multiple values for user db data using kwargs
async def update_many_values(userID, guildID, **kwargs):
    base_str = f"users.{str(userID)}."
    set_dict = {base_str + key: val for key, val in kwargs.items()} # expand kwargs to format

    await bot.db.update_user({"_id": str(guildID)}, {"$set": set_dict})


# counter data
async def lookup_counter(guildID):
    data = await bot.db.find_user({"_id": str(guildID), f"settings.{"counter"}": {"$exists": True}})
    if data == None:
        return False
    else:
        return data


async def new_counter(guildID):
    newGuild = {
        "Channel": 0, 
        "Counter": 0, 
        "lastUser": 0,
    }
    await bot.db.update_user({"_id": str(guildID)}, {"$set": {"settings." + "counter": {**newGuild}}})


async def update_counter(guildID, item, new_value):
    await bot.db.update_user(
        {"_id": str(guildID)}, {"$set": {"settings." + "counter" + "." + item: new_value}}
    )

# server settings data
async def lookup_server(guildID):
    data = await bot.db.find_user({"_id": str(guildID), f"settings.{"server"}": {"$exists": True}})
    if data == None:
        return False
    else:
        return data

async def new_server(guildID):
    newGuild = {
        "IgnoredChannels": [],
        "IgnoredChannelDrops": []
    }
    await bot.db.update_user({"_id": str(guildID)}, {"$set": {"settings." + "server": {**newGuild}}})