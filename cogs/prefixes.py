from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Prefixes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Display the prefixes used on the current guild
    @commands.command(aliases=['prefixes', 'add-prefix', 'setprefix', 'addprefix', 'set-prefix'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def prefix(self, ctx):
        message = f'I can only respond to commands starting with {self.bot.user.mention}.'
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Prefixes(bot))
