# Primarily copied from Nub from here -
# https://github.com/One-Nub/helper-bot/blob/main/src/modules/events/on_interaction.py

import logging

import discord
from discord import ComponentType, Interaction, InteractionType

from resources.mrcookie import instance as bot


@bot.event
async def on_interaction(interaction: Interaction):
    # Handle interactions with custom handler

    match interaction.type:
        case InteractionType.component:
            if not interaction.data:
                logging.error("Discord failed at it's job - no interaction data on component interaction")
                return

            # Only really doing this cuz discord.py buries the actual type and these are basically dicts to us anyway.
            # mcd = MessageComponentData(**interaction.data)  # type:ignore[reportArgumentType]
            inter_data = interaction.data
            component_type = inter_data.get("component_type")

            match component_type:
                case ComponentType.button.value:
                    for name, handler in bot.button_handlers.items():
                        if not inter_data["custom_id"].startswith(name):  # type: ignore
                            continue

                        await handler(
                            interaction,
                            (
                                discord.ui.View.from_message(interaction.message)
                                if interaction.message
                                else None
                            ),
                        )

                case (
                    ComponentType.string_select.value
                    | ComponentType.user_select.value
                    | ComponentType.role_select.value
                    | ComponentType.mentionable_select.value
                    | ComponentType.channel_select.value
                ):
                    # If custom handlers for select menus are added.
                    pass

        case InteractionType.application_command:
            pass

        case InteractionType.autocomplete:
            pass

        case InteractionType.modal_submit:
            pass