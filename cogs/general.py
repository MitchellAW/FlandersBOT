import botInfo
import settings.config
import datetime
import discord
import json
import prefixes

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class General():
    def __init__(self, bot):
        self.bot = bot

    # Get the uptime of the bot. In a full description format by default.
    def getUptime(self, full=True):
        currentTime = datetime.datetime.utcnow()
        delta = currentTime - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if full:
            return ('{} days, {} hours, {} minutes, and {} seconds'.
                  format(days, hours, minutes, seconds))

        else:
            return ('{}d {}h {}m {}s'.
                  format(days, hours, minutes, seconds))

    # Whispers a description of the bot with author, framework, guild count etc.
    # If user has DMs disabled, send the message in the channel
    @commands.command()
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
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def help(self, ctx):
        try:
            await ctx.author.send(botInfo.commandsList)

        except:
            await ctx.send(botInfo.commandList)

    # Sends the feedback to the feedback channel of support server
    @commands.command()
    @commands.cooldown(2, 600, BucketType.user)
    async def feedback(self, ctx, *, message : str):
        feedbackChannel = self.bot.get_channel(403688189627465730)
        embed = discord.Embed(title='📫 Feedback from: ' + str(ctx.author) +
                              ' (' + str(ctx.author.id) + ')',
                              colour=discord.Colour(0x44981e),
                              description='```' + message + '```')

        embed.set_author(name=ctx.message.author.name,
                         icon_url=ctx.message.author.avatar_url)

        await feedbackChannel.send(embed=embed)

    # Display the prefixes used on the current guild
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def prefix(self, ctx):
        guildPrefixes = await prefixes.prefixesFor(ctx.message.guild,
                                                   self.bot.prefixData)
        if len(guildPrefixes) > 5:
            await ctx.send('This servers prefixes are: `ned`, `diddly`,' +
                               ' `doodly`,' + ' `diddly-`, `doodly-` and `' +
                               guildPrefixes[-1] + '`.' )

        else:
            await ctx.send('This servers prefixes are `ned`, `diddly`, ' +
                               '`doodly`,' + ' `diddly-` and `doodly-`.')

    # Allows for a single custom prefix per-guild
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(3, 60, BucketType.guild)
    async def setprefix(self, ctx, *, newPrefix : str=None):
        guildIndex = prefixes.findGuild(ctx.message.guild, self.bot.prefixData)

        # Only allow custom prefixes in guilds
        if ctx.message.guild is None:
            await ctx.send('Custom prefixes are for servers only.')

        # Require entering a prefix
        if newPrefix is None:
            await ctx.send('You did not provide a new prefix.')

        # Limit prefix to 10 characters, may increase
        elif len(newPrefix) > 10:
            await ctx.send('Custom server prefix too long (Max 10 chars).')

        elif self.bot.prefixData[guildIndex]['prefix'] == newPrefix:
            await ctx.send('This server custom prefix is already `' +
                               newPrefix + '`.')

        # Add a new custom guild prefix if one doesn't already exist
        elif guildIndex == -1:
            self.bot.prefixData.append({'guildID':ctx.message.guild.id,
                        'prefix':newPrefix})
            prefixes.writePrefixes(self.bot.prefixData)
            await ctx.send('This servers custom prefix changed to `'
                                       + newPrefix + '`.')

        # Otherwise, modify the current prefix to the new one
        else:
            self.bot.prefixData[guildIndex]['prefix'] = newPrefix
            prefixes.writePrefixes(self.bot.prefixData)
            await ctx.send('This servers custom prefix changed to `'
                                       + newPrefix + '`.')

    # Display statistics for the bot
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def stats(self, ctx):

        # Get guild count
        guildCount = len(self.bot.guilds)

        # Count users online in guilds
        totalMembers = 0
        onlineUsers = 0
        for guild in self.bot.guilds:
            totalMembers += len(guild.members)
            for member in guild.members:
                if member.status == discord.Status.online:
                    onlineUsers += 1

        averageOnline = round((onlineUsers / guildCount), 2)

        # Embed statistics output
        embed = discord.Embed(colour=discord.Colour(0x44981e))
        embed.set_thumbnail(url='https://images.discordapp.net/avatars/221609683562135553/afc35c7bcaf6dcb1c86a1c715ac955a3.png')
        embed.set_author(name='FlandersBOT Statistics', url='https://github.com/FlandersBOT', icon_url='https://images.discordapp.net/avatars/221609683562135553/afc35c7bcaf6dcb1c86a1c715ac955a3.png')
        embed.add_field(name='Bot Name', value='FlandersBOT#0680', inline=True)
        embed.add_field(name='Bot Owner', value='Mitch#8293', inline=True)
        embed.add_field(name='Total Members', value=str(totalMembers), inline=True)
        embed.add_field(name='Server Count', value=str(guildCount), inline=True)
        embed.add_field(name='Online Users', value=str(onlineUsers), inline=True)
        embed.add_field(name='Online Users Per Server', value=str(averageOnline), inline=True)
        embed.add_field(name='Uptime', value=self.getUptime(False), inline=True)

        # Post statistics
        await ctx.send(embed=embed)

    # Posts the bots uptime to the channel
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def uptime(self, ctx):
        await ctx.send('🔌 Uptime: **' + self.getUptime() + '**')


def setup(bot):
    bot.add_cog(General(bot))
