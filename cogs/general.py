import datetime

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import botInfo
import prefixes


class General:
    def __init__(self, bot):
        self.bot = bot

    # Get the uptime of the bot. In a full description format by default.
    def get_uptime(self, full=True):
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

    # Check the latency of the bot
    @commands.command(aliases=['Ping', 'PING'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000, 2)
        await ctx.send('🏓 Latency: ' + str(latency) + 'ms')

    # Whispers a description of the bot with author, framework, guild count etc.
    # If user has DMs disabled, send the message in the channel
    @commands.command(aliases=['Info', 'INFO'])
    @commands.cooldown(1, 3, BucketType.user)
    async def info(self, ctx):
        try:
            await ctx.author.send(botInfo.botInfo + '\n***Currently active in '
                                  + str(len(self.bot.guilds)) + ' servers***')

        except discord.Forbidden:
            await ctx.send(botInfo.botInfo + '\n***Currently active in '
                           + str(len(self.bot.guilds)) + ' servers***')

    # Whispers a list of the bot commands, If the user has DMs disabled,
    # sends the message in the channel
    @commands.command(aliases=['Help', 'HELP'])
    @commands.cooldown(1, 3, BucketType.user)
    async def help(self, ctx):
        try:
            await ctx.author.send(botInfo.commandsList)

        except discord.Forbidden:
            await ctx.send(botInfo.commandsList)

    # Sends the feedback to the feedback channel of support server
    @commands.command(aliases=['Feedback', 'FEEDBACK'])
    @commands.cooldown(2, 600, BucketType.user)
    async def feedback(self, ctx, *, message: str):
        feedback_channel = self.bot.get_channel(403688189627465730)
        embed = discord.Embed(title='📫 Feedback from: ' + str(ctx.author) +
                              ' (' + str(ctx.author.id) + ')',
                              colour=discord.Colour(0x44981e),
                              description='```' + message + '```')

        embed.set_author(name=ctx.message.author.name,
                         icon_url=ctx.message.author.avatar_url)

        await feedback_channel.send(embed=embed)
        # Thank for feedback and suggest vote
        await ctx.send('Thanks neighbourino! 📫 The feedback has been sent ' +
                       'to my support serveroo! If you\'d like to hel-diddly' +
                       '-elp me grow in popularity, try `ned vote`')

    # Message the benefits of voting and provide link to upvote at
    @commands.command(aliases=['Vote', 'VOTE', 'upvote', 'Upvote', 'UPVOTE'])
    @commands.cooldown(1, 3, BucketType.user)
    async def vote(self, ctx):
        await ctx.send('If you vote for me using the link below, it will '
                       'hel-diddly-elp me grow in popularity!\n'
                       '<https://discordbots.org/bot/221609683562135553/vote>')

    # DM user with an invite link for the bot
    @commands.command(aliases=['Invite', 'INVITE'])
    @commands.cooldown(1, 3, BucketType.user)
    async def invite(self, ctx):
        try:
            await ctx.author.send('You can add me to your own server using '
                                  'the link below:\n'
                                  '<https://discordapp.com/oauth2/authorize?'
                                  'client_id=' + str(self.bot.user.id) +
                                  '&scope=bot&permissions=19456>')

        except discord.Forbidden:
            ctx.send('You can add me to your own server using the link below:\n'
                     '<https://discordapp.com/oauth2/authorize?client_id=' +
                     str(self.bot.user.id) + '&scope=bot&permissions=19456>')

    # Display information regarding the last update
    @commands.command(aliases=['Update', 'UPDATE'])
    @commands.cooldown(1, 3, BucketType.user)
    async def update(self, ctx):
        await ctx.send('**Ever had trouble with my gifs not always '
                       'diddly-ding-dong displaying in discord?**\nWell now '
                       'I will generate all my gifs for you, so that they '
                       'will embed-diddly-ed more often! If you experience any'
                       ' issues with this, please use `ned feedback [feedback '
                       'here]`')

    # Allow administrators to make ned leave the server
    @commands.command(aliases=['Leave', 'LEAVE'])
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        await ctx.send('Okilly-dokilly! 👋')
        await ctx.guild.leave()

    # Display the prefixes used on the current guild
    @commands.command(aliases=['Prefix', 'PREFIX', 'prefixes', 'Prefixes'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def prefix(self, ctx):
        guild_prefixes = prefixes.prefixes_for(ctx.message.guild,
                                                     self.bot.prefix_data)
        if len(guild_prefixes) > 5:
            await ctx.send('This servers prefixes are: `Ned`, `ned`, `diddly`' +
                           ', `doodly`,' + ' `diddly-`, `doodly-` and `' +
                           guild_prefixes[-1] + '`.')

        else:
            await ctx.send('This servers prefixes are: `Ned`, `ned`, `diddly`' +
                           ', `doodly`,' + ' `diddly-` and `doodly-`.')

    # Allows for a single custom prefix per-guild
    @commands.command(aliases=['Setprefix', 'SETPREFIX'])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(3, 60, BucketType.guild)
    async def setprefix(self, ctx, *, new_prefix: str=None):
        guild_index = prefixes.find_guild(ctx.message.guild,
                                          self.bot.prefix_data)

        # Only allow custom prefixes in guilds
        if ctx.message.guild is None:
            await ctx.send('Custom prefixes are for servers only.')

        # Require entering a prefix
        if new_prefix is None:
            await ctx.send('You did not provide a new prefix.')

        # Limit prefix to 10 characters, may increase
        elif len(new_prefix) > 10:
            await ctx.send('Custom server prefix too long (Max 10 chars).')

        elif self.bot.prefix_data[guild_index]['prefix'] == new_prefix:
            await ctx.send('This server custom prefix is already `' +
                           new_prefix + '`.')

        # Add a new custom guild prefix if one doesn't already exist
        elif guild_index == -1:
            self.bot.prefix_data.append({'guildID': ctx.message.guild.id,
                                        'prefix': new_prefix})
            prefixes.write_prefixes(self.bot.prefix_data)
            await ctx.send('This servers custom prefix changed to `'
                           + new_prefix + '`.')

        # Otherwise, modify the current prefix to the new one
        else:
            self.bot.prefix_data[guild_index]['prefix'] = new_prefix
            prefixes.write_prefixes(self.bot.prefix_data)
            await ctx.send('This servers custom prefix changed to `'
                           + new_prefix + '`.')

    # Display statistics for the bot
    @commands.command(aliases=['Stats', 'STATS'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def stats(self, ctx):
        # Get guild count
        guild_count = len(self.bot.guilds)

        # Count users online in guilds
        total_members = 0
        online_users = 0
        for guild in self.bot.guilds:
            total_members += len(guild.members)
            for member in guild.members:
                if member.status == discord.Status.online:
                    online_users += 1

        average_online = round((online_users / guild_count), 2)

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
        embed.add_field(name='Bot Owner', value='Mitch#8293',
                        inline=True)
        embed.add_field(name='Server Count', value=str(guild_count),
                        inline=True)
        embed.add_field(name='Total Members', value=str(total_members),
                        inline=True)
        embed.add_field(name='Online Users', value=str(online_users),
                        inline=True)
        embed.add_field(name='Online Users Per Server',
                        value=str(average_online), inline=True)
        embed.add_field(name='Uptime', value=self.get_uptime(False),
                        inline=True)
        embed.add_field(name='Commands Executed', value=str(command_count),
                        inline=True)

        # Post statistics
        await ctx.send(embed=embed)

    # Posts the bots uptime to the channel
    @commands.command(aliases=['Uptime', 'UPTIME'])
    @commands.cooldown(1, 3, BucketType.user)
    async def uptime(self, ctx):
        await ctx.send('🔌 Uptime: **' + self.get_uptime() + '**')


def setup(bot):
    bot.add_cog(General(bot))
