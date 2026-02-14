import logging

from discord import CustomActivity, Status

from resources.mrcookie import instance as bot
from resources.checks import lookup_bot_central

from datetime import datetime, timezone


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=CustomActivity(name="Baking cookies!"),
        status=Status.online,
    )
    logging.info(f"{bot.user.name}#{bot.user.discriminator} is now logged in & ready!")

    ## load the latest alert from the database on startup
    data = await lookup_bot_central()
    if data and data.get("DevAlerts"):
        latest = data["DevAlerts"][-1]
        exp = latest.get("expiresAt")

        if exp and datetime.fromisoformat(exp) <= datetime.now(timezone.utc):
            bot.latest_alert = None
        else:
            bot.latest_alert = latest
    else:
        bot.latest_alert = None