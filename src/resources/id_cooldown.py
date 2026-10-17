import asyncio

class IDCooldown:
    """Background handling of a cooldown"""

    def __init__(self, cooldown_duration: int = 10) -> None:
        self.cooldown = cooldown_duration
        self.ids: set[int] = set()

    async def _add_id(self, identifier: int):
        """Adds user to be on cooldown, then removes after self.response_cooldown duration."""
        self.ids.add(identifier)
        await asyncio.sleep(self.cooldown)
        self.ids.discard(identifier)

    def check_for_id(self, identifier: int) -> bool:
        """See if an id is on cooldown (True) or not (False). Automatically applies cooldown when False."""
        if not identifier in self.ids:
            asyncio.create_task(self._add_id(identifier=identifier))
            return False
        else:
            return True
