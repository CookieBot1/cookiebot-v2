import asyncio
import random

import discord

from resources import checks
from resources.id_cooldown import IDCooldown
from resources.mrcookie import instance as bot

from .prompts import user_prompts

# all units in seconds
PROMPT_TIMEOUT = 75  # time for a drop to timeout
PROMPT_COOLDOWN = (3 * 60) + PROMPT_TIMEOUT  # time between drops
TIME_BETWEEN_USER_MSGS = 90  # time between messages for a drop to trigger

# Handles cooldown logic
channel_cooldowns: IDCooldown = IDCooldown(PROMPT_COOLDOWN)
# Keeps track of which channels have an active prompt
channel_lock: set[str] = set()
# Keeps track of last sent message in a channel
channel_last_message: dict[str, discord.Message] = dict()


@bot.listen()
async def on_message(message: discord.Message):
    channel_id = str(message.channel.id)

    # Ignore bot messages, ignore when channel is locked. Also ignores non text channels, and DMs.
    if (
        message.author.bot
        or channel_id in channel_lock
        or type(message.channel) != discord.TextChannel
        or message.guild is None
    ):
        return

    # Check if the channel is set to be ignored for drops.
    server_data = await checks.lookup_server(message.guild.id)
    if server_data is not False:
        ign_chn_drops = server_data["settings"]["server"].get("IgnoredChannelDrops", [])
        if message.channel.id in ign_chn_drops:
            return

    last_msg = channel_last_message.get(channel_id)
    if (
        not last_msg
        or last_msg.author.id == message.author.id
        or (message.created_at - last_msg.created_at).seconds >= TIME_BETWEEN_USER_MSGS
    ):
        channel_last_message[channel_id] = message
        return

    # This applies the cooldown automatically if there is no cooldown found.
    if channel_cooldowns.check_for_id(message.channel.id):
        channel_last_message[channel_id] = message
        return

    asyncio.create_task(process_trigger(message.channel))
    del channel_last_message[channel_id]


async def process_trigger(channel: discord.TextChannel):
    # lock as soon as possible once processing
    channel_lock.add(str(channel.id))

    ch_prsr = ChannelProcessor(str(channel.id))

    # Send prompt
    prompt_embed = discord.Embed(
        title="back alley deal",
        color=0x468674,
    )
    prompt_embed.add_field(name="🕵️‍♂️ cookie man says...", value=ch_prsr.prompt)
    prompt_embed.add_field(
        name="🍪 You'll earn:", value=f"{ch_prsr.reward} cookie{'s' if ch_prsr.reward > 1 else ''}"
    )
    prompt_embed.set_footer(text=f"BE QUICK! They're gonna burn after {PROMPT_TIMEOUT} seconds!! 🔥")
    prompt_message: discord.Message = await channel.send(embed=prompt_embed)

    # Listen for messages, then stop after asyncio.sleep.
    bot.add_listener(ch_prsr.message_listener, name="on_message")
    await asyncio.sleep(PROMPT_TIMEOUT)
    bot.remove_listener(ch_prsr.message_listener, name="on_message")

    if not ch_prsr.complete:
        await prompt_message.reply(f"-# you guys suck at this 🫵😂... try again next time ", delete_after=7)
        await asyncio.sleep(7)
        await prompt_message.delete()
    else:
        await prompt_message.delete()

    channel_lock.remove(str(channel.id))


class ChannelProcessor:
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self.prompt = random.choice(list(user_prompts.keys()))
        self.answer = user_prompts[self.prompt].lower()
        self.reward = random.randint(1, 16)
        self.complete = False

    async def message_listener(self, message: discord.Message):
        if message.author.bot or str(message.channel.id) != self.channel_id or self.complete:
            return

        content = message.content.lower()
        if content != self.answer:
            return

        self.complete = True
        await self.on_complete(message)

    async def on_complete(self, message: discord.Message):
        if not message.guild:
            # for pylance, but this should be impossible anyway
            return

        author_id = message.author.id

        prompt_embed = discord.Embed(
            title="🎉 Cookies Collected!",
            color=0x2ECC71,
            description=(
                f"Good job <@{author_id}> for being the fastest! Your pockets are now filled with "
                f"{self.reward} more cookie{'s' if self.reward >1 else ''}."
            ),
        )

        await message.reply(embed=prompt_embed, mention_author=False)

        guild_id = message.guild.id
        guild_data = await checks.lookup_database(author_id, guild_id)
        if not guild_data:
            # Populate default user data
            await checks.new_database(author_id, guild_id)
            guild_data = await checks.lookup_database(author_id, guild_id)

        user_data = guild_data.get("users", {}).get(str(author_id), {"Cookies": 0})  # type: ignore
        user_cookies = user_data["Cookies"] + self.reward

        await checks.update_value(author_id, guild_id, "Cookies", user_cookies)
