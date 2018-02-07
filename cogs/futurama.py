import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Futurama():
    def __init__(self, bot):
        self.bot = bot
        self.morbotron = CartoonAPI('https://morbotron.com/')

    # Generate the gif and send it once the generation completes
    async def sendGif(self, ctx, gifUrl):
        sent = await ctx.send('Generating... <a:loading:410316176510418955>')
        generatedUrl = await self.morbotron.generateGif(gifUrl)
        await sent.edit(content=generatedUrl)

    @commands.command(aliases=['Futurama', 'FUTURAMA'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futurama(self, ctx, *, message : str=None):
        if message is None:
            await ctx.send(await self.morbotron.getRandomCartoon())

        else:
            gifUrl = await self.morbotron.findCartoonQuote(message, True)
            if 'https://' not in gifUrl:
                await ctx.send(gifUrl)

            else:
                await self.sendGif(ctx, gifUrl)


    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['Futuramagif', 'FUTURAMAGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futuramagif(self, ctx):
        gifUrl = await self.morbotron.getRandomCartoon(True)
        await self.sendGif(ctx, gifUrl)


def setup(bot):
    bot.add_cog(Futurama(bot))

