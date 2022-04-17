import json

import asyncio

import aiohttp
import discord
from discord.ext import commands
from tabulate import tabulate


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Change the bot's avatar
    @commands.command(hidden=True)
    @commands.is_owner()
    async def avatar(self, ctx, avatar_url):
        async with aiohttp.ClientSession() as aioClient:
            async with aioClient.get(avatar_url) as resp:
                new_avatar = await resp.read()
                await self.bot.user.edit(avatar=new_avatar)
                await ctx.send('Avatar changed!')

    # Get the number of all the commands executed
    @commands.command(hidden=True)
    @commands.is_owner()
    async def commandstats(self, ctx, *, modifier: str = None):
        # Get command counts ordered alphabetically
        if modifier is None or modifier != 'count':
            query = '''SELECT command, COUNT(command) AS command_count FROM command_history
                       WHERE failed = false
                       GROUP BY command
                       ORDER BY command
                    '''
            rows = await self.bot.db.fetch(query)

        # Get command counts ordered by command count
        else:
            query = '''SELECT command, COUNT(command) AS command_count FROM command_history
                       WHERE failed = false
                       GROUP BY command
                       ORDER BY command_count DESC
                    '''
            rows = await self.bot.db.fetch(query)

        # Display each command stats on separate line and format using tabulate
        command_data = map(lambda row: [row['command'], row['command_count']], rows)
        message = tabulate(command_data, headers=['Command Name', 'Count'], tablefmt='presto', colalign=('right',))
        await ctx.send(f'```{message}```')

    # Get the number of commands executed in last month that weren't in support server
    @commands.command(hidden=True)
    @commands.is_owner()
    async def newstats(self, ctx):
        # Get command counts ordered alphabetically
        query = '''SELECT command, COUNT(command) AS command_count FROM command_history
                   WHERE failed = false AND guild_id != 403154226790006784 AND used_at BETWEEN (
                       NOW() AT time zone 'utc'
                   ) - INTERVAL '30 DAYS' AND (
                       NOW() AT time zone 'utc'
                   ) 
                   GROUP BY command
                   ORDER BY command
                '''

        rows = await self.bot.db.fetch(query)

        # Display each command stats on separate line and format using tabulate
        command_data = map(lambda row: [row['command'], row['command_count']], rows)
        message = tabulate(command_data, headers=['Command Name', 'Count'], tablefmt='presto', colalign=('right',))
        await ctx.send(f'```{message}```')

    # Loads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def load(self, ctx, *, cog: str):
        try:
            await self.bot.load_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.send(e)
        else:
            await ctx.message.add_reaction('✅')

    # Unloads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def unload(self, ctx, *, cog: str):
        try:
            await self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.send(e)
        else:
            await ctx.message.add_reaction('✅')

    # Reloads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def reload(self, ctx, *, cog: str):
        try:
            await self.bot.unload_extension(cog)
            await self.bot.load_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.send(e)
        else:
            await ctx.message.add_reaction('✅')

    # Manually syncs commands to the guild, or globally if followed by global
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx, *, globe: str = None):
        if globe == "global":
            synced = await ctx.bot.tree.sync()
        else:
            synced = await ctx.bot.tree.sync(guild=ctx.guild)

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if globe == 'global' else 'to the current guild.'}"
        )

    # Shuts the bot down - usable by the bot owner - requires confirmation
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def shutdown(self, ctx):
        # Make confirmation message based on bots username to prevent myself from shutting wrong bot down.
        def check(message):
            return message.author.id == self.bot.config['owner_id']

        try:
            await ctx.send('Reply in 10 seconds to shutdown.', delete_after=10)
            response = await self.bot.wait_for('message', check=check, timeout=10)
            await response.add_reaction('✅')
            await self.bot.db.close()
            await self.bot.close()

        except asyncio.TimeoutError:
            pass

    # Generates a list of guilds the bot is in, contains name, bot and user counts
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(attach_files=True)
    async def guildlist(self, ctx):
        with open('cogs/data/guildlist.csv', 'w') as guild_list:
            guild_list.write('Server ID,Server Name,# of Users,Features\n')
            for guild in self.bot.guilds:

                # Write to csv file (guild name, total member count, region and features)
                guild_list.write(f'{guild.id},"{guild.name}",{guild.member_count},{guild.features}\n')

        await ctx.send(file=discord.File('cogs/data/guildlist.csv'))

    # Reload config json file, allows regen of bot listing tokens without taking bot down
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def reloadconfig(self, ctx):
        with open('settings/config.json', 'r') as config_file:
            self.bot.config = json.load(config_file)
            await ctx.message.add_reaction('✅')


async def setup(bot):
    await bot.add_cog(Owner(bot))
