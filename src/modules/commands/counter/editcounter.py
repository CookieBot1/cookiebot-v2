from resources.mrcookie import instance as bot
from resources.checks import lookup_counter, new_counter, update_counter
from resources.helpers import ask_yes_no, ask_role, make_check, SetupCancelled, handle_cancel
import discord
import asyncio


async def announce_counter_change(guild: discord.Guild, channel_id: int, embed: discord.Embed):
    channel = guild.get_channel(channel_id)
    if channel is None:
        try:
            channel = await guild.fetch_channel(channel_id)
        except Exception:
            return
    try:
        await channel.send(embed=embed)
    except Exception:
        pass

@bot.command(aliases=["counteredit", "editcount", "countedit"])
async def editcounter(ctx, option: str = ""):
    cleanup: list[discord.Message] = []
    try:
        if ctx.guild is None:
            return await ctx.reply("This command only works in servers!", delete_after=5)

        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.reply("You can't use this command.", delete_after=5)

        option = (option or "").strip().lower()
        aliases = {
            "channels": "channel",
            "roles": "role",
            "badrole": "role",
            "fails": "role",
            "failrole": "role",
            "expressions": "math",
        }
        option = aliases.get(option, option)

        if option not in {"channel", "role", "math"}:
            return await ctx.reply(
                "Usage:\n"
                "• ``.editcounter channel``\n"
                "• ``.editcounter role``\n"
                "• ``.editcounter math``",
                delete_after=10
            )

        # check if data is in DB
        guildID = ctx.guild.id
        counterData = await lookup_counter(guildID)
        if counterData is False:
            await new_counter(guildID)
            counterData = await lookup_counter(guildID)

        old_channel_id = int(counterData["settings"]["counter"].get("Channel", 0))
        if old_channel_id == 0:
            return await ctx.reply("No counting channel is set yet. Run `.setcounter` first.", delete_after=8)


        # editing the channel option ---
        if option == "channel":
            m = await ctx.send(
                "Which channel should be the new counting channel?\n"
                "Mention it (ex: #counting) or paste the channel ID. Type `cancel` to stop."
            )
            cleanup.append(m)

            check = make_check(ctx)
            msg: discord.Message = await bot.wait_for("message", timeout=45.0, check=check)
            cleanup.append(msg)
            await handle_cancel(msg)

            new_channel = None

            if msg.channel_mentions:
                new_channel = msg.channel_mentions[0]
            else:
                raw = msg.content.strip()
                if raw.isdigit():
                    new_channel = ctx.guild.get_channel(int(raw))
                    if new_channel is None:
                        try:
                            new_channel = await ctx.guild.fetch_channel(int(raw))
                        except Exception:
                            new_channel = None

            if new_channel is None or not isinstance(new_channel, discord.TextChannel):
                return await ctx.send("Couldn’t find that text channel. No changes made.")

            # update DB
            await update_counter(guildID, "Channel", new_channel.id)

            # announce in OLD channel, then NEW channel (so everyone sees it)
            embed = discord.Embed(
                title="🔧 Counting Channel Updated",
                description=f"The counting channel has been changed to {new_channel.mention}.",
                color=0x9b59b6
            )
            embed.set_footer(text=f"Changed by {ctx.author} • Use .editcounter to modify settings")

            await announce_counter_change(ctx.guild, old_channel_id, embed)
            if new_channel.id != old_channel_id:
                await announce_counter_change(ctx.guild, new_channel.id, embed)

            return await ctx.reply(f"✅ Updated counting channel to {new_channel.mention}.")


        # editing the math option ---
        if option == "math":
            current = bool(counterData["settings"]["counter"].get("AllowMath", False))

            m = await ctx.send(
                f"Math expressions are currently **{'enabled' if current else 'disabled'}**.\n"
                "Would you like to enable math expressions? Type `yes` or `no`. Type `cancel` to stop."
            )
            cleanup.append(m)

            allow_math = await ask_yes_no(ctx, "", default=current, cleanup=cleanup)  # question already sent above
            await update_counter(guildID, "AllowMath", allow_math)

            embed = discord.Embed(
                title="🧮 Counting Math Setting Updated",
                description=f"Math expressions are now **{'enabled' if allow_math else 'disabled'}**.",
                color=0x9b59b6
            )
            embed.set_footer(text=f"Changed by {ctx.author}")

            await announce_counter_change(ctx.guild, old_channel_id, embed)
            return await ctx.reply(f"✅ Math is now **{'enabled' if allow_math else 'disabled'}**.")


        # editing the bad role and fails to get the role ---
        if option == "role":
            enabled = bool(counterData["settings"]["counter"].get("badCounterRoleEnabled", False))
            current_role_id = int(counterData["settings"]["counter"].get("badCounterRoleID", 0))
            current_fails = int(counterData["settings"]["counter"].get("badCounterRoleFails", 0))

            role_obj = ctx.guild.get_role(current_role_id) if current_role_id else None

            m = await ctx.send(
                "Let’s edit the bad counter role settings.\n"
                f"Currently: **{'enabled' if enabled else 'disabled'}**"
                + (f", Role: {role_obj.mention}" if role_obj else ", Role: *(none)*")
                + f", Fails: **{current_fails if current_fails else 'none'}**\n"
                "Keep enabled? Type `yes` or `no`. Type `cancel` to stop."
            )
            cleanup.append(m)

            enabled_new = await ask_yes_no(ctx, "", default=enabled, cleanup=cleanup)

            role_id_new = current_role_id
            fails_new = current_fails

            if enabled_new:
                role = await ask_role(ctx, "Which role should be used? Mention it, send ID, or exact name. Type `cancel` to stop.", cleanup=cleanup)
                if role is None:
                    await ctx.send("Couldn’t find that role. No changes made.")
                    return
                role_id_new = role.id

                # reuse your existing ask_number_or_none
                n = await ask_number_or_none(ctx, "After how many fails should the role be given? Send a number or `none`. Type `cancel` to stop.", cleanup=cleanup)
                fails_new = 0 if n is None else int(n)
            else:
                role_id_new = 0
                fails_new = 0

            await update_counter(guildID, "badCounterRoleEnabled", enabled_new)
            await update_counter(guildID, "badCounterRoleID", role_id_new)
            await update_counter(guildID, "badCounterRoleFails", fails_new)

            role_obj_new = ctx.guild.get_role(role_id_new) if role_id_new else None

            desc = f"Bad counter role is now **{'enabled' if enabled_new else 'disabled'}**."
            if enabled_new:
                desc += f"\nRole: {role_obj_new.mention if role_obj_new else f'`{role_id_new}`'}"
                desc += f"\nFails threshold: **{fails_new if fails_new else 'none'}**"

            embed = discord.Embed(
                title="🎭 Bad Counter Role Settings Updated",
                description=desc,
                color=0xe67e22
            )
            embed.set_footer(text=f"Changed by {ctx.author}")

            await announce_counter_change(ctx.guild, old_channel_id, embed)
            return await ctx.reply("✅ Updated bad counter role settings.")

    except SetupCancelled:
        await ctx.send("❌ Edit cancelled.")
        return

    except asyncio.TimeoutError:
        await ctx.send("⏰ Timed out. No changes made.")
        return

    except Exception as error:
        await ctx.send(error)

    finally:
        for m in cleanup:
            try:
                await m.delete()
                await asyncio.sleep(0.4)
            except Exception:
                pass
