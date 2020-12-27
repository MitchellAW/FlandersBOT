from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import prefixes

COMMANDS_LIST = '''
Hi-diddly-ho, neighborino! Here are the commands, shout them out anytime and
I'll happily oblige! Well, so long as the reverend approves of course.

**COMMAND PREFIXES**

`ned`, `diddly`, `doodly`

**COMMANDS**
*All commands must start with one of the command prefixes or 
<@221609683562135553>!*

**GENERAL**

**help** - Will send this list of commands.
**info** - Will send a personal message with more information about me.
**prefix** - Will post the prefixes I respond to on your server.
**setprefix [prefix]** - Sets a prefix I will respond to on your server.
**feedback [message]** - Send a feedback message or suggestions.
**invite** - Will post an invite link for me to join your server.
**vote** - Will post the benefits of voting for me and a link to vote.
**notifications** - Will toggle DM reminders for when you can vote next.
**update** - Will post the highlights of my last major update.
**stats** - Will post some of my statist-diddly-istics.

**TV SHOWS**

**tvshows** - Will post a list of commands for all currently supported TV shows.
**trivia** - Will post a list of commands for playing trivia games.
**epinfo** - Will post episode information on the last post made in the channel.

*I currently support commands for The Simpsons, Futurama, Rick and Morty.*

**For Example:** `ned info`, `diddly help tvshows`, `doodly-trivia`
'''

TV_SHOW_COMMANDS = '''
**TV SHOWS**

**simpsons** - Will post a random Simpsons gif with caption.
**simpsons [quote]** - Searches for a Simpsons gif using the quote.

**futurama** - Will post a random Futurama gif with caption.
**futurama [quote]** - Searches for a Futurama gif using the quote.

**rickandmorty** - Will post a random Rick and Morty gif with caption.
**rickandmorty [quote]** - Searches for a Rick and Morty gif using the quote.

**epinfo** - Will post episode information on the last post made in the channel.

**For Example:** `ned simpsons nothing at all`, `ned futurama`
'''

TRIVIA_COMMANDS = '''
**TRIVIA**

**simpsonstrivia** - Play a trivia game using 100+ questions from The Simpsons.
**futuramatrivia** - Play a game of trivia using 100+ questions from Futurama.
**suggest** - Posts a link for suggesting some trivia questions of your own.
**leaderboard** - Shows a leaderboard of trivia users across the globe.
**scoreboard** - Shows a scoreboard of trivia users in the server.
**score** - Shows your trivia score and statistics, used in the leaderboards.

**For Example:** `ned simpsonstrivia`, `ned leaderboard`, `ned suggest` 
'''

BOT_INFO = ('''Hi-diddly-ho, neighborino! I hear you wanted some 
mor-diddly-ore information...
Well, If it's clear and yella', you've got juice there, fella. If it's tangy 
and brown, you're in cider town.
Now, there's two exceptions and it gets kinda tricky here...

__**INFO**__

Framework: Discord.py (version=''' + discord.__version__ + ''')
Author: <@210898009242861568> (Discord)
Support Server: <https://discord.gg/xMmxMYg>
Invite URL: <https://discordapp.com/oauth2/authorize?client_id=''' +
            '''221609683562135553&scope=bot&permissions=19456>
GitHub Source: <https://github.com/MitchellAW/FlandersBOT>
If you'd like to hel-diddly-elp me grow in popularity, use `ned vote`
''')

VOTE_URL = '<https://discordbots.org/bot/221609683562135553/vote>'


