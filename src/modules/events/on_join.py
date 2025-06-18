from resources.mrcookie import instance as bot

from resources.checks import new_counter, new_server, lookup_counter, lookup_server

@bot.event
async def on_guild_join(guild):
    if await lookup_server(guild.id) == False:
        await new_server(guild.id)
  
    