import dbl
import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Simpsons():
    def __init__(self, bot):
        self.bot = bot
        self.frinkiac = CartoonAPI('https://frinkiac.com/')

    # Generate the gif and send it once the generation completes
    async def sendGif(self, ctx, gifUrl):
        upvoters = await dbl.getUpvoters()
        if str(ctx.message.author.id) in upvoters:
            sent = await ctx.send('Generating... <a:loading:410316176510418955>')
            generatedUrl = await self.frinkiac.generateGif(gifUrl)
            await sent.edit(content=generatedUrl)

        else:
            await ctx.send(gifUrl)

    @commands.command(aliases=['Simpsons', 'SIMPSONS'])
    #@commands.cooldown(1, 3, BucketType.channel)
    async def simpsons(self, ctx, *, message : str=None):
        if message is None:
            await ctx.send(await self.frinkiac.getRandomCartoon())

        else:
            gifUrl = await self.frinkiac.findCartoonQuote(message, True)
            if 'https://' not in gifUrl:
                await ctx.send(gifUrl)

            else:
                await self.sendGif(ctx, gifUrl)

    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['Simpsonsgif', 'SIMPSONSGIF'])
    #@commands.cooldown(1, 3, BucketType.channel)
    async def simpsonsgif(self, ctx):
        upvoters = await dbl.getUpvoters()
        hasUpvoted = str(ctx.message.author.id) in upvoters
        gifUrl = await self.frinkiac.getRandomCartoon(True)
        await self.sendGif(ctx, gifUrl)

def setup(bot):
    bot.add_cog(Simpsons(bot))

