from resources.mrcookie import instance as bot
import discord
from datetime import datetime, timezone
from resources.checks import lookup_database, new_database, validate_user, is_blacklisted


BELLA_ID = 846544080111665182


def fmt_int(x):
    try:
        return f"{int(x):,}"
    except:
        return str(x)


def format_duration(start_date):
    if not start_date:
        return "Unknown"

    # Mongo may return a datetime already
    if isinstance(start_date, str):
        try:
            start_date = datetime.fromisoformat(start_date)
        except:
            return "Unknown"

    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    delta = now - start_date

    days = delta.days

    years = days // 365
    days %= 365

    months = days // 30
    days %= 30

    parts = []

    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")

    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")

    if days or not parts:
        parts.append(f"{days} day{'s' if days != 1 else ''}")

    return ", ".join(parts)


@bot.command(aliases=["relationshipstats", "couple"])
async def relationship(ctx, userID="0"):
    try:
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)

        ## determine whose relationship to show
        if userID != "0":
            userID = await validate_user(userID)

            if userID is None or guild.get_member(int(userID)) is None:
                raise Exception("Invalid user, try again!")

            if await is_blacklisted(userID):
                raise Exception("Can't show relationship, user is blacklisted.")
        else:
            userID = ctx.author.id

        userID = str(userID)

        member = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))

        ## fetch user database
        userData = await lookup_database(userID, guildID)

        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)

        userThing = userData["users"].get(userID, {})

        marriedStatus = userThing.get("Married")
        userMarried = 0 if marriedStatus is None else int(marriedStatus)

        ## not married
        if userMarried == 0:
            embed = discord.Embed(
                title="💔 Welcome to the Single Club!",
                description=f"{member.mention} isn't married to anyone.",
                color=0x992D22
            )

            embed.set_thumbnail(url=member.display_avatar.url)

            await ctx.send(embed=embed)
            return

        partnerID = str(userMarried)

        partner = guild.get_member(int(partnerID))

        if partner is None:
            try:
                partner = await guild.fetch_member(int(partnerID))
            except:
                raise Exception("Couldn't find this user's partner.")

        ## fetch partner database
        partnerData = await lookup_database(partnerID, guildID)

        if partnerData == False:
            await new_database(partnerID, guildID)
            partnerData = await lookup_database(partnerID, guildID)

        partnerThing = partnerData["users"].get(partnerID, {})

        ## make sure marriage points both ways
        partnerMarried = partnerThing.get("Married")

        if partnerMarried is None or int(partnerMarried) != int(userID):
            raise Exception("Marriage data isn't consistent.. weird.")

        ## stats
        userCookies = int(userThing.get("Cookies", 0))
        partnerCookies = int(partnerThing.get("Cookies", 0))

        userRobCount = int(userThing.get("RobCount", 0) or 0)
        partnerRobCount = int(partnerThing.get("RobCount", 0) or 0)

        userRobGains = int(userThing.get("RobGains", 0) or 0)
        partnerRobGains = int(partnerThing.get("RobGains", 0) or 0)

        richerPartner = (
            member.display_name
            if userCookies >= partnerCookies
            else partner.display_name
        )

        biggerCriminal = (
            member.display_name
            if userRobCount >= partnerRobCount
            else partner.display_name
        )

        combinedCookies = userCookies + partnerCookies
        combinedRobberies = userRobCount + partnerRobCount
        combinedRobGains = userRobGains + partnerRobGains

        ## marriage date
        marriageDate = userThing.get("MarriageDate")

        if marriageDate is None:
            marriageDate = partnerThing.get("MarriageDate")

        duration = format_duration(marriageDate)

        ## special Bella relationship
        is_bella_relationship = (
            int(userID) == BELLA_ID or
            int(partnerID) == BELLA_ID
        )

        if is_bella_relationship:
            embed_color = 0x9B59B6
            title = f"💜 {member.display_name} + {partner.display_name} 🦋"
            footer = "Been waiting to love each other since 2021 💜"
            desc = "Best friends, lovers, and the cutest little cookie monsters in the world 🥹💜"
        else:
            embed_color = 0xFF69B4
            title = f"💍 {member.display_name} + {partner.display_name}"
            footer = "Powered By Sam"
            desc = "Happily married! 🍪"

        relationship_embed = discord.Embed(
            title=title,
            color=embed_color
        )

        relationship_embed.description = desc

        relationship_embed.add_field(
            name="❤️ Together",
            value=f"**{duration}**",
            inline=True
        )

        relationship_embed.add_field(
            name="🍪 Cookies",
            value=f"**{fmt_int(combinedCookies)}**",
            inline=True
        )

        relationship_embed.add_field(
            name="🏆 Richer Partner",
            value=f"**{richerPartner}**",
            inline=True
        )

        relationship_embed.add_field(
            name="💰 Robberies",
            value=f"**{fmt_int(combinedRobberies)}**",
            inline=True
        )

        relationship_embed.add_field(
            name="✨ Robbery Gains",
            value=f"**{fmt_int(combinedRobGains)}** Cookies",
            inline=True
        )

        relationship_embed.add_field(
            name="🦹 Bigger Criminal",
            value=f"**{biggerCriminal}**",
            inline=True
        )

        if is_bella_relationship:
            relationship_embed.add_field(
                name="💜 Us",
                value=(
                    "My baby, my wifey, my Bellita, and the love of my life.\n"
                    "I'd relive every moment of my life again just to be with you. ❤️"
                ),
                inline=False
            )

        relationship_embed.set_thumbnail(url=member.display_avatar.url)
        relationship_embed.set_footer(text=footer)

        await ctx.send(embed=relationship_embed)

    except Exception as Error:
        await ctx.send(str(Error))