from resources.mrcookie import instance as bot

@bot.event
async def on_command_error(ctx, error):
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)

@bot.tree.error
async def on_app_command_error(interaction, error):
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)