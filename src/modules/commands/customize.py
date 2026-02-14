import discord
from resources.mrcookie import instance as bot

from resources.checks import lookup_database, new_database, update_value
import asyncio


async def edit_bio(ctx, userID, guildID, check, cleanup):
    m = await ctx.send("Please enter your new bio: (max 200 characters)\nType `cancel` to cancel the update.")
    cleanup.append(m)
    try:
        bio_msg = await bot.wait_for("message", check=check, timeout=120)  # 2 minutes to respond
        cleanup.append(bio_msg)
    except asyncio.TimeoutError:
        await ctx.send("Customization timed out. Please try again.")
        return False

    bio = bio_msg.content.strip()
    if bio.lower() == "cancel" or bio.lower() == "exit":
        m = await ctx.send("❌ Bio update cancelled. No changes made.")
        cleanup.append(m)
        return False
    if len(bio) > 200:
        m = await ctx.send("Bio is too long! Please keep it under 200 characters.")
        cleanup.append(m)
        return False                 
    await update_value(userID, guildID, "Bio", bio)
    m = await ctx.send("✅ Your bio has been updated successfully!")
    cleanup.append(m)
    return True

async def edit_color(ctx, userID, guildID, check, cleanup):
    colors = {
        "red": "0xFF0000",
        "green": "0x00FF00",
        "blue": "0x0000FF",
        "yellow": "0xFFFF00",
        "purple": "0x800080",
        "orange": "0xFFA500",
        "pink": "0xFFC0CB",
        "black": "0x000000",
        "white": "0xFFFFFF",
        "cyan": "0x00FFFF",
    }

    m = await ctx.send("**Choose a color: **" + ", ".join([c.title() for c in colors.keys()]) + "\nType `cancel` to cancel the update.")
    cleanup.append(m)

    try:
        color_msg = await bot.wait_for("message", check=check, timeout=120) # 2 minutes to respond
        cleanup.append(color_msg)

        if color_msg.content.lower() == "cancel" or color_msg.content.lower() == "exit":
            m = await ctx.send("❌ Color update cancelled. No changes made.")
            cleanup.append(m)
            return False
    except asyncio.TimeoutError:
        await ctx.send("Customization timed out. Please try again.")
        return False
                
    chosen_color = colors.get(color_msg.content.strip().lower())
    if chosen_color is None:
        m = await ctx.send("Invalid color choice. Please try the command again.")
        cleanup.append(m)
        return False
    else:
        await update_value(userID, guildID, "ProfileColor", int(chosen_color.lstrip('#'), 16))
        m = await ctx.send(f"✅ Your profile color has been updated to **{color_msg.content.strip().title()}**!")
        cleanup.append(m)
        return True


async def edit_stats(ctx, userID, guildID, userData, check, cleanup):
    profile_options = {
        "cookies": "Cookies",
        "streaks": "Streaks",
        "count": "Counting",
        "rob": "Robbery",
        # "inventory": "Inventory",
    }
                
    shown_list = ["Cookies", "Streaks", "Counting", "Robbery"]  # keep in sync with allowed
    m = await ctx.send(
    "Choose which stats to show (comma-separated).\n"
    f"**Options:** {', '.join(sorted(set([k for k in profile_options.keys() if len(k) >= 3])))}"
    " or `all`, `none`\n"
    "Type `cancel` to cancel the update."
    )
    cleanup.append(m)

    try:
        options_msg = await bot.wait_for("message", check=check, timeout=180) # 3 minutes to respond
        cleanup.append(options_msg)
    except asyncio.TimeoutError:
        await ctx.send("Customization timed out. Please try again.")
        return False
                
    raw = options_msg.content.strip().lower()

    if raw in {"cancel", "stop", "exit"}:
        m = await ctx.send("❌ Stats update cancelled. No changes made.")
        cleanup.append(m)
        return

    # Load current options so we don't wipe fields you didn't include (like Inventory)
    current = userData["users"][str(userID)].get("ProfileOptions", {})
    updated = dict(current)  # copy

    if raw in {"reset", "default", "all"}:
        # set your defaults
        updated.update({"Cookies": True, "Streaks": True, "Counting": True, "Robbery": True, "Inventory": False})
    elif raw == "none":
        for k in shown_list:
            updated[k] = False
    else:
        chosen = [x.strip().lower() for x in raw.split(",") if x.strip()]
        if not chosen:
            m = await ctx.send("⚠️ You didn’t pick anything. No changes made.")
            cleanup.append(m)
            return

        # Translate user input -> canonical keys
        canonical = []
        invalid = []
        for item in chosen:
            if item in profile_options:
                canonical.append(profile_options[item])
            else:
                invalid.append(item)
        # If nothing valid, don't wipe their profile
        if not canonical:
            m = await ctx.send(f"⚠️ I didn’t recognize any of those: `{', '.join(invalid[:8])}`. No changes made.")
            cleanup.append(m)
            return
        # Set the known sections on/off based on selection
        for k in shown_list:
            updated[k] = (k in canonical)

        if invalid:
            m = await ctx.send(f"⚠️ Ignored: `{', '.join(invalid[:8])}`")
            cleanup.append(m)

    await update_value(userID, guildID, "ProfileOptions", updated)
    m = await ctx.send("✅ Your profile display options have been updated!")
    cleanup.append(m)
    return True

