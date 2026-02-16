import discord
from discord.ext import commands

from resources.checks import lookup_server, new_server, update_ignored_drops
from resources.mrcookie import instance as bot


## this command disables/enables drops
@bot.command(aliases=["disabledrops"])
async def ignoredrops(ctx: commands.Context, channel: discord.TextChannel | None = None):
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

        ignored_drop_data: list = server_data["settings"]["server"].get("IgnoredChannelDrops", [])

        ignored = channel_id in ignored_drop_data
        if ignored:
            ignored_drop_data.remove(channel_id)
        else:
            ignored_drop_data.append(channel_id)

        ignored = not ignored

        reply_message = (
            f":mute: {channel.mention} will no longer have cookies drop!"
            if ignored
            else f":loudspeaker: Cookies will now drop in {channel.mention}!"
        )

        await update_ignored_drops(guild_id, ignored_drop_data)

        await ctx.reply(reply_message)

    except Exception as error:
        await ctx.send(error)