import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import api.dbl
from api.cartoons import CartoonAPI

class RickAndMorty():
    def __init__(self, bot):
        self.bot = bot
        self.masterOfAllScience = CartoonAPI('https://masterofallscience.com/')

    # Generate the gif and send it once the generation completes
    async def sendGif(self, ctx, gifUrl):
        upvoters = await api.dbl.getUpvoters()
        if str(ctx.message.author.id) in upvoters:
            sent = await ctx.send('Generating... <a:loading:410316176510418955>')
            generatedUrl = await self.masterOfAllScience.generateGif(gifUrl)
            await sent.edit(content=generatedUrl)

        else:
            await ctx.send(gifUrl)

    @commands.command(aliases=['Rickandmorty', 'RICKANDMORTY'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmorty(self, ctx, *, message : str=None):
        if message is None:
            await ctx.send(await self.masterOfAllScience.getRandomCartoon())

        else:
            gifUrl = await self.masterOfAllScience.findCartoonQuote(message, True)
            if 'https://' not in gifUrl:
                await ctx.send(gifUrl)

            else:
                await self.sendGif(ctx, gifUrl)

    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['Rickandmortygif', 'RICKANDMORTYGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortygif(self, ctx):
        gifUrl = await self.masterOfAllScience.getRandomCartoon(True)
        await self.sendGif(ctx, gifUrl)

def setup(bot):
    bot.add_cog(RickAndMorty(bot))
