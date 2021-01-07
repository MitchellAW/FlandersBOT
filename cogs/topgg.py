import asyncio
from datetime import datetime

import dbl
import discord
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType

from cogs.general import General


class TopGG(commands.Cog):
    # Query to get the total points (weekend = 2, weekday = 1)
    POINTS_QUERY = '''SELECT SUM(CASE WHEN is_weekend THEN 2 ELSE 1 END) AS points FROM vote_history
                      WHERE vote_type = 'upvote'
                   '''

    # Query to insert a new vote into the history
    INSERT_QUERY = '''INSERT INTO vote_history (user_id, vote_type,  is_weekend)
                      VALUES ($1, $2, $3)
                   '''

    # Get time of most recent vote from user
    LAST_VOTE_QUERY = '''SELECT MAX(voted_at) FROM vote_history
                         WHERE user_id = $1 AND vote_type = 'upvote'
                      '''

    VOTE_URL = '<https://discordbots.org/bot/221609683562135553/vote>'

    def __init__(self, bot):
        self.bot = bot
        self.cached_subscribers = set()

        # Client for interacting with top.gg API
        self.dblpy = dbl.DBLClient(
            self.bot,
            self.bot.config['dbl_token'],
            webhook_auth=self.bot.config['webhook']['webhookAuth'],
            webhook_port=self.bot.config['webhook']['webhookPort'],
            webhook_path='/dblwebhook',
            # Only auto post server count if not in debug mode
            autopost=(not self.bot.debug_mode)
        )

        # Update table with any missing votes
        self.bot.loop.create_task(self.update_missing_votes())

    # (Re) Populate cache using entries in subscribers table
    async def cache_subscribers(self):
        self.cached_subscribers.clear()
        query = '''SELECT user_id FROM subscribers
                '''
        rows = await self.bot.db.fetch(query)
        self.cached_subscribers.update(map(lambda row: row['user_id'], rows))

    # Notify all users on restart
    async def notify_subscribers(self):
        for user_id in self.cached_subscribers:
            await self.notify_user(user_id, new_vote=False)

    # Record any missing votes since webhook was last ran.
    # Inserts missing votes as null user_id into vote_history table
    async def update_missing_votes(self):
        # Cache subscribers and add
        await self.cache_subscribers()
        await self.notify_subscribers()

        # Get info for this bot
        bot_info = await self.dblpy.get_bot_info(self.bot.config['bot_id'])

        # Count votes currently in history
        logged_points = await self.bot.db.fetchval(self.POINTS_QUERY)

        if logged_points is None:
            logged_points = 0

        # Calculate missing votes
        votes_missing = bot_info['points'] - logged_points

        # For each missing vote, insert value with null user and is_weekend as false
        if votes_missing > 0:
            print(f'Inserting {votes_missing} missing votes...')

        for _ in range(votes_missing):
            await self.bot.db.execute(self.INSERT_QUERY, None, 'upvote', False)

    # Insert vote into vote history table and thank user for voting
    async def log_and_thank(self, data):
        await self.bot.db.execute(self.INSERT_QUERY, int(data['user']), data['type'], data['isWeekend'])

        # Get user using id
        user_id = int(data['user'])
        user = self.bot.get_user(user_id)

        # Thank if subscribed to notifications
        if user_id in self.cached_subscribers:
            await user.send('Thanks for voting! You will now be notified when you can vote again in 12 hours.')

            # Notify user when they can vote next
            await self.notify_user(user_id, new_vote=True)

    # Notify user in 12 hours or whenever they can vote again if they're subscribed
    async def notify_user(self, user_id, new_vote=True):
        user = self.bot.get_user(user_id)

        # Wait time remaining
        seconds_remaining = await self.seconds_until_vote(user_id)

        # Wait if user has voted recently
        if seconds_remaining is not None:
            await asyncio.sleep(seconds_remaining)

        # Ensure user still wants to be notified
        if user_id in self.cached_subscribers and new_vote:
            await user.send('<https://discordbots.org/bot/221609683562135553/vote>\n**You can vote now.**')

    # Get seconds remaining until user is able to vote again, returns None if no votes recorded
    async def seconds_until_vote(self, user_id):
        voted_at = await self.bot.db.fetchval(self.LAST_VOTE_QUERY, int(user_id))

        # Return seconds until next vote (subtract from 12 hours)
        if voted_at is not None:
            time_diff = (datetime.utcnow() - voted_at)

            # Seconds until user can vote again
            time_between_votes = (12 * 60 * 60)
            seconds_remaining = time_between_votes - min(time_diff.seconds, time_between_votes)
            return seconds_remaining

        else:
            return None

    # Gets the hours, minutes and seconds remaining using the number of seconds given
    @staticmethod
    def time_until_vote(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return hours, minutes, seconds

    # Event triggered when user votes for the bot, logs vote and thanks user
    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        await self.log_and_thank(data)

    # Event triggered for test upvotes, logs vote and thanks user
    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        await self.log_and_thank(data)

    # Message the benefits of voting and provide link to upvote at
    @commands.command(aliases=['upvote', 'voting'])
    @commands.cooldown(1, 30, BucketType.user)
    async def vote(self, ctx):
        message = 'If you vote for me using the link below, it will hel-diddly-elp me grow in popularity!\n'

        # Check if user is able to vote already
        seconds_remaining = await self.seconds_until_vote(ctx.author.id)
        if seconds_remaining is None or seconds_remaining <= 0:
            message += f'{self.VOTE_URL}\n**You can vote now.**'

        # Otherwise, notify them of the time remaining until they can vote again
        else:
            hours, minutes, seconds = self.time_until_vote(seconds_remaining)
            message += f'**You can vote again in: {hours} hours, {minutes} minutes, and {seconds} seconds.**'

        await ctx.send(message)

    # Toggle notifications for when user can vote again
    @commands.command(aliases=['notify', 'toggle', 'reminder', 'remind', 'subscribe', 'sub'])
    @commands.cooldown(2, 30, BucketType.user)
    async def notifications(self, ctx):
        # Disable notifications if already subscribed
        if ctx.author.id in self.cached_subscribers:
            query = '''DELETE FROM subscribers
                       WHERE user_id = $1
                    '''
            await self.bot.db.execute(query, ctx.author.id)
            await self.cache_subscribers()
            await General.dm_author(ctx, 'You will no longer be notified when you can vote again.')
            return

        # Attempt to DM user and notify them they have subscribed
        try:
            message = 'Notifications enabled.\n'

            # Check if user is able to vote now
            seconds_remaining = await self.seconds_until_vote(ctx.author.id)

            # No vote timestamps for user in history or voted over 12 hours ago, notify and exit
            if seconds_remaining is None or seconds_remaining <= 0:
                message += f'{self.VOTE_URL}\n**You can vote now.**'

            # Notify user of the time remaining before notification will be sent
            else:
                hours, minutes, seconds = self.time_until_vote(seconds_remaining)
                message += f'**You will be notified when you can vote again in: {hours} hours, {minutes} minutes, '\
                           f'and {seconds} seconds.**'

            await ctx.author.send(message)

        # DMs are disabled, don't enable notifications
        except discord.Forbidden:
            await ctx.send('You have DMs disabled, please enable DMs if you\'d like to enable notifications.')

        # If DMs are available, add user to reminders list and notify them
        else:
            query = '''INSERT INTO subscribers (user_id)
                       VALUES ($1)
                    '''
            await self.bot.db.execute(query, ctx.author.id)

            # Notify user when time expires
            if seconds_remaining is not None and seconds_remaining > 0:
                await self.notify_user(ctx.author.id, new_vote=True)


def setup(bot):
    bot.add_cog(TopGG(bot))