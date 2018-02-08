import asyncio

import aiohttp
import discord
from discord.ext import commands

import settings.config

class Owner():

    def __init__(self, bot):
        self.bot = bot

    # Change the bot's avatar
    @commands.command()
    @commands.is_owner()
    async def avatar(self, ctx, avatarUrl):
        async with aiohttp.ClientSession() as aioClient:
            async with aioClient.get(avatarUrl) as resp:
                newAvatar = await resp.read()
                await self.bot.user.edit(avatar=newAvatar)
                await ctx.send('Avatar changed!')

    # Change the bot's status/presence
    @commands.command()
    @commands.is_owner()
    async def status(self, ctx, *, message : str):
        newStatus = discord.Game(name=message.format(len(self.bot.guilds)),
                          type=0)

        await self.bot.change_presence(game=newStatus, afk=True)
        self.bot.statusFormat = message

    # Sends a list of the guilds the bot is active in - usable by the bot owner
    @commands.command()
    @commands.is_owner()
    async def serverlist(self, ctx):
        guildList = ""
        for guild in self.bot.guilds:
            guildList += (guild.name + ' : ' + str(guild.region) + ' (' +
                          str(len(guild.members)) + ')\n')

        await ctx.author.send(guildList)

    # Get the number of all the commands executed
    @commands.command()
    @commands.is_owner()
    async def commandstats(self, ctx):
        commandCount = ''
        for key in self.bot.commandStats:
            commandCount += key + ': ' + str(self.bot.commandStats[key]) + '\n'

        await ctx.send(commandCount)

    # Loads a cog (requires dot path)
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    # Unloads a cog (requires dot path)
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    # Reloads a cog (requires dot path)
    @commands.command()
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
    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        # Make confirmation message based on bots username to prevent
        # myself from shutting wrong bot down.
        def check(message):
            return (message.content == self.bot.user.name[:4] and
                    message.author.id == settings.config.OWNERID)

        try:
            await ctx.send('Respond ' + self.bot.user.name[:4] +
                           ' to shutdown')

            response = await self.bot.wait_for('message', check=check,
                                               timeout=10)
            await response.add_reaction('✅')
            await self.bot.logout()
            await self.bot.close()

        except asyncio.TimeoutError:
            pass

def setup(bot):
    bot.add_cog(Owner(bot))

