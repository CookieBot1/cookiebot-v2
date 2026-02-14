import discord
from discord.ext import commands
from resources.checks import update_value, lookup_database, new_database, update_database

from resources.mrcookie import instance as bot
from resources.helpers import get_latest_active_alert

async def send_alerts_help(ctx):
    # send the help embed
    help_embed = discord.Embed(
        description = "If we release an update or announcement, you'll be told to open ``.alerts`` whenever you run ``.daily``",
        color = 0x9b59b6,
        )
            
    help_embed.set_author(name = "Subscribe to Developer Alerts!", icon_url = ctx.bot.user.avatar)

    help_embed.add_field(name = "🟢 How do I enable developer alerts?", value =
    "Use ``.alerts on`` or ``.alerts off`` to toggle alerts", inline = False)

    help_embed.add_field(name = "🍪 What else can I get from alerts?", value =
    "Besides knowing what's new, we also sometimes send free cookies and shop items.. so you should turn on alerts", inline = False)

    return await ctx.reply(embed = help_embed)


@bot.command(aliases = ["devalerts", "alert"])
async def alerts(ctx, option = "view"):
    try:
        category = option.lower()
        aliases = {
            "general": "help",
            "yes": "on",
            "true": "on",
            "no": "off",
            "false": "off",
            "enable": "on",
            "disable": "off",
            "read": "view",
            "open": "view"
        }
        category = aliases.get(category, category)
        if category not in ["on", "off", "help", "view"]:
            return await ctx.reply(
                "Invalid alert type! Please use: `on`, `off`, `help`, `view`, or just say ``.alerts``.",
                delete_after=7
            )

        if category == "view":
            userID = str(ctx.author.id)
            guildID = ctx.guild.id

            userData = await lookup_database(userID, guildID)
            if not userData:
                await new_database(userID, guildID)
                userData = await lookup_database(userID, guildID)

            '''user_alerts = userData["users"].get(userID, {}).get("alerts", False)'''

            ## THIS IS TEMPORARY SINCE OLD DB MIGHT HAVE NO ALERTS VALUE, REMOVE LATER!!!!!!
            userThing = userData["users"].get(userID, {})

            user_alerts = userThing.get("DevAlerts")

            user_alerts = False if user_alerts is None else bool(user_alerts)
            ## ------------------------------------------------------------

            # if alerts are off, just show help instead
            if not user_alerts:
                return await send_alerts_help(ctx)
            else:
                latest_alert = get_latest_active_alert()
                if not latest_alert:
                    return await ctx.send("No alerts at this time.")

                embed = discord.Embed.from_dict(latest_alert["message"])
                await ctx.send(embed=embed)

                # mark this alert as read for this user
                u = userData["users"][userID]

                state = u.get("AlertState", {})
                current_id = latest_alert.get("date")

                state["readId"] = current_id
                state["pingForId"] = current_id
                state["pingCount"] = 0

                u["AlertState"] = state

                await update_database(userID, guildID, u)

        elif category == "help":
            return await send_alerts_help(ctx)

        else:
            # toggle alerts
            userID = str(ctx.author.id)
            guildID = ctx.guild.id

            if category == "on":
                await update_value(userID, guildID, "DevAlerts", True)
                await ctx.reply("✅ Developer alerts have been turned **ON**!" + "\n" + "When you run ``.daily``, you'll be notified to open ``.alerts`` if there's any update or announcement.")

            elif category == "off":
                await update_value(userID, guildID, "DevAlerts", False)
                await ctx.reply("❌ Developer alerts have been turned **OFF**." + "\n" + "You won't receive notifications anymore.")

    except Exception as Error:
        await ctx.send(Error)