import asyncio
import datetime
import json

import asyncpg
import discord
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Track command count
        self.command_count = 0
        self.bot.loop.create_task(self.count_commands())

        # Insert command updates in batches to prevent spam causing excessive inserts
        self._command_batch = []
        self._batch_lock = asyncio.Lock(loop=self.bot.loop)
        self.batch_insert_loop.add_exception_type(asyncpg.PostgresConnectionError)
        self.batch_insert_loop.start()

    # Get the uptime of the bot. In a short description format by default.
    def get_uptime(self, full=False):
        current_time = datetime.datetime.utcnow()
        delta = current_time - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if full:
            return f'{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds'

        else:
            return f'{days}d {hours}h {minutes}m {seconds}s'

    # Update the cached successful command count
    async def count_commands(self):
        query = '''SELECT COUNT(*) FROM command_history
                   WHERE failed = false
                '''
        self.command_count = await self.bot.db.fetchval(query)

    # On each command, add attributes of command to batch to be logged by task loop
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        # Ensure command recorded
        if ctx.command is None:
            return

        # Get guild id
        guild_id = None
        if ctx.guild is not None:
            guild_id = ctx.guild.id

        # Cache command to batch for insertion
        self._command_batch.append(
            {
                'command': ctx.command.qualified_name,
                'prefix': ctx.prefix,
                'guild_id': guild_id,
                'used_at': ctx.message.created_at.isoformat(),
                'failed': ctx.command_failed
            }
        )

        # Update command count
        if not ctx.command_failed:
            self.command_count += 1

    # Ensure loop ends if cog is unloaded
    def cog_unload(self):
        self.batch_insert_loop.stop()

    # Loops each 10 seconds, inserts all batched command stats into command history table
    @tasks.loop(seconds=10)
    async def batch_insert_loop(self):
        async with self._batch_lock:
            query = '''INSERT INTO command_history (command, prefix, guild_id, used_at, failed)
                       SELECT x.command, x.prefix, x.guild_id, x.used_at, x.failed 
                       FROM jsonb_to_recordset($1::jsonb) AS
                       x(command TEXT, prefix TEXT, guild_id BIGINT, used_at TIMESTAMP, failed BOOLEAN)
                    '''
            if self._command_batch:
                await self.bot.db.execute(query, json.dumps(self._command_batch))
                self._command_batch.clear()

    # Posts the bots uptime to the channel
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def uptime(self, ctx):
        await ctx.send(f'🔌 Uptime: **{self.get_uptime(True)}**')

    # Check the latency of the bot
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000, 2)
        await ctx.send(f'🏓 Latency: {str(latency)}ms')

    # Get all episode information of the last screencap that was posted in the
    # channel
    @commands.command(aliases=['episodeinfo'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.bot_has_permissions(embed_links=True)
    async def epinfo(self, ctx):
        if ctx.channel.id in self.bot.cached_screencaps:
            # Get screencap and its timestamp
            screencap = self.bot.cached_screencaps[ctx.channel.id]
            real_timestamp = screencap.get_real_timestamp()

            # Create embed for episode information, links to wiki of episode
            embed = discord.Embed(title=f'{screencap.api.title}: {screencap.title}', colour=discord.Colour(0x44981e),
                                  url=screencap.wiki_url)

            # Add episode information
            embed.add_field(name='Episode', value=screencap.key, inline=True)
            embed.add_field(name='Air Date', value=screencap.air_date, inline=True)
            embed.add_field(name='Timestamp', value=real_timestamp, inline=True)
            embed.add_field(name='Director(s)', value=screencap.director)
            embed.add_field(name='Writer(s)', value=screencap.writer)
            await ctx.send(embed=embed)

    # Display statistics for the bot
    @commands.command(aliases=['statistics'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.bot_has_permissions(embed_links=True)
    async def stats(self, ctx):
        # Count users online in guilds and user average
        total_members = 0
        for guild in self.bot.guilds:
            total_members += guild.member_count

        guild_count = len(self.bot.guilds)

        # Embed statistics output
        embed = discord.Embed(colour=discord.Colour(0x44981e))
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name=f'{self.bot.user.name} Statistics', url='https://github.com/FlandersBOT',
                         icon_url=self.bot.user.avatar_url)

        # Round latency to 2 decimal places and get milliseconds
        latency = round(self.bot.latency * 1000, 2)

        # Add all statistics
        embed.add_field(name='Bot Owner', value='Mitch#8293', inline=True)
        embed.add_field(name='Server Count', value=f'{guild_count:,}', inline=True)
        embed.add_field(name='Total Members', value=f'{total_members:,}', inline=True)
        embed.add_field(name='Uptime', value=self.get_uptime(), inline=True)
        embed.add_field(name='Latency', value=f'{latency:,}' + ' ms', inline=True)
        embed.add_field(name='Commands Used', value=f'{self.command_count:,}', inline=True)
        await ctx.send(embed=embed)

    # All privacy related functions, including information regarding the data logged, and options to both delete, and
    # opt out of future data logging
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def privacy(self, ctx, *, subcommand: str = None):
        # Display generic privacy info
        if subcommand is None or subcommand == 'info':
            await ctx.send('FlandersBOT stores the user ID (e.g. 221609683562135553) privately and stores the username '
                           '& discriminator (e.g. FlandersBOT#0680) of all trivia participants publicly for use in the '
                           'trivia leaderboards.\nIf you wish to participate in trivia without appearing in the '
                           'leaderboards, use the command: `ned privacy config`\nIf you wish to remove all data '
                           'relating to your account, use the command: `ned privacy remove`.')

        # Adjust privacy settings for user
        elif subcommand.lower() in ['edit', 'update', 'config', 'modify']:
            msg = await ctx.send('By default, all trivia participants are visible to the public in the trivia '
                                 'leaderboard. Alternatively, you may change your privacy settings by reacting to this '
                                 'message.\n**A**: Public\n**B**: Private')

            await msg.add_reaction('🇦')
            await msg.add_reaction('🇧')

            # Check for response of cross/tick
            def is_answer(reaction, user):
                return (not user.bot and str(reaction.emoji) in ['🇦', '🇧', '🇨']
                        and user.id == ctx.author.id)

            react, user = await self.bot.wait_for('reaction_add',
                                                  check=is_answer, timeout=120)

            # Affirmative reaction, drop all data for that user
            if react.emoji == '🇦':

                # Set privacy setting for profile to public
                query = '''UPDATE leaderboard
                           SET privacy = 0
                           WHERE user_id = $1
                        '''
                await self.bot.db.execute(query, user.id)
                await msg.edit(content='Your leaderboard stats are now public')

            # Affirmative reaction, drop all data for that user
            if react.emoji == '🇧':
                # Set privacy setting for profile to private
                query = '''UPDATE leaderboard
                           SET privacy = 1
                           WHERE user_id = $1
                        '''
                await self.bot.db.execute(query, user.id)
                await msg.edit(content='Your leaderboard stats are now private.')

        # Remove all data logged for user
        elif subcommand.lower() in ['remove', 'delete', 'erase', 'purge']:
            msg = await ctx.send('Would you like to erase all your user data?\nThis will remove you from the trivia '
                                 'leaderboard, and cannot be undone.')

            await msg.add_reaction('❌')
            await msg.add_reaction('✅')

            # Check for response of cross/tick
            def is_answer(reaction, user):
                return not user.bot and str(reaction.emoji) in ['❌', '✅'] and user.id == ctx.author.id

            react, user = await self.bot.wait_for('reaction_add', check=is_answer, timeout=120)

            # Affirmative reaction, drop all data for that user
            if react.emoji == '✅':

                # Delete all records of user from leaderboard
                query = '''DELETE FROM leaderboard 
                           WHERE user_id = $1
                        '''
                await self.bot.db.execute(query, user.id)

                # Delete all records of user from answers
                query = '''DELETE FROM answers
                           WHERE user_id = $1
                        '''
                await self.bot.db.execute(query, user.id)

                # Clear all records of user id from vote history, replaces with null
                query = '''UPDATE vote_history
                           SET user_id = NULL
                           WHERE user_id = $1
                        '''
                await self.bot.db.execute(query, user.id)

                await msg.edit(content='All data relating to your account has been deleted.\nIf you wish to '
                                       'participate in trivia without appearing in the leaderboards, use the command: '
                                       '`ned privacy config`')


async def setup(bot):
    await bot.add_cog(Stats(bot))
