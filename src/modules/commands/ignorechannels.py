import discord
from discord.ext import commands

from resources.checks import lookup_server, new_server, update_ignored_channels
from resources.mrcookie import instance as bot


## this command disables/enables drops
@bot.command(aliases=["ignorechannels"])
async def ignorechannel(ctx, channel: discord.TextChannel | None = None):
    try:
        if ctx.guild is None:
            return await ctx.message.reply(content="This commands only works in servers!", delete_after=5)

        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.message.reply(content="You can't use this command.", delete_after=5)

        channel = channel or ctx.channel
        channel_id = channel.id
        guild_id = ctx.guild.id

        server_data = await lookup_server(guild_id)
        if server_data is False:
            await new_server(guild_id)
            server_data = await lookup_server(guild_id)

        ignored_channels: list = server_data["settings"]["server"].get("IgnoredChannels", [])

        ignored = channel_id in ignored_channels
        if ignored:
            ignored_channels.remove(channel_id)
        else:
            ignored_channels.append(channel_id)

        ignored = not ignored

        reply_message = (
            f":loudspeaker: {channel.mention} will now be ignored!"
            if ignored
            else f":mute: {channel.mention} will no longer be ignored!"
        )

        await update_ignored_channels(guild_id, ignored_channels)

        await ctx.reply(reply_message)

    except Exception as error:
        await ctx.send(error)