import botInfo
import settings.config
import discord
import json
import prefixes

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class General():
    def __init__(self, bot):
        self.bot = bot

    # Whispers a description of the bot with author, framework, server count etc.
    @commands.command()
    async def info(self):
        await self.bot.whisper((botInfo.botInfo + '\n***Currently active in '
                          + str(len(self.bot.servers)) + ' servers***'))

    # Whispers a list of the bot commands
    @commands.command()
    async def help(self):
        await self.bot.whisper(botInfo.commandsList)

    # Display the prefixes used on the current server
    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, BucketType.channel)
    async def prefix(self, ctx):
        serverPrefixes = await prefixes.prefixesFor(ctx.message.server)
        if len(serverPrefixes) > 5:
            await self.bot.say('This servers prefixes are: `ned`, `diddly`,' +
                               ' `doodly`,' + ' `diddly-`, `doodly-` and `' +
                               serverPrefixes[-1] + '`.' )

        else:
            await self.bot.say('This servers prefixes are `ned`, `diddly`, ' +
                               '`doodly`,' + ' `diddly-` and `doodly-`.')

    # Allows for a single custom prefix per-server
    @commands.command(pass_context=True)
    @commands.has_permissions(manage_server=True)
    @commands.cooldown(3, 60, BucketType.server)
    async def setprefix(self, ctx, *, message : str=None):
        serverIndex = prefixes.findServer(ctx.message.server)

        # Only allow custom prefixes in servers
        if ctx.message.server is None:
            await self.bot.say('Custom prefixes are for servers only.')

        # Require entering a prefix
        if message is None:
            await self.bot.say('You did not provide a new prefix.')

        # Limit prefix to 10 characters, may increase
        elif len(message) > 10:
            await self.bot.say('Custom server prefix too long (Max 10 chars).')

        else:
            # Write the new custom prefix
            with open('prefixes.json', 'r') as serverList:
                data = json.load(serverList)
                serverList.close()

            # Declare if it is already that prefix
            if data[serverIndex]['prefix'] == message:
                await self.bot.say('This servers custom prefix is already `' +
                                   message + '`.')

            else:
                # Add a new custom server prefix if one doesn't already exist
                if serverIndex == -1:
                    data.append({'serverID':ctx.message.server.id,
                                'prefix':message})

                # Otherwise, modify the current prefix to the new one
                else:
                    data[serverIndex]['prefix'] = message

                # Write the new prefix to the file
                with open('prefixes.json', 'w') as serverList:
                    json.dump(data, serverList, indent=4)
                    serverList.close()
                    await self.bot.say('This servers custom prefix changed to `'
                                       + message + '`.')


    @commands.command(pass_context=True)
    async def status(self, ctx, *, message : str):
        if ctx.message.author.id == settings.config.OWNERID:
            await self.bot.change_presence(game=discord.Game(name=message,
                                                             type=0))

    # Sends a list of the servers the bot is active in - usable by the bot owner
    @commands.command(pass_context=True)
    async def serverlist(self, ctx):
        if ctx.message.author.id == settings.config.OWNERID:
            serverList = ""
            for server in self.bot.servers:
                serverList += server.name + '\n'
            await self.bot.whisper(serverList)

    # Shuts the bot down - usable by the bot owner
    @commands.command(pass_context=True)
    async def shutdown(self, ctx):
        if ctx.message.author.id == settings.config.OWNERID:
            await self.bot.logout()
            await self.bot.close()

    # Display statistics for the bot
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def stats(self):

        # Get server count
        serverCount = len(self.bot.servers)

        # Count users online in servers
        totalMembers = 0
        onlineUsers = 0
        for server in self.bot.servers:
            totalMembers += len(server.members)
            for member in server.members:
                if member.status == discord.Status.online:
                    onlineUsers += 1

        averageOnline = round((onlineUsers / serverCount), 2)

        # Embed statistics output
        embed = discord.Embed(colour=discord.Colour(0x44981e))
        embed.set_thumbnail(url="https://images.discordapp.net/avatars/221609683562135553/afc35c7bcaf6dcb1c86a1c715ac955a3.png")
        embed.set_author(name="FlandersBOT Statistics", url="https://github.com/FlandersBOT", icon_url="https://images.discordapp.net/avatars/221609683562135553/afc35c7bcaf6dcb1c86a1c715ac955a3.png")
        embed.add_field(name="Bot Name", value="FlandersBOT#0680", inline=True)
        embed.add_field(name="Bot Owner", value="Mitch#8293", inline=True)
        embed.add_field(name="Total Members", value=str(totalMembers), inline=True)
        embed.add_field(name="Server Count", value=str(serverCount), inline=True)
        embed.add_field(name="Online Users", value=str(onlineUsers), inline=True)
        embed.add_field(name="Online Users per Server", value=str(averageOnline), inline=True)

        # Post statistics
        await self.bot.say(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))
