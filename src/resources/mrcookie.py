import importlib
import logging

import certifi
import discord
from discord.ext import commands
from motor import motor_asyncio

instance: "MrCookie" = None
logger = logging.getLogger()


class MrCookie(commands.Bot):
    def __init__(
        self,
        command_prefix: str,
        mongodb_url: str,
        intents: discord.Intents,
    ) -> None:

        global instance

        super().__init__(
            command_prefix,
            intents=intents,
        )

        if mongodb_url:
            self.db = MongoDB(mongodb_url)
        else:
            logger.error("NO MONGODB URL WAS FOUND.")

        self.button_handlers = {}

        instance = self

    @staticmethod
    def load_module(import_name: str) -> None:
        importlib.import_module(import_name)

    def add_button_handler(self, custom_id_prefix: str):
        def inner(func):
            self.button_handlers[custom_id_prefix] = func

        return inner


class MongoDB:
    def __init__(self, connection_string: str) -> None:
        """Initializes the MongoDB connection.

        Args:
            connection_string (str): The URL to connect to MongoDB with.
        """
        logger.info("Connecting to MongoDB.")
        self.client = motor_asyncio.AsyncIOMotorClient(connection_string, tlsCAFile=certifi.where())
        self.db = self.client["mrcookie"]
        logger.info("MongoDB initialized.")

    # blacklist collection
    async def find_blacklist(self, doc):
        document = await self.db.blacklist_users.find_one(doc)
        return document

    async def add_blacklist(self, doc):
        await self.db.blacklist_users.insert_one(doc)

    async def del_blacklist(self, doc):
        await self.db.blacklist_users.delete_one(doc)

    # master_data collection
    async def find_user(self, doc):
        document = await self.db.master_data.find_one(doc)
        return document

    async def update_user(self, dict, set):
        await self.db.master_data.update_one(dict, set, upsert=True)

    async def get_guild_users(self, guildID: int):
        return await self.db.master_data.find_one({"_id": str(guildID)}, projection={"users": 1})
    
    async def get_guilds(self):
        cursor = self.db.master_data.find(projection={"_id": 1})
        document = await cursor.to_list(None)
        return document
