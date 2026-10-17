import asyncio

# env stuff
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from resources.mrcookie import MrCookie

load_dotenv()

# for bot uptime tracking
start_time = []

# nub logging
discord.utils.setup_logging()

# intent
intents = discord.Intents.default()
intents.message_content = False
intents.members = False
intents.presences = False


async def main():

    bot = MrCookie(
        command_prefix = '.',
        mongodb_url = os.getenv("uri_p"),
        intents=intents,
    )

    bot.latest_alert = None
    from resources.checks import is_blacklisted

    @bot.tree.interaction_check
    async def global_blacklist_check(interaction: discord.Interaction) -> bool:
        try:
            blacklisted = await asyncio.wait_for(
                is_blacklisted(interaction.user.id),
                timeout=2.0
            )
        except asyncio.TimeoutError:
            await interaction.response.send_message(
                "CookieBot is having trouble checking permissions. Please try again.",
                ephemeral=True
            )
            return False

        if blacklisted:
            await interaction.response.send_message(
                "You are blacklisted from using CookieBot.",
                ephemeral=True
            )
            return False

        return True

    MODULES = ["modules/commands", "modules/events", "modules/commands/drops", "modules/commands/counter"]
    bot.remove_command('help') # remove the default help command

    ## loop through all the files under the commands folder, that's how we check for commands
    for directory in MODULES:
        files = [
            name
            for name in os.listdir("src/" + directory.replace(".", "/"))
            if name[:1] != "." and name[:2] != "__" and name != "_DS_Store"
        ]

        for filename in [f.replace(".py", "") for f in files]:
            if filename in ("bot", "__init__"):
                continue

            bot.load_module(f"{directory.replace('/','.')}.{filename}")

    async with bot:
        await bot.login(token=os.getenv("token"))
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands: {[cmd.name for cmd in synced]}")
        await bot.connect()


if __name__ == "__main__":
    asyncio.run(main())