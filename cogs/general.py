import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import bot_info
import prefixes


class General:
    def __init__(self, bot):
        self.bot = bot
        self.FEEDBACK_CHANNEL = 403688189627465730

    # Try to send a DM to author, otherwise post in channel
    @staticmethod
    async def dm_author(ctx, message):
        try:
            await ctx.author.send(message)

        except discord.Forbidden:
            await ctx.send(message)

    # Whispers a description of the bot with author, framework, guild count etc.
    # If user has DMs disabled, send the message in the channel
    @commands.command(aliases=['Info', 'INFO'])
    @commands.cooldown(1, 3, BucketType.user)
    async def info(self, ctx):
        await self.dm_author(ctx, bot_info.bot_info + '\n***Currently active '
                             'in ' + str(len(self.bot.guilds)) + 'servers***')

    # Whispers a list of the bot commands, If the user has DMs disabled,
    # sends the message in the channel
    @commands.command(aliases=['Help', 'HELP'])
    @commands.cooldown(1, 3, BucketType.user)
    async def help(self, ctx, *, category: str=None):
        # Post general help commands
        if category is None:
            await self.dm_author(ctx, bot_info.commands_list)

        # Post help commands for all tv shows
        elif category.lower() == 'tvshows' or category.lower() == 'tv shows':
            await self.dm_author(ctx, bot_info.tv_shows)

    # Whispers a list of help commands for all tv shows
    @commands.command(aliases=['Tvshows', 'TVshows', 'TVShows', 'TVSHOWS',
                               'tv', 'TV', 'Tv'])
    @commands.cooldown(1, 3, BucketType.user)
    async def tvshows(self, ctx):
        await self.dm_author(ctx, bot_info.tv_shows)

    # Sends the feedback to the feedback channel of support server
    @commands.command(aliases=['Feedback', 'FEEDBACK'])
    @commands.cooldown(2, 600, BucketType.user)
    async def feedback(self, ctx, *, message: str):
        feedback_channel = self.bot.get_channel(self.FEEDBACK_CHANNEL)
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
        await self.dm_author(ctx, 'You can add me to your own server using '
                                  'the link below:\n'
                                  '<https://discordapp.com/oauth2/authorize?'
                                  'client_id=' + str(self.bot.user.id) +
                                  '&scope=bot&permissions=19456>')

    # Sends url to FlandersBOT github repo
    @commands.command(aliases=['Source', 'SOURCE', 'github', 'Github',
                               'GitHub', 'GITHUB', 'repo', 'Repo', 'REPO'])
    @commands.cooldown(1, 3, BucketType.user)
    async def source(self, ctx):
        await ctx.send('Github Repo Source: '
                       '<https://github.com/MitchellAW/FlandersBOT>')

    # Display information regarding the last update
    @commands.command(aliases=['Update', 'UPDATE'])
    @commands.cooldown(1, 3, BucketType.user)
    async def update(self, ctx):
        await ctx.send('I now support 30 Rock and West Wing! Use `ned tvshows`'
                       'for information on how to use them. If you experience '
                       'any issues with this, please use `ned feedback ['
                       'feedback here]`')

    # Allow administrators to make ned leave the server
    @commands.command(aliases=['Leave', 'LEAVE'])
    @commands.guild_only()
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
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(3, 60, BucketType.guild)
    async def setprefix(self, ctx, *, new_prefix: str=None):
        guild_index = prefixes.find_guild(ctx.message.guild,
                                          self.bot.prefix_data)
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
            await ctx.send('This servers custom prefix changed to `' +
                           new_prefix + '`.')


def setup(bot):
    bot.add_cog(General(bot))
