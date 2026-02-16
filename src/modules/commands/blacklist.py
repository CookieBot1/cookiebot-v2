import time
from discord.ext import commands 
from resources.mrcookie import instance as bot 
from resources.checks import is_admin, validate_user, is_blacklisted

@bot.command()
async def blacklist(ctx, temp_ID = "0"):
    try:
        if await is_admin(ctx.author.id) == False:
            raise Exception("You don't have permission to run this command.")
        
        userID = await validate_user(temp_ID) 
        if userID == None:
            raise Exception("Invalid user.")
            
        if ctx.author.id == int(userID):
            raise Exception("You can't blacklist yourself.")
            
        if await is_blacklisted(userID) == True:
            raise Exception("User is already blacklisted.")
        
        # writing in DB
        await bot.db.add_blacklist({"_id": str(userID)})

        # cache update
        bot.blacklist_cache[userID] = (True, time.time())

        await ctx.send("Blacklisted " + str(userID))

    except Exception as Error:
        await ctx.send(Error)
