import discord
from discord.ext import commands

from resources.mrcookie import instance as bot

@bot.command(aliases = ["cmds", "commands"])
async def help(ctx, category = "general"):
    try:
        category = category.lower()
        aliases = {
            "main": "general",
            "gen": "general",
            "information": "info",
            "inf": "info",
            "setting": "settings",
            "count": "counter",
            "counting": "counter",
            "cookie": "cookies",
            "statistics": "stats",
            "stat": "stats",
            "social": "fun",
        }
        category = aliases.get(category, category)
        if category not in ["general", "info", "settings", "counter", "cookies", "stats", "fun"]:
            return await ctx.reply(
                "Invalid help type! Please use: `general`, `info`, `settings`, `counter`, `cookies`, `stats`, `fun`.",
                delete_after=7
            )

        if category == "general":
            # send the help embed
            help_embed = discord.Embed(
                description = "Use ``.help (category)`` to learn more about these commands!",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            help_embed.set_author(name = "CookieBot Help Page", icon_url = ctx.bot.user.avatar)

            help_embed.add_field(name = "📖 Info", value = 
            "All the general info commands about CookieBot." + "\n" +
            "``.alerts`` ``.help`` ``.ping`` ``.info`` ``.invite``", inline = False)
    
            help_embed.add_field(name = "⚙️ Settings", value =
            "Commands to customize CookieBot's settings in your server." + "\n" + 
            "``.settings`` ``.ignoredrops`` ``.ignorechannels`` ``.setcounter`` ``.editcounter`` ``.resetcounter`` ", inline = False)
            
            help_embed.add_field(name = "✏️ Counter", value =
            "All the commands involving the counting game!" + "\n" +
            "``.savecount`` ``.skipcount``", inline = False)
            
            help_embed.add_field(name = "🍪 Cookies", value =
            "All the economy commands involving cookies." + "\n" +
            "``.daily`` ``.rob`` ``.give`` ``.eat`` ``.shop``", inline = False)

            help_embed.add_field(name = "📈 Stats", value =
            "View fun statistics about the server and users!" + "\n" +
            "``.profile`` ``.customize`` ``.leaderboard`` ``.balance`` ``.stats``", inline = False)

            help_embed.add_field(name = "🎱 Fun", value =
            "All the fun and social commands for the server!" + "\n" +
            "``.marry`` ``.divorce``", inline = False)

            help_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=help_embed)
        
        if category == "info":
            # send the info embed
            info_embed = discord.Embed(
                description = "General info commands about CookieBot.",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            info_embed.set_author(name = "Info Help Page", icon_url = ctx.bot.user.avatar)

            info_embed.add_field(name = "🔹 Developer Alerts", value = 
            "Toggle developer alerts for updates and announcements." + "\n" +
            "For more info on developer alerts, run ``.alert help``." + "\n" +
            "Usage: ``.alert on`` or ``.alert off`` to toggle. To read alerts, run ``.alert``.", inline = False)

            info_embed.add_field(name = "🔹 Help Page", value = 
            "Lists all available CookieBot commands." + "\n" +
            "Usage: ``.help`` or ``.help <category>``" + "\n" +
            "``<category>`` can be either ``info``, ``settings``, ``counter``, ``cookies``, or ``stats``.", inline = False)
    
            info_embed.add_field(name = "🔹 Ping", value = 
            "Sends the bot's latency." + "\n" +
            "Usage: ``.ping``", inline = False)
            
            info_embed.add_field(name = "🔹 Bot Info", value =
            "Sends statistical information about CookieBot." + "\n" +
            "Usage: ``.info``", inline = False)
            
            info_embed.add_field(name = "🔹 Bot Invite", value =
            "Invite CookieBot to your server." + "\n" +
            "Usage: ``.invite``", inline = False)

            info_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=info_embed)
        
        if category == "settings":
            # send the settings embed
            settings_embed = discord.Embed(
                description = "Commands to customize CookieBot's settings in your server. All of the following commands require the ``Manage Server`` permission.",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            settings_embed.set_author(name = "Settings Help Page", icon_url = ctx.bot.user.avatar)

            settings_embed.add_field(name = "🔹 Server Settings", value = 
            "View server settings such as counter configuration and ignored drops." + "\n" +
            "Usage: ``.settings (optional: category)``" + "\n" +
            "``category`` can be either ``counter`` or ``cookie`` to view specific settings.", inline = False)
    
            settings_embed.add_field(name = "🔹 Ignore Cookie Drops", value = 
            "Change which channels ignore cookie drops. Commands can still be run in these channels unless disabled." + "\n" +
            "Usage: ``.ignoredrops (optional: #channel)``", inline = False)

            settings_embed.add_field(name = "🔹 Ignore Command Channels", value = 
            "Change which channels ignore command usage. Cookie drops are still sent in these channels unless disabled." + "\n" +
            "Usage: ``.ignorechannels (optional: #channel)``", inline = False)
            
            settings_embed.add_field(name = "🔹 Set Counter Channel", value =
            "Start the prompt to select the channel where users can start counting." + "\n" +
            "Usage: ``.setcounterchannel``", inline = False)

            settings_embed.add_field(name = "🔹 Edit Counter Settings", value =
            "Edit the settings for the counter in your server." + "\n" +
            "Usage: ``.editcounter (feature)``", inline = False)

            settings_embed.add_field(name = "🔹 Reset Counter Channel", value =
            "Reset the channel where counting is tracked." + "\n" +
            "Usage: ``.resetcounterchannel``", inline = False)

            settings_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=settings_embed)

        if category == "counter":
            # send the counter embed
            counter_embed = discord.Embed(
                description = "All the commands involving the counting game!",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            counter_embed.set_author(name = "Counter Help Page", icon_url = ctx.bot.user.avatar)

            counter_embed.add_field(name = "🔹 Revive Count", value = 
            "Restore the count if someone messes up." + "\n" +
            "Usage: ``.savecount``", inline = False)
    
            counter_embed.add_field(name = "🔹 Skip Count", value = 
            "Skip the current number by a random amount just to troll." + "\n" +
            "Usage: ``.skipcount``", inline = False)

            counter_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=counter_embed)

        if category == "cookies":
            # send the counter embed
            counter_embed = discord.Embed(
                description = "All the economy commands involving cookies.",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            counter_embed.set_author(name = "Cookies Help Page", icon_url = ctx.bot.user.avatar)

            counter_embed.add_field(name = "🔹 Daily Cookies", value = 
            "Collect your daily cookies reward." + "\n" +
            "Usage: ``.daily``", inline = False)
    
            counter_embed.add_field(name = "🔹 Robbery", value = 
            "Attempt to rob cookies from another user. Chances are random." + "\n" +
            "Usage: ``.rob (user)``" + "\n" +
            "``user`` can be a mention or user ID.", inline = False)

            counter_embed.add_field(name = "🔹 Give Cookies", value = 
            "Give cookies to another user." + "\n" +
            "Usage: ``.give (user) (amount)``" + "\n" +
            "``user`` can be a mention or user ID.", inline = False)

            counter_embed.add_field(name = "🔹 Eat Cookies", value = 
            "Eat one cookie at a time, there's no benefit to this lol." + "\n" +
            "Usage: ``.eat (amount)``", inline = False)

            counter_embed.add_field(name = "🔹 Cookie Shop", value = 
            "Browse and purchase items from the cookie shop." + "\n" +
            "Usage: ``.shop``", inline = False)

            counter_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=counter_embed)

        if category == "stats":
            # send the stats embed
            stats_embed = discord.Embed(
                description = "View fun statistics about the server and users!",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            stats_embed.set_author(name = "Stats Help Page", icon_url = ctx.bot.user.avatar)

            stats_embed.add_field(name = "🔹 User Profile", value = 
            "View your or someone else's customizable profile!" + "\n" +
            "Usage: ``.profile (optional: user)``" + "\n" +
            "``user`` can be a mention or user ID.", inline = False)
    
            stats_embed.add_field(name = "🔹 Customize Your Settings", value = 
            "Customize your profile and other preferences." + "\n" +
            "Usage: ``.customize to see what you can configure.``", inline = False)

            stats_embed.add_field(name = "🔹 Server Leaderboards", value = 
            "View leaderboards for various categories." + "\n" +
            "Usage: ``.leaderboard (optional: category)``" + "\n" +
            "``category`` can be ``cookies``, ``count``, or ``countfail``.", inline = False)

            stats_embed.add_field(name = "🔹 Cookie Balance", value = 
            "View your or someone else's cookie balance." + "\n" +
            "Usage: ``.balance (optional: user)``" + "\n" +
            "``user`` can be a mention or user ID.", inline = False)

            stats_embed.add_field(name = "🔹 Fun Server Stats", value = 
            "View highest stats in the server such as most robberies, cookies, counting, and more!" + "\n" +
            "Usage: ``.stats``", inline = False)

            stats_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=stats_embed)

        if category == "fun":
            # send the fun embed
            fun_embed = discord.Embed(
                description = "All the fun and social commands for the server!",
                color = 0x9b59b6,
                )
    
            # title and profile icon
            fun_embed.set_author(name = "Fun Help Page", icon_url = ctx.bot.user.avatar)

            fun_embed.add_field(name = "🔹 Marry", value = 
            "Marry another user in the server." + "\n" +
            "Usage: ``.marry (user)``" + "\n" +
            "``user`` can be a mention or user ID.", inline = False)

            fun_embed.add_field(name = "🔹 Divorce", value = 
            "Divorce your current spouse." + "\n" +
            "Usage: ``.divorce``", inline = False)

            fun_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=fun_embed)

    except Exception as Error:
        await ctx.send(Error)