import json

import asyncio

import aiohttp
import discord
from discord.ext import commands


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

    # Change the bot's status/presence to only cycle through given message
    @commands.command(hidden=True)
    @commands.is_owner()
    async def status(self, ctx, *, message: str):
        new_status = discord.Game(name=message.format(len(self.bot.guilds)))
        await self.bot.change_presence(activity=new_status)
        self.bot.status_formats = [message]
        await ctx.send('Status changed!')

    # Add a status/presence format to the status cycle
    @commands.command(hidden=True)
    @commands.is_owner()
    async def addstatus(self, ctx, *, message: str):
        self.bot.status_formats.append(message)
        await ctx.send('Status added!')

    # Resets the status/presence formats to cycle through two original formats
    @commands.command(hidden=True)
    @commands.is_owner()
    async def resetstatus(self, ctx):
        self.bot.status_formats = ['Ned vote | {} Servers',
                                   'Ned help | {} Servers']
        await ctx.send('Status reset!')

    # Get the number of all the commands executed
    @commands.command(hidden=True)
    @commands.is_owner()
    async def commandstats(self, ctx):
        command_count = ''
        for key in self.bot.command_stats:
            command_count += (key + ': ' + str(self.bot.command_stats[key]) +
                              '\n')

        await ctx.send(command_count)

    # Loads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    # Unloads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    # Reloads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    # Shuts the bot down - usable by the bot owner - requires confirmation
    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        # Make confirmation message based on bots username to prevent
        # myself from shutting wrong bot down.
        def check(message):
            return (message.content == self.bot.user.name[:4] and
                    message.author.id == self.bot.config['owner_id'])

        try:
            await ctx.send('Respond ' + self.bot.user.name[:4] + ' to shutdown')
            response = await self.bot.wait_for('message', check=check,
                                               timeout=10)
            await response.add_reaction('✅')
            await self.bot.db.close()
            await self.bot.logout()
            await self.bot.close()

        except asyncio.TimeoutError:
            pass

    # Generates a list of guilds the bot is in, contains name, bot and user
    # counts
    @commands.command(hidden=True)
    @commands.is_owner()
    async def guildlist(self, ctx):
        with open('cogs/data/guildlist.csv', 'w') as guild_list:
            guild_list.write('Server Name,# of Bots,# of Users,Total,Region,'
                             'Features\n')
            for guild in self.bot.guilds:
                bot_count = 0
                for member in guild.members:
                    if member.bot:
                        bot_count += 1

                # Write to csv file (guild name, bot count, user count,
                #  total member count)
                guild_list.write('"' + guild.name + '",' +
                                 str(bot_count) + ',' +
                                 str(len(guild.members) - bot_count) + ',' +
                                 str(len(guild.members)) + ',' +
                                 str(guild.region) + ',' +
                                 str(guild.features) + '\n')

        await ctx.send(file=discord.File('cogs/data/guildlist.csv'))

    # Reload config json file, allows regen of bot listing tokens without taking
    # bot down
    @commands.command(hidden=True)
    @commands.is_owner()
    async def reloadconfig(self, ctx):
        with open('settings/config.json', 'r') as config_file:
            self.bot.config = json.load(config_file)
            await ctx.message.add_reaction('✅')


def setup(bot):
    bot.add_cog(Owner(bot))
