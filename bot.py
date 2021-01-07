import asyncio
import json
import os
from datetime import datetime

import asyncpg
import discord
from discord.ext import commands


class FlandersBOT(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix=self.get_default_prefixes, case_insensitive=True, intents=intents)

        # Remove default help command
        self.remove_command('help')

        # Default configuration with cache
        self.cached_screencaps = {}
        self.reminders = []
        self.uptime = datetime.utcnow()
        self.db = None
        self.db_conn = None
        self.logging = None

        # Discord channel id used for all error logging
        self.LOGGING_CHANNEL = 415700137302818836

        # Load config file
        with open('settings/config.json', 'r') as config_file:
            self.config = json.load(config_file)

        # Configure debug mode
        self.debug_mode = self.config['debug_mode']

    # Default get prefixes method, is replaced once prefixes cog loads (custom guild prefixes)
    async def get_default_prefixes(self, bot, message):
        default_prefixes = ['ned', 'diddly', 'doodly']
        return commands.when_mentioned_or(*default_prefixes)(self, message)


# Runs FlandersBOT
def run_bot():
    loop = asyncio.get_event_loop()

    # Load config file for token
    with open('settings/config.json', 'r') as conf:
        config = json.load(conf)

    # Establish connection to PostgreSQL database
    try:
        db = loop.run_until_complete(asyncpg.create_pool(**config['db_credentials']))

    except Exception as e:
        exc = f'{type(e).__name__}: {e}'
        print(f'Failed to connect PostgreSQL. Terminating.\n{exc}')
        return

    # Requires members intents for leaderboard username display
    intents = discord.Intents.default()
    intents.members = True

    # Initialise bot with db connection
    bot = FlandersBOT(intents)
    bot.db = db

    # Load all bot extensions from cogs folder
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            extension = file[:-3]

            try:
                bot.load_extension(f"cogs.{extension}")

            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                print(f'Failed to load extension {extension}\n{exc}')

    # Run FlandersBOT
    bot.run(config['bot_token'])


run_bot()