@bot.command(aliases = ["custom", "personalize", "edit", "config", "configure"])
async def customize(ctx, category: str = "general", section: str | None = None):
    ## options include: general, profile
    try:        
        category = category.lower()
        aliases = {
            "main": "general",
            "gen": "general",
            "me": "profile",
            "user": "profile",
        }
        category = aliases.get(category, category)

        section_aliases = {
            "biography": "bio",
            "about": "bio",
            "colour": "color",
            "stat": "stats",
            "statistics": "stats",
            "options": "stats",
        }
        if section:
            section = section_aliases.get(section.lower(), section.lower())

        if category not in ["general", "profile"]:
            return await ctx.reply(
                "Invalid customize type! Please use: `general`, `profile`.",
                delete_after=7
            )
        
        ## if no option is specified, show general customize options
        if category == "general":
            # send the general customize embed
            general_embed = discord.Embed(
                description = "Here's a list of all the user customization options!",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            general_embed.set_author(name = "Customize Page", icon_url = ctx.author.display_avatar.url)

            general_embed.add_field(name = "👤 Profile", value = "Edit your profile page by using the following command:" + "\n" + "``.customize profile <optional: bio, color, stats>``", inline = False)
            general_embed.add_field(name = "🔔 Alerts", value = "Edit your alert settings by using the following command:" + "\n" + "``.alert <optional: on/off>``", inline = False)

            general_embed.set_footer(text = "More options coming soon!")
            return await ctx.send(embed=general_embed)

        ## profile flow
        userID = str(ctx.author.id)
        guildID = str(ctx.guild.id)

        userData = await lookup_database(userID, guildID)
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)

        ## make sure a bot isn't talking
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        
        ## ---- PROFILE CUSTOMIZATION CMD ----
        if category == "profile":
            cleanup = [] ## for auto deleting msgs after

            # Jump routing:
            if section in {"bio", "color", "stats"}:
                if section == "bio":
                    await edit_bio(ctx, userID, guildID, check, cleanup)
                elif section == "color":
                    await edit_color(ctx, userID, guildID, check, cleanup)
                elif section == "stats":
                    await edit_stats(ctx, userID, guildID, userData, check, cleanup)
                await ctx.send("🎉 Profile customization complete!")
                for m in cleanup:
                    try:
                        await m.delete()
                        await asyncio.sleep(0.25)
                    except (discord.Forbidden, discord.NotFound):
                        pass
                return

            else:
                # Wizard flow (yes/no prompts) — and when "yes", call helper
                m = await ctx.send("✏️ Would you like to edit your bio? Please say `yes` or `no`.")
                cleanup.append(m)
                try:
                    msg = await bot.wait_for("message", check=check, timeout=120)
                    cleanup.append(msg)
                except asyncio.TimeoutError:
                    await ctx.send("Customization timed out. Please try again.")
                    return

                if msg.content.lower() in {"yes", "y"}:
                    await edit_bio(ctx, userID, guildID, check, cleanup)

                m = await ctx.send("🎨 Would you like to change the color of your profile? Say `yes` or `no`.")
                cleanup.append(m)
                msg = await bot.wait_for("message", check=check, timeout=120)
                cleanup.append(msg)
                if msg.content.lower() in {"yes", "y"}:
                    await edit_color(ctx, userID, guildID, check, cleanup)

                m = await ctx.send("📊 Would you like to change what stats show on your profile? Say `yes` or `no`.")
                cleanup.append(m)
                msg = await bot.wait_for("message", check=check, timeout=120)
                cleanup.append(msg)
                if msg.content.lower() in {"yes", "y"}:
                    await edit_stats(ctx, userID, guildID, userData, check, cleanup)

            await ctx.send("🎉 Profile customization complete!") 
            for m in cleanup:
                try:
                    await m.delete()
                    await asyncio.sleep(0.25)  # 250ms pacing
                except (discord.Forbidden, discord.NotFound):
                    pass
            return

    except Exception as Error:
        await ctx.send(Error)