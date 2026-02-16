import time
from discord.ext import commands 
from resources.mrcookie import instance as bot 
from resources.checks import is_admin, validate_user, is_blacklisted

@bot.command()
async def unblacklist(ctx, temp_ID = "0"):
    try:
        if await is_admin(ctx.author.id) == False:
            raise Exception("You don't have permission to run this command.")
        
        userID = await validate_user(temp_ID) 
        if userID == None:
            raise Exception("Invalid user.")
                
        if await is_blacklisted(userID) == False:
            raise Exception("User is not blacklisted.")
        
        # writing in db
        await bot.db.del_blacklist({"_id": str(userID)})

        # cache update 
        bot.blacklist_cache[userID] = (False, time.time())

        await ctx.send("Unblacklisted " + str(userID))

    except Exception as Error:
        await ctx.send(Error)
