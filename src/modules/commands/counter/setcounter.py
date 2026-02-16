from resources.mrcookie import instance as bot
from resources.checks import update_counter, lookup_counter, new_counter
from resources.helpers import ask_yes_no, ask_role, make_check, SetupCancelled, handle_cancel
import discord
from discord.ext import commands
import asyncio


async def ask_number_or_none(ctx, question: str, *, timeout: float = 30.0, cleanup=None):
    qmsg = await ctx.send(question + "Type `cancel` to stop setup.")
    if cleanup is not None:
        cleanup.append(qmsg)

    def check(m: discord.Message) -> bool:
        return (
            m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id
            and m.guild is not None
        )

    try:
        msg: discord.Message = await bot.wait_for("message", timeout=timeout, check=check)
        if cleanup is not None:
            cleanup.append(msg)

        await handle_cancel(msg)

        content = msg.content.strip().lower()

        if content in {"none", "off", "disable", "disabled"}:
            return None

        try:
            n = int(content)
            if n < 1:
                await ctx.send("Must be 1 or higher. No number set.")
                return None
            return n
        except ValueError:
            await ctx.send("Not a number. No number set.")
            return None

    except asyncio.TimeoutError:
        await ctx.send("No response. No number set.")
        return None

@bot.command()
async def setcounter(ctx):
    try:
        cleanup: list[discord.Message] = []
        guildID = ctx.guild.id

        if ctx.guild is None:
            return await ctx.message.reply(content="This commands only works in servers!", delete_after=5)

        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.message.reply(content="You can't use this command.", delete_after=5)

        counterData = await lookup_counter(guildID)
        if counterData is False:
            await new_counter(guildID)
            counterData = await lookup_counter(guildID)

        # Code shouldn't continue if a counter channel is already set
        if counterData["settings"]["counter"]["Channel"] != 0:
            raise Exception("🔴 **Counter channel already set!**" + '\n' + "Reset the counter first with ``.resetcounter`` before setting a new one.")

        # Ask the question once
        prompt = await ctx.send(
            "Enable math expressions in the counting channel? "
            "(example: `1+1` counts as `2`)\n"
            "Reply with `yes` or `no` within **30 seconds**. Type `cancel` to stop setup."
        )
        cleanup.append(prompt)

        allow_math = False
        try:
            check = make_check(ctx)
            reply: discord.Message = await bot.wait_for("message", timeout=30.0, check=check)
            cleanup.append(reply)

            await handle_cancel(reply)

            content = reply.content.strip().lower()
            if content in ("yes", "y", "true", "on", "enable", "enabled"):
                allow_math = True
            elif content in ("no", "n", "false", "off", "disable", "disabled"):
                allow_math = False
            else:
                await ctx.send("Invalid response — leaving math expressions **disabled**.")
        except asyncio.TimeoutError:
            await ctx.send("No response — leaving math expressions **disabled**.")

        await update_counter(guildID, "AllowMath", allow_math)


        # Code now for the bad counter role
        enable_bad_role = await ask_yes_no(ctx, "Would you like to enable the bad counter role? Type ``yes`` or ``no``.", default=False, cleanup=cleanup)

        bad_role_id = 0
        give_on_delete = False
        fail_threshold = None

        if enable_bad_role:
            role = await ask_role(ctx, "Which role should be used? Mention it, send ID, or exact name.", cleanup=cleanup)
            if role is None:
                await ctx.send("Skipping bad counter role setup.")
                enable_bad_role = False
            else:
                bad_role_id = role.id
                give_on_delete = await ask_yes_no(ctx, "Should the role be given if someone deletes their counting attempt? Type ``yes`` or ``no``.", default=True, cleanup=cleanup)
                fail_threshold = await ask_number_or_none(ctx, "After how many fails should the role be given? Send a number or ``none``.", cleanup=cleanup)

        await update_counter(guildID, "badCounterRoleEnabled", enable_bad_role)
        await update_counter(guildID, "badCounterRoleID", bad_role_id)
        await update_counter(guildID, "badCounterRoleDelete", give_on_delete)
        await update_counter(guildID, "badCounterRoleFails", fail_threshold if fail_threshold is not None else 0)

        await update_counter(guildID, "Channel", ctx.channel.id)

        counter_embed = discord.Embed(
            title = "✅ Counter Channel Set!",
            description = "Want to change your counter channel? Run ``.setcounter`` again in that channel.",
            color = 0x2ecc71,
            )

        counter_embed.set_footer(text = 'To find out how counting works, run ".help counter"')
        final_msg = await ctx.send(embed=counter_embed)

        await asyncio.sleep(8)
        # delete all setup messages (bot prompts + user replies)
        for m in cleanup:
            try:
                await m.delete()
                await asyncio.sleep(0.4)  # ← THIS is the rate-limit fix
            except (discord.Forbidden, discord.NotFound):
                pass
            except Exception:
                pass

    except SetupCancelled:
        await ctx.send("❌ Setup cancelled.")
        return
    except Exception as Error:
        await ctx.send(Error)