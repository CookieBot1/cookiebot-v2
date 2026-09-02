from resources.mrcookie import instance as bot
import discord
import random

BELLA_ID = 846544080111665182

BELLA_TITLES = [
    "💜 Johnny's Favorite Girl",
    "🦋 My Lil 4'11 Princess",
    "🍳 Holder of La Pans",
    "🎮 Professional Rorox Player",
    "🛻 Truck Driving Babygirl",
    "💅 SLAYYYYY GO GIRL",
    "🤏 THE CLOCK ITTT-er",
    "🎵 Reggaeton Specialist",
    "😛 (Alleged) Certified Thug",
    "☕ Iced Caramel Macchiato Regular",
]

BELLA_QUOTES = [
    "God FORBID I have an entire CookieBot cmd dedicated to meee 🙄",
    "This is music to my latina ears 🎶",
    "Line by line. Bar by bar.",
    "Omg when I tell you...",
    "SLAYYYYY GO GIRL 💅",
    "CLOCK ITTT 🤏",
    "God bless I have my own cmd I'm just too GOOD 🙏",
    "uwu",
    "u.u",
    "O_o",
]

BELLA_FACTS = [
    "Her fav color is purple 💜",
    "She calls Roblox `rorox` 🎮",
    "She loves butterflies 🦋",
    "She loves her stuffies more than most people (except Johnny) 🧸",
    "She takes her pan VERY seriously 🍳",
    "She loves alfredo pasta with chicken ☕",
    "She adores Peanut M&M's 🥜",
    "Ritz + Nutella + Coffee is Bellita's FAV breakfast",
    "She loves long C curl hairrr",
    "She's allergic to kiwi's so KEEP THEM AWAY",
    "Seafood has been permanently banned from all Bella territory",
    "Drill detected. Even tho she doesn't understand it.. Bella LOVES IT.",
    "She tripped at work while running once, it was SO cute.",
    "She hates iguanas bc once under a tree she.. ahem I can't say without getting smacked..",
    "She hates crumbl bc it tastes like diabetes.. HER WORDS not mine",
    "She loves the warmthhhh, like to the point where 90 degrees could be cold to her",
    "She loves her boyfriend Johnny more than anything in the world, and he loves her back just as much 💜",
    "She took CS classes in HS JUST FOR FUN, AWWWW isn't that so cute omfg",
    "She had an adorable pet birdie when she was younger, it sat on her shoulder and everything and was as cute as her",
    "She has girly quotes all over her room and it's so adorable, like 'girls will be girls' and I just can't help but admire her cuteness.",
]

@bot.command()
async def bella(ctx):
    try:
        bella = ctx.guild.get_member(BELLA_ID)

        if bella is None:
            try:
                bella = await ctx.guild.fetch_member(BELLA_ID)
            except:
                bella = None

        title = random.choice(BELLA_TITLES)
        quote = random.choice(BELLA_QUOTES)
        fact = random.choice(BELLA_FACTS)

        embed = discord.Embed(
            title="💜 BELLITA 🦋",
            description=title,
            color=0x9B59B6
        )

        embed.add_field(
            name="🇲🇽🇻🇪 Latina Species",
            value="Mexico + Venezuela",
            inline=True
        )

        embed.add_field(
            name="💜 Favorite Color",
            value="Purple",
            inline=True
        )

        embed.add_field(
            name="🎮 Favorite Game",
            value="Rorox",
            inline=True
        )

        embed.add_field(
            name="☕ Fav Cafe",
            value="Iced Caramel Macchiato With Cold Foam",
            inline=True
        )

        embed.add_field(
            name="🍳 Weapon",
            value="La Bella Pan",
            inline=True
        )

        embed.add_field(
            name="🛻 Dream Car",
            value="Black Lifted Truck",
            inline=True
        )

        embed.add_field(
            name="🎵 Music",
            value="Reggaeton\nAlbanian Drill\nRomanian Rap",
            inline=True
        )

        embed.add_field(
            name="💅 Street Level",
            value="Certified Thug*",
            inline=True
        )

        embed.add_field(
            name="🦋 Bella Fact",
            value=fact,
            inline=False
        )

        embed.add_field(
            name="💬 Bella Quote",
            value=f"*\"{quote}\"*",
            inline=False
        )

        embed.add_field(
            name="❤️ Her Person",
            value=(
                "Johnny — her husband, lover, best friend, "
                "and the luckiest guy to have the most perfect partner in the world, my babybella 💜"
            ),
            inline=False
        )

        if bella:
            embed.set_thumbnail(url=bella.display_avatar.url)

        embed.set_footer(
            text="*Thug certification has not been verified by THE Thug Johnny."
        )

        await ctx.send(embed=embed)

        # special response if Bella herself runs the command
        if ctx.author.id == BELLA_ID:
            bella_messages = [
                "heyyy mi amorrr 🥹💜 si, this whole command is litt about you, my fav cmd in the WHOLE bot",
                "babyyy don't forget to drink water 😭💜 also I LOVE YOUUU",
                "as my wifey would say, God FORBID my Bellita has an entire CookieBot profile 🙄💜",
                "SLAYYYYY GO GIRL 💅 even CookieBot knows you're bodytee and other tiktok words ❤️",
            ]

            await ctx.send(random.choice(bella_messages))

    except Exception as Error:
        await ctx.send(Error)