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
        }
        category = aliases.get(category, category)
        if category not in ["general", "info", "settings", "counter", "cookies"]:
            return await ctx.reply(
                "Invalid help type! Please use: `general`, `info`, `settings`, `counter`, `cookies`.",
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
            "All the general information commands about CookieBot." + "\n" +
            "``.help`` ``.ping`` ``.info`` ``.invite``", inline = False)
    
            help_embed.add_field(name = "⚙️ Settings", value =
            "Commands to customize CookieBot's settings in your server." + "\n" + 
            "``.settings`` ``.ignoredrops`` ``.configcounter`` ``.setcounterchannel`` ``.resetcounter`` ", inline = False)
            
            help_embed.add_field(name = "✏️ Counter", value =
            "Commands to manage the counting game in your server." + "\n" +
            "``.leaderboard count`` ``.leaderboard countfails`` ``.savecount``", inline = False)
            
            help_embed.add_field(name = "🍪 Cookies", value =
            "All the fun commands involving cookies!" + "\n" +
            "``.daily`` ``.rob`` ``.give`` ``.eat`` ``.balance`` ``.leaderboard cookies`` ``.shop``", inline = False)

            help_embed.set_footer(text = "Need help? Join our server: https://discord.gg/QVNAyWfVsG")
            await ctx.send(embed=help_embed)
        
        if category == "info":
            await ctx.send("Info section WIP")
        
        if category == "settings":
            await ctx.send("Settings section WIP")

        if category == "counter":
            await ctx.send("Counter section WIP")

        if category == "cookies":
            await ctx.send("Cookies section WIP")


        '''"``.help``➙ View this help page to learn about CookieBot." + "\n" +
        "``.ping`` ➙ Find the latency from the bot to Discord." + "\n" +
        "``.info`` ➙ [Aliases: status] Information about the bot's status and more." + "\n" +
        "``.invite`` ➙ Invite CookieBot to your server. ", inline = True)'''

        '''"``.daily`` ➙ Collect free cookies once everyday, amount increases based on streak." + "\n" + 
        "``.rob (user)`` ➙ Try to steal another user's cookies, but you may not succeed." + "\n" +
        "``.eat`` ➙ Eat one cookie cause you're hungry." + "\n" +
        "``.give (user) (amount)`` ➙ [Aliases: transfer, gift] Give another user some of your cookies.", inline = True)'''

        '''"``.leaderboard`` ➙ [Aliases: lb] View who has the highest cookies in this server." + "\n" +
        "``.stats (optional: user)`` ➙ View complete statistics of a user." + "\n" +
        "``.bal (optional: user)`` ➙ [Aliases: balance] View your or another user's cookie balance.", inline = True)'''

        '''"``.say (optional: channelID) (message)`` ➙ Have the bot post your message.", inline = True)'''
    
    except Exception as Error:
        await ctx.send(Error)
