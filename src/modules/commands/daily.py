from resources.mrcookie import instance as bot
import discord
from datetime import datetime, timedelta, timezone

from resources.checks import lookup_database, new_database, update_database, lookup_bot_central
from resources.helpers import get_latest_active_alert

import random
BELLA_ID = 846544080111665182

BELLA_DAILY_MESSAGES = [
    "I love how caring you are. You always worry about me and make sure I'm okay, and I'll never stop appreciating that baby ❤️",
    "I adore how loving you are. You're always so affectionate with me and never let me forget how much you want and love me, I'm so lucky to have you. ❤️",
    "I love how gentle you are with me. Whenever I'm jelly or anxious, you're so soft and patient with me until I feel okay again 🥺❤️",
    "You're always there to support me through every hard decision. You give me so much strength just by being beside me ❤️",
    "For 5 years, you've always been my safe space. I can tell you anything without ever feeling judged, and you're always there to listen ❤️",
    "I love how thoughtful you are. You always remember the little things about me, and you make me feel so special and loved ❤️",
    "You're naturally sooo beautiful. Even when you think your makeup is a lil off or your lashes are too short, you still light up every room you walk into ❤️",
    "I admire how hardworking you are. Even when you're exhausted, you still give everything to your goals and the people you love. Nothing can stop you ❤️",
    "You make me laugh sooo much. Your jokes, energy, and personality make being around you so fun, and you can make anyone smile in seconds ❤️",
    "I love your energyyy. You'll randomly sing, dance, jump up, and burst into energy, and I can't help but match it every timeee, you're my happiness ❤️",
    "You're sooo smart in every way. Academically, emotionally, AND street smart mi amor. You understand things and people so naturally, and I'm always impressed by you ❤️",
    "You're genuinely so talented. From how amazing you are with babies, to your nails, makeup, and hair.. you put so much love into everything you do and I can't help but admire you ❤️",
    "I love your cute shy sideee. You'll get nervyyy, look awayyy, or start playing with something, and I get to see the sweet soft side you don't show everyone 🥺❤️",
    "I love how tough you are. If somebody annoys you, you're not scared to say it straightttt to their face. I love my independent woman ❤️",
    "Under that adorable gangsta girl is the warmest heart. You're such a huge sweetheart, and you deserve to always be loved, cared for, and treated amazingly ❤️",

    "Since we met, you've only ever been the brightest part of my day baby ❤️",
    "Being your best friend and your lover has taught me things only you could ever show me ❤️",
    "You taught me how true love feels baby. I never knew I could love and desire someone this deeply until you ❤️",
    "Every warm feeling I get in my chest when I see you is because of you, my one of a kind Kattita ❤️",
    "I'll never be able to thank God enough for giving me the best gift I've ever received.. you and your love ❤️",
    "You're my miracle from heaven, baby. My wish upon a shooting star and my prayers answered ❤️",
    "You're the love of my life, Bellita. Nothing will ever change that ❤️",
    "At your lowest, I'll always be beside you to pick you up. At your highest, I'll be right there telling you how proud I am ❤️",
    "I promise I'll always give you the love and respect you deserve, my angel ❤️",
    "I love you wifey. I love you my best friend. I love you Bellita. ❤️",
    "I love you beyond the end of time. That's a promise ❤️",
    "I waited almost half a decade for your heart, and I'd wait infinitely more for you all over again ❤️",
    "You're not only the girl I love, you're my best friend too. That's one of my favorite things about us ❤️",
    "No matter what kind of day you're having, remember your Johnny is always right here beside you ❤️",
    "You are one of a kind to me, Kattita. There will never be another you ❤️",
    "Of everything life could've given me, getting to love you is still my favorite gift ❤️",
    "I hope you never forget how proud I am of you, baby. In the little things, the big things, and everything in between ❤️",
    "Your love is one of the most precious things I've ever been trusted with, and I'll always treasure it ❤️",
    "If I had to wait all those years for you again knowing where we'd end up, I'd do it every single time ❤️",

    "God FORBID I have the cutest girlfriend ever 🙄❤️",
    "SLAYYYYY GO GIRL 💅 you successfully collected cookies in such a cute as fuck wayyy",
    "CLOCK ITTTT 🤏 another day of being my pretty girl ❤️",
    "Line by line. Bar by bar. Cookie by cookie. Let's make babie- ahem this is in public oopsies ❤️",
    "Omg when I TELL YOUUUU this girl is BEAUTIFULL ❤️ yes I'm talking about YOU baby",
    "This is music to my latino ears... my wifey collected her daily cookies 🕺❤️",
    "Daily reminder that you're my pretty pretty pretty babygirl. MHM I needed to say pretty three times.",
    "WOAH WOAH BREAKING NEWS 🚨 Bella is THE MOST ADOOOORABLE AND CUTEST LIL BABY IN THE WORRRRRRRRLLLDDD! (I love her sm omfg)",
    "Johnny has reviewed the evidence and concluded that you're cute as fuck. Decision is final.",
    "I asked Johnny who the prettiest girl in the world is.. and this mf just sent me a pic of you.",
    "Your daily cookies have been approved by your nerdy hot asf boyfriend & husband ❤️",
    "Heyy cutiepie <3 I hid messages inside a Discord bot because ykk saying I love you 900 times a day wasn't enoughhhh",
    "u.u 👉👈 hewwo Bellita... Johnny says ur pwetty... uwu... okay I'm never typing that again ahem.",
    "O_o omg... is that... the love of my life collecting her daily cookies??? UWU- omfg why did I type this.. wtv you're smilingggg so it's worth itttt",
    "You may call it rorox, but I still call you my baaaaby ❤️",
    "ykk I would buy you an iced caramel macchiato rn if CookieBot could automatically do ittt everytime you run this cmd ☕❤️",
    "Babyyy your daily reward should've been chocola- ahem peanut M&M's but ykkk CookieBot only has cookies 😔",
    "Ritz + Nutella + you + me = literally all we need lowkeyyy ❤️",
    "I hope your day has Starbucks, stuffies, good music, and me annoying you baby ❤️",
    "🦋 A butterfly delivered your daily cookies today.. YAYAYAYAYAYAYYY WOOOOOOO (you're so cute btw) 🥹❤️",
    "🐸 CookieBot tried hiring a frog to deliver this message. I sent him to federal prison ASAP. You're welcome babyyy",
    "I was gonna get you seafood with your daily but I didn't wanna risk you throwing me outside the window or wtvvv",
    "Bella's daily checklist: 💜 be pretty 🦋 love butterflies ❤️ be obsessed with Johnny (thisss MOST)",
    "I found a big black lifted truck outside. CMON BABY VAMOS we're going to starbucks 🛻❤️",
    "CookieBot played reggaeton and Bella spawned in instantly. Scientists remain confused and are trying to investigate.",
    "Albanian drill started playing... everybody RUN. Bella is gonna pull out her thug side again (she's so cute when she does it btw) ❤️",
    "God FORBID my girlfriend is a certified THUG 🙄 (mhm go ahead and say BAR BY BAR LINE BY BAR you CUTIIIIIE)",
    "is it weird that I love you even deeper when you like... threaten people with a pan.. idk it's kinda hot babe ❤️",
    "🧸 Our babies held a meeting and unanimously agreed that you're the best mommy. But ykk I'm a close CLOSE 2nd so careful baby",
    "ykk you could tell me the most random story in the world and I'd still sit there like 🥹 because I'm obessed with everything about you.",
    "You being nervyyy and looking away and pushing my face away when you're shy is STILL one of the cutest things ever btw.",
    "heyy my beautiful wifeyyyyy ❤️ just wanted to interrupt you for a sec... to say I LOVE YOUUUUU.",

    "MWAH MWAH MWAH MWHAMWAHMMAWH MWAHHHHHH MWAH MWAH MWAH MMMWAH MWAHMWMAHMWAH MWAH 💋💋💋💋💋💋💋💋 BOOO SURPRISE KISS, ahem I mean here's your cookies bebe",
    "Come hereeeee lemme kiss your pretty faceeee 😚❤️ CookieBot can waitttt",
    "If you're reading this, you legally owe Johnny one- I mean fifty kisses. Sorry baby I don't make the rules (yes I doooo)",
    "lowkeyyy imagine having a husband nerdy enough to code you into his Discord bot 😭 like yk... couldn't be you... oh wait.. WAIT AM I A NERD BABE?",
    "You thought you were just running `.daily` LMAOOOO GET LOVED AND KISSED LOSERRRR LLLLLLL 🫵😂❤️",
]

