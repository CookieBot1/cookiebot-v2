from resources.mrcookie import instance as bot
from resources.checks import update_counter, lookup_counter, new_counter
import discord

@bot.command()
async def setcounter(ctx):
    guildID = ctx.guild.id

    counterData = await lookup_counter(guildID)
    if counterData is False:
        await new_counter(guildID)
        counterData = await lookup_counter(guildID)

    # resets data to default incase they run .setcounter after already having an existing counting channel
    await update_counter(guildID, "Channel", ctx.channel.id)
    await update_counter(guildID, "Counter", 0)
    await update_counter(guildID, "lastUser", 0)


    # Ask the question once
    prompt = await ctx.send(
        "Enable math expressions in the counting channel? "
        "(example: `1+1` counts as `2`)\n"
        "Reply with `yes` or `no` within **30 seconds**."
    )

    def check(m: discord.Message) -> bool:
        return (
            m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id
            and m.guild is not None
        )

    allow_math = False
    try:
        reply: discord.Message = await bot.wait_for("message", timeout=30.0, check=check)
        content = reply.content.strip().lower()

        if content in ("yes", "y", "true", "on", "enable", "enabled"):
            allow_math = True
        elif content in ("no", "n", "false", "off", "disable", "disabled"):
            allow_math = False
        else:
            # invalid response -> keep default (False)
            await ctx.send("Didn’t understand that — leaving math expressions **disabled**.")
    except TimeoutError:
        await ctx.send("No response — leaving math expressions **disabled**.")

    await update_counter(guildID, "AllowMath", allow_math)


    counter_embed = discord.Embed(
        title = "✅ Counter Channel Set!",
        description = "Want to change your counter channel? Run ``.setcounter`` again in that channel.",
        color = 0x2ecc71,
        )

    counter_embed.set_footer(text = 'To find out how counting works, run ".help counter"')
    await ctx.send(embed=counter_embed)