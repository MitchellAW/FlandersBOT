import datetime

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Stats:
    def __init__(self, bot):
        self.bot = bot

    # Get the uptime of the bot. In a short description format by default.
    def get_uptime(self, full=False):
        current_time = datetime.datetime.utcnow()
        delta = current_time - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if full:
            return ('{} days, {} hours, {} minutes, and {} seconds'.
                    format(days, hours, minutes, seconds))

        else:
            return ('{}d {}h {}m {}s'.
                    format(days, hours, minutes, seconds))

    # Posts the bots uptime to the channel
    @commands.command(aliases=['Uptime', 'UPTIME'])
    @commands.cooldown(1, 3, BucketType.user)
    async def uptime(self, ctx):
        await ctx.send('🔌 Uptime: **' + self.get_uptime(True) + '**')

    # Check the latency of the bot
    @commands.command(aliases=['Ping', 'PING'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000, 2)
        await ctx.send('🏓 Latency: ' + str(latency) + 'ms')

    # Get all episode information of the last screencap that was posted in the
    # channel
    @commands.command(aliases=['Epinfo', 'EpInfo', 'EPINFO'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def epinfo(self, ctx):
        if ctx.channel.id in self.bot.cached_screencaps:
            # Get screencap and its timestamp
            screencap = self.bot.cached_screencaps[ctx.channel.id]
            real_timestamp = screencap.get_real_timestamp()

            # Create embed for episode information, links to wiki of episode
            embed = discord.Embed(
                title=screencap.api.title + ': ' + screencap.title,
                colour=discord.Colour(0x44981e),
                url=screencap.wiki_url)

            # Add episode information
            embed.add_field(name='Episode', value=screencap.key, inline=True)
            embed.add_field(name='Air Date', value=screencap.air_date,
                            inline=True)
            embed.add_field(name='Timestamp', value=real_timestamp,
                            inline=True)
            embed.add_field(name='Director(s)', value=screencap.director)
            embed.add_field(name='Writer(s)', value=screencap.writer)
            await ctx.send(embed=embed)

    # Display statistics for the bot
    @commands.command(aliases=['Stats', 'STATS'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def stats(self, ctx):
        # Count users online in guilds and user average
        total_members = 0
        online_users = 0
        for guild in self.bot.guilds:
            total_members += len(guild.members)
            for member in guild.members:
                if member.status == discord.Status.online:
                    online_users += 1
        user_average = round((online_users / self.bot.guilds), 2)
        guild_count = str(self.bot.guilds)

        # Count number of commands executed
        command_count = 0
        for key in self.bot.command_stats:
            command_count += self.bot.command_stats[key]

        # Embed statistics output
        embed = discord.Embed(colour=discord.Colour(0x44981e))
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name=self.bot.user.name + ' Statistics',
                         url='https://github.com/FlandersBOT',
                         icon_url=self.bot.user.avatar_url)

        # Add all statistics
        embed.add_field(name='Bot Owner', value='Mitch#8293', inline=True)
        embed.add_field(name='Server Count', value=guild_count, inline=True)
        embed.add_field(name='Total Members', value=total_members, inline=True)
        embed.add_field(name='Online Users', value=online_users, inline=True)
        embed.add_field(name='Average Online', value=user_average, inline=True)
        embed.add_field(name='Uptime', value=self.get_uptime(), inline=True)
        embed.add_field(name='Commands Used', value=command_count, inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
