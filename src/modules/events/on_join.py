from resources.mrcookie import instance as bot

from resources.checks import new_counter, lookup_counter

@bot.event
async def on_guild_join(guild):
    if await lookup_counter(guild.id) == False:
        await new_counter(guild.id)
  
    