async def send_dev_alert(ctx, userData, userID):
    # respect per-guild subscription toggle
    u = userData["users"][userID]
    if not bool(u.get("DevAlerts", False)):
        return

    latest_alert = get_latest_active_alert()
    if not latest_alert:
        return

    current_id = latest_alert.get("date")
    state = u.get("AlertState", {})
    read_id = state.get("readId")
    ping_for = state.get("pingForId")
    ping_count = int(state.get("pingCount", 0))

    # if new alert, reset ping tracking
    if ping_for != current_id:
        ping_for = current_id
        ping_count = 0

    # If unread for this alert and under 2 reminders
    if read_id != current_id and ping_count < 2:
        await ctx.send("Hey, <@!" + str(ctx.author.id) + ">! There's a 🔔 **New Developer Alert!** Run `.alert` to view it.")
        ping_count += 1

    u["AlertState"] = {
        "readId": read_id,
        "pingForId": ping_for,
        "pingCount": ping_count
    }

@bot.command()
async def daily(ctx):
    try:
        userID = str(ctx.author.id)
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)
        user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))

        ## this block fetches user data from the database
        userData = await lookup_database(userID, guildID) 
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)


        dbUser = userData["users"][userID]

        userCookies = dbUser.get("Cookies", 0)
        userStreaks = dbUser.get("Streaks", 0)
        userDailyMultiplier = dbUser.get("DailyMultiplier", 0)

        userMultExpire = dbUser.get("DailyMultExpire")
        if userMultExpire is None:
            userMultExpire = datetime.now() - timedelta(days=1)

        userDailyExpire = dbUser.get("DailyExpire")
        if userDailyExpire is None:
            userDailyExpire = datetime.now() - timedelta(days=1)
        

        ## this checks if they have a cooldown
        if datetime.now() < userDailyExpire:
            timer = int(userDailyExpire.timestamp())

            cooldown_embed = discord.Embed(
                description = "You can collect your cookies again " + "<t:" + str(timer) + ":R>",
                color = 0x992d22
            )
            cooldown_embed.set_footer(
                text = "Tomorrow at " + userDailyExpire.strftime("%I:%M %p")
            )   
            cooldown_embed.set_author(name = "Not yet " + str(user.display_name) + "!", icon_url = user.display_avatar)
            await ctx.send(embed=cooldown_embed)
            return

        ## calculate and give daily cookies
        BaseCookies = 15
        Multiplier = 0
        StreakCookies = int((userStreaks/14) * 1.5)

        if userDailyMultiplier > 0:
            if userMultExpire and userMultExpire >= datetime.now():
                Multiplier = userDailyMultiplier
            else:
                userDailyMultiplier = 0
        
        Temp = (BaseCookies + StreakCookies) * Multiplier
        TotalCookies = BaseCookies + StreakCookies + Temp
        userCookies += TotalCookies

        ## this block updates their streak and daily cooldown
        if datetime.now() > userDailyExpire + timedelta(hours = 24): ## reset cooldown if 24 hours past expiration
            userStreaks = 1
        else:
            userStreaks += 1
        
        userDailyExpire = datetime.now() + timedelta(hours = 23)

        ## send the final embed
        dailyembed = discord.Embed(
            description = "You have collected your daily ``" + str(TotalCookies) + "`` cookies!" + "\n" + 
            "You now have a streak of ``" + str(userStreaks) + "``.", 
            color = 0x2ecc71,
            timestamp = userDailyExpire
            )

        dailyembed.set_author(name = "Daily Cookies - " + str(user.display_name), icon_url = user.display_avatar)
        dailyembed.set_footer(text = "You can collect again in 23 hours.")
        await ctx.send(embed=dailyembed)

        ## special Bella daily love message
        if ctx.author.id == BELLA_ID:
            love_message = random.choice(BELLA_DAILY_MESSAGES)

            bella_embed = discord.Embed(
                title="💌 A little message from your Johnny",
                description=love_message,
                color=0x9B59B6
            )

            bella_embed.set_footer(text="— Johnny, your nerd, lover, and best friend 💜")

            await ctx.send(embed=bella_embed)

        await send_dev_alert(ctx, userData, userID) ## check for dev alert and ping if unread

        ## update the database
        userData["users"][userID]["Cookies"] = userCookies
        userData["users"][userID]["Streaks"] = userStreaks
        userData["users"][userID]["DailyMultiplier"] = userDailyMultiplier
        userData["users"][userID]["DailyMultExpire"] = userMultExpire
        userData["users"][userID]["DailyExpire"] = userDailyExpire
        
        await update_database(userID, guildID, userData["users"][userID])
        
    except Exception as Error:
        await ctx.send(Error)