class General(commands.Cog):
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
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def info(self, ctx):
        await self.dm_author(ctx, BOT_INFO + '\n***Currently active '
                             'in ' + str(len(self.bot.guilds)) + ' servers***')

    # Whispers a list of the bot commands, If the user has DMs disabled,
    # sends the message in the channel
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def help(self, ctx, *, category: str = None):
        # Post general help commands
        if category is None:
            await self.dm_author(ctx, COMMANDS_LIST)

        # Post help commands for all tv shows
        elif category.lower() == 'tvshows' or category.lower() == 'tv shows':
            await self.dm_author(ctx, TV_SHOW_COMMANDS)

    # Whispers a list of help commands for all tv shows
    @commands.command(aliases=['tv'])
    @commands.cooldown(1, 3, BucketType.user)
    async def tvshows(self, ctx):
        await self.dm_author(ctx, TV_SHOW_COMMANDS)

    # Will get the last screencap posted in the channel and post a new gif
    # of the same moment with meme_caption as the new caption
    @commands.command(aliases=['caption', 'subtitles', 'custom'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def meme(self, ctx, *, meme_caption: str = None):
        if ctx.channel.id in self.bot.cached_screencaps:
            screencap = self.bot.cached_screencaps[ctx.channel.id]

            if screencap is not None:
                gif_url = await screencap.get_gif_url(meme_caption)
                sent = await ctx.send('Generating meme... ' +
                                      '<a:loading:410316176510418955>')
                generated_url = await screencap.api.generate_gif(gif_url)
                try:
                    await sent.edit(content=generated_url)

                except discord.NotFound:
                    pass

    # Sends the feedback to the feedback channel of support server
    @commands.command()
    @commands.cooldown(2, 600, BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def feedback(self, ctx, *, message: str = None):
        if message is None:
            await ctx.send('Sorry, I noodily-need some feedback to send.\n' +
                           'Usage: `ned feedback [feedback message here]`')
        else:
            feedback_channel = self.bot.get_channel(self.FEEDBACK_CHANNEL)
            embed = discord.Embed(title='📫 Feedback from: ' + str(ctx.author) +
                                  ' (' + str(ctx.author.id) + ')',
                                  colour=discord.Colour(0x44981e),
                                  description='```' + message + '```')

            embed.set_author(name=ctx.message.author.name,
                             icon_url=ctx.message.author.avatar_url)

            await feedback_channel.send(embed=embed)
            # Thank for feedback and suggest vote
            await ctx.send('Thanks neighbourino! 📫 The feedback has been ' +
                           'sent to my support serveroo! If you\'d like to ' +
                           'hel-diddly-elp me grow in popularity, try ' +
                           '`ned vote`.')

    # Message the benefits of voting and provide link to upvote at
    @commands.command(aliases=['upvote'])
    @commands.cooldown(1, 30, BucketType.user)
    async def vote(self, ctx):
        query = '''SELECT MAX(voted_at) FROM vote_history
                   WHERE user_id = $1 AND vote_type = 'upvote';'''

        message = ('If you vote for me using the link below, it will ' +
                   'hel-diddly-elp me grow in popularity!\n' + VOTE_URL + '\n')

        row = await self.bot.db.fetchrow(query, ctx.author.id)

        if row['max'] is not None:
            time_diff = (datetime.utcnow() - row['max'])
            seconds_remaining = 43200 - time_diff.seconds

            if seconds_remaining <= 0:
                message += '**You can vote now.**'

            else:
                hours, remainder = divmod(seconds_remaining, 3600)
                minutes, seconds = divmod(remainder, 60)
                message += ('**You can vote again in: {} hours, {} minutes, '
                            'and {} seconds.**'.format(hours, minutes, seconds))

        else:
            message += '**You can vote now.**'

        await ctx.send(message)

    # DM user with an invite link for the bot
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def invite(self, ctx):
        await self.dm_author(ctx, 'You can add me to your own server using '
                                  'the link below:\n'
                                  '<https://discordapp.com/oauth2/authorize?'
                                  'client_id=' + str(self.bot.user.id) +
                                  '&scope=bot&permissions=19456>')

    # Sends url to FlandersBOT github repo
    @commands.command(aliases=['github', 'repo'])
    @commands.cooldown(1, 3, BucketType.user)
    async def source(self, ctx):
        await ctx.send('Github Repo Source: '
                       '<https://github.com/MitchellAW/FlandersBOT>')

    # Display information/news regarding the last update
    @commands.command(aliases=['news'])
    @commands.cooldown(1, 3, BucketType.user)
    async def update(self, ctx):
        await ctx.send('- Added 200+ new questions to Simpsons trivia!'
                       '- Added a trivia leaderboard, use `Ned leaderboard`!'
                       '- Trivia matches now display a scoreboard at the end!')

    # Allow administrators to make ned leave the server
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        await ctx.send('Okilly-dokilly! 👋')
        await ctx.guild.leave()

    # Display the prefixes used on the current guild
    @commands.command(aliases=['prefixes'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def prefix(self, ctx):
        guild_prefixes = prefixes.prefixes_for(ctx.message.guild,
                                               self.bot.prefix_data)
        if len(guild_prefixes) > 7:
            await ctx.send('This servers prefixes are: `Ned`, `ned`, `diddly`' +
                           ', `doodly`,' + ' `diddly-`, `doodly-` and `' +
                           guild_prefixes[-1] + '`.')

        else:
            await ctx.send('This servers prefixes are: `Ned`, `ned`, `diddly`' +
                           ', `doodly`,' + ' `diddly-` and `doodly-`.')

    # Allows for a single custom prefix per-guild
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(3, 60, BucketType.guild)
    async def setprefix(self, ctx, *, new_prefix: str = None):
        guild_index = prefixes.find_guild(ctx.message.guild,
                                          self.bot.prefix_data)
        # Require entering a prefix
        if new_prefix is None:
            await ctx.send('You did not provide a new prefix.')

        # Limit prefix to 10 characters, may increase
        elif len(new_prefix) > 10:
            await ctx.send('Custom server prefix too long (Max 10 chars).')

        # Add a new custom guild prefix if one doesn't already exist
        elif guild_index == -1:
            self.bot.prefix_data.append(
                {'guildID': ctx.message.guild.id,
                 'prefix': new_prefix}
            )
            prefixes.write_prefixes(self.bot.prefix_data)
            await ctx.send('This servers custom prefix changed to `'
                           + new_prefix + '`.')

        elif self.bot.prefix_data[guild_index]['prefix'] == new_prefix:
            await ctx.send('This server custom prefix is already `' +
                           new_prefix + '`.')

        # Otherwise, modify the current prefix to the new one
        else:
            self.bot.prefix_data[guild_index]['prefix'] = new_prefix
            prefixes.write_prefixes(self.bot.prefix_data)
            await ctx.send('This servers custom prefix changed to `' +
                           new_prefix + '`.')

    # Toggle notifications for when user can vote again
    @commands.command(aliases=['reminder', 'subscribe'])
    @commands.cooldown(2, 30, BucketType.user)
    async def notifications(self, ctx):
        if ctx.author.id in self.bot.reminders:
            self.bot.reminders.remove(ctx.author.id)
            await self.dm_author(ctx, 'You will no longer be notified when you '
                                      'can vote again.')

        else:
            self.bot.reminders.append(ctx.author.id)
            try:
                await self.dm_author(ctx, 'Notifications enabled. You will be '
                                          'notified when you are able to vote.')

            except discord.Forbidden:
                await ctx.send('You have DMs disabled, please enable DMs if '
                               'you\'d like to enable notifications.')

            # Check if user is able to vote now
            query = '''SELECT MAX(voted_at) FROM vote_history
                       WHERE user_id = $1 AND vote_type = 'upvote';'''
            row = await self.bot.db.fetchrow(query, ctx.author.id)

            # No timestamps in history, notify and exit
            if row['max'] is None:
                await self.dm_author(ctx, VOTE_URL + '\n**You can vote now.**')

            else:
                # Calculate seconds until next vote
                time_diff = (datetime.utcnow() - row['max'])
                seconds_remaining = 43200 - time_diff.seconds

                # Voted over 12 hours ago, notify and exit
                if seconds_remaining <= 0:
                    await self.dm_author(ctx, VOTE_URL +
                                         '\n**You can vote now.**')

    @commands.command(aliases=['toggled'])
    async def toggle(self, ctx):
        if ctx.author.id not in self.bot.reminders:
            self.bot.reminders.append(ctx.author.id)

        else:
            self.bot.reminders.remove(ctx.author.id)


def setup(bot):
    bot.add_cog(General(bot))
