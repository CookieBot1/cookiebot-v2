from resources.checks import is_blacklisted, lookup_counter, lookup_server
from resources.mrcookie import instance as bot
from resources.constants import JUNO_ID
import discord

from modules.commands.counter.counter import safe_eval_int


import asyncio
import random

@bot.event
async def on_message(message):
    if message.author.bot or await is_blacklisted(message.author.id):
        return

    ## juno only
    if message.author.id == JUNO_ID:
        ctx = await bot.get_context(message)

        if ctx.valid:

            serverData = await lookup_server(message.guild.id)
            if serverData is False:
                await new_server(message.guild.id)
                serverData = await lookup_server(message.guild.id)

            junomode = serverData["settings"]["server"]["juno"]
            if not junomode:
                await bot.process_commands(message)
                return

            ## fake "processing"
            async with message.channel.typing():
                await asyncio.sleep(random.uniform(1.2, 4.8))

            cmd = (ctx.command.name or "").lower()

            ## fake balance
            if cmd in {"balance", "bal"}:
                fake_cookies = random.randint(-200, 10)

                embed = discord.Embed(
                    title="🍪 Cookie Balance",
                    color=0xe74c3c  # red = broke
                )

                embed.add_field(name = "Cookies", value = fake_cookies, inline = True)
                embed.add_field(name = "Rank", value = "#1 in D4VD's Mind", inline = True)
                embed.set_footer(text="Tip: Maybe DONT gamble your savings..")

                await message.channel.send(embed=embed)

            ## fake rob
            elif cmd == "rob":
                outcomes = [
                    "🚓 You were caught INSTANTLY, IMAGINE. **0 cookies stolen.**",
                    "🧤 Lowkeyy you tripped mid-heist.. **Mission failed.**",
                    "📸 RRUNNNUN!! NOOO.. you were deported by ICE.",
                    "💥 Idk how but you.. you.. robbed yourself.. **-100 cookies.**",
                    "🪤 You got too close to cooldude and exploded.. **RIP**",
                ]

                embed = discord.Embed(
                    title="💅 Robbery Did Not Slay",
                    description=random.choice(outcomes),
                    color=0x992d22
                )
                embed.set_footer(text="Tsk Tsk Crime does not pay. Especially for YOU.")

                await message.channel.send(embed=embed)


            ## fake daily
            elif cmd == "daily":
                fake_daily = random.randint(-500, 5)

                embed = discord.Embed(
                    description=f"You have collected your daily **{fake_daily} cookies**!\nCome back tomorrow for more crumbs.",
                    color=0xf1c40f
                )
                embed.set_author(name = "Daily Cookies - Juno", icon_url = "https://imgur.com/a/NJhSWyC")
                embed.set_footer(text="Streak: 1 day (CMON JUNO YOU CAN DO BETTER)")

                await message.channel.send(embed=embed)

            elif cmd == "profile":
                embed = discord.Embed(
                    title=f"{message.author.display_name}'s Profile",
                    description="Haay Slayerzzz, I'm Juno! Welcoom to mah profile ig uwu 👑✨\n\n",
                    color=0x9b59b6
                )
                embed.add_field(name="Cookies", value="*embarrassed*", inline=True)
                embed.add_field(name="Streaks", value="30 Years (age accurate)", inline=True)
                embed.add_field(name="Rank", value="PFFFT", inline=True)

                embed.add_field(name="Counter Stats", value="5", inline=True)
                embed.add_field(name="Count Fails", value="999 Fails", inline=True)
                embed.add_field(name="Count Saves", value="WIP", inline=True)

                embed.add_field(name="Rob Count", value="Only Gets Robbed", inline=True)
                embed.add_field(name="Rob Gains", value="-1000 Cookies Somehow", inline=True)
                embed.add_field(name="Rob Chances", value="100%", inline=True)

                embed.set_footer(text="Weirdest profile ever ngl")
                embed.set_thumbnail(url= message.author.display_avatar.url)   
                
                await message.channel.send(embed=embed)

            ## any other command
            else:
                await ctx.send("💀 **BOT ERRORING...**")
                await ctx.send("01000001 01110011 00100000 01001010 01110101 01101110 01101111 00100000 01101111 01101110")
                await ctx.send("01100011 01100101 00100000 01110011 01100001 01101001 01100100 00101110 00101110 00100000")
                await ctx.send("01001000 01001001 00100000 01000100 01000001 01010110 01001001 01000100 00100000 01000010")
                await ctx.send("01000001 01010010 01001011 01001011 01001011 01001011 00101110 00101110.")

                await ctx.send("*SHUTTING* ``DOWN`` **IN** 3... __DOS__... 1... **AHHHHHHH**")
                await ctx.send("https://tenor.com/view/ill-be-missing-you-missing-you-p-diddy-puff-daddy-big-gif-22616397")
        
            return

    await bot.process_commands(message)



@bot.listen()
async def on_message_delete(message: discord.Message):
    if message.guild is None:
        return

    # ignore bot messages
    if message.author and message.author.bot:
        return

    counterData = await lookup_counter(message.guild.id)
    if counterData is False:
        return

    channelID = counterData["settings"]["counter"].get("Channel", 0)
    if channelID == 0:
        return

    # only care about the counting channel
    if message.channel.id != channelID:
        return

    # if message content is missing (uncached), we can't know what it was
    if not message.content:
        return

    raw = message.content.strip()

    # check if it was a number
    parsed = int(raw) if raw.isdigit() else None

    # optionally allow math expressions
    allow_math = counterData["settings"]["counter"].get("AllowMath", False)
    if parsed is None and allow_math:
        parsed = safe_eval_int(raw)

    # if it wasn't a valid counting attempt, ignore
    if parsed is None:
        return

    # it WAS a counting attempt — warn users
    savedCounter = counterData["settings"]["counter"].get("Counter", 0)
    next_count = savedCounter + 1

    if message.author:
        who = message.author.mention
    else:
        who = "Someone"

    await message.channel.send(
        f"⚠️ {who} deleted a counting message!! Next count is **{next_count}**"
    )

