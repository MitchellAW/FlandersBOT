from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Prefixes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Display the prefixes used on the current guild
    @commands.command(aliases=['prefixes'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def prefix(self, ctx):
        # List default command prefixes
        message = 'My default prefixes are: '
        for i in range(len(self.bot.default_prefixes)):
            message += f'`{self.bot.default_prefixes[i]}`'

            # Follow message format of "prefix1, prefix2 and prefix3"
            if i < len(self.bot.default_prefixes) - 1:
                message += ', '

            if i == len(self.bot.default_prefixes) - 2:
                message += ' and '

        message += '.'

        # Display custom guild prefixes
        if ctx.guild.id in self.bot.cached_prefixes:
            guild_prefixes = self.bot.cached_prefixes[ctx.guild.id]

            message += '\nThis servers custom prefixes include: '

            # Loop through and add each custom prefix
            for i in range(len(guild_prefixes)):
                message += f'`{guild_prefixes[i]}`'

                # Follow message format of "prefix1, prefix2 and prefix3"
                if i == len(guild_prefixes) - 2:
                    message += ' and '

                elif i < len(guild_prefixes) - 1:
                    message += ', '

        # No custom prefixes found
        else:
            message += '\nThis server doesn\'t have any custom prefixes.'

        await ctx.send(message)

    # Allows for a single custom prefix per-guild
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(3, 60, BucketType.guild)
    async def addprefix(self, ctx, *, new_prefix: str = None):
        # Get custom prefixes for guild, gets empty list if none found
        current_prefixes = self.bot.cached_prefixes.get(ctx.guild.id, [])

        # Require entering a prefix
        if new_prefix is None:
            await ctx.send('You did not provide a new prefix.')

        # Limit prefix to 10 characters, may increase
        elif len(new_prefix) > 10:
            await ctx.send('Custom server prefix too long (Max 10 chars).')

        # Prevent adding default prefix as a custom prefix
        elif new_prefix in self.bot.default_prefixes:
            await ctx.send(f'This bot already supports `{new_prefix}` as a default prefix.')

        # Add custom prefix to DB
        elif new_prefix in current_prefixes:
            await ctx.send(f'This server already supports `{new_prefix.lower()}` as a custom prefix.')

        # Check if server is at custom prefix limit of 10 prefixes
        elif len(current_prefixes) >= 10:
            await ctx.send('Sorry, this server already has 10 custom prefixes. Use the command '
                           '`ned removeprefix <prefix>` to clear another prefix first.')

        # Insert new prefix into custom prefixes table and update cached prefixes
        else:
            query = '''INSERT INTO prefixes (guild_id, prefix)
                       VALUES ($1, $2)
                    '''
            await self.bot.db.execute(query, ctx.guild.id, new_prefix.lower())
            await self.bot.cache_prefixes()
            await ctx.send(f'This server now supports the custom prefix `{new_prefix.lower()}`.')

    # Allows removal of a specified custom server command prefix
    @commands.command(aliases=['deleteprefix', 'eraseprefix'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 3, BucketType.channel)
    async def removeprefix(self, ctx, *, old_prefix: str = None):
        if old_prefix is None:
            await ctx.send('You did not specify a prefix to remove')

        elif ctx.guild.id not in self.bot.cached_prefixes:
            await ctx.send('This server does not have any custom prefixes to remove.')

        elif old_prefix not in self.bot.cached_prefixes[ctx.guild.id]:
            await ctx.send(f'This server does not have `{old_prefix}` as a custom prefix.\n'
                           f'Use `ned prefix` for more info.')

        else:
            query = '''DELETE FROM prefixes
                       WHERE guild_id = $1 AND prefix = $2
                    '''

            await self.bot.db.execute(query, ctx.guild.id, old_prefix)
            await ctx.send(f'Removed {old_prefix} as a custom prefix.')
            await self.bot.cache_prefixes()

    # Allows removal of all custom server command prefixes
    @commands.command(aliases=['deleteprefixes', 'clearprefixes', 'eraseprefixes', 'purgeprefixes'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 3, BucketType.channel)
    async def removeprefixes(self, ctx):
        # Check server has any custom prefixes
        if ctx.guild.id not in self.bot.cached_prefixes:
            await ctx.send('This server does not have any custom prefixes to remove.')

        # Remove all custom prefixes
        else:
            query = '''DELETE FROM prefixes
                       WHERE guild_id = $1
                    '''
            await self.bot.db.execute(query, ctx.guild.id)
            await self.bot.cache_prefixes()
            await ctx.send('Removed all custom prefixes.')


def setup(bot):
    bot.add_cog(Prefixes(bot))
