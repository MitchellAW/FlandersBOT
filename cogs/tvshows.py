import discord
from discord.ext import commands

import compuglobal


class TVShowCog(commands.Cog):
    def __init__(self, bot, api):
        self.bot = bot
        self.api = api

    # Get random or searched screencap based on search parameter and update cached_screencaps
    async def get_screencap(self, ctx, search=None):
        screencap = None
        try:
            if search is None:
                screencap = await self.api.get_random_screencap()

            else:
                screencap = await self.api.search_for_screencap(search)

            self.bot.cached_screencaps.update(
                {ctx.message.channel.id: screencap}
            )

        except compuglobal.APIPageStatusError as error:
            await self.bot.LOGGING.send(error)
            await ctx.send(error)

        except compuglobal.NoSearchResultsFound as error:
            await ctx.send(error)

        return screencap

    # Post a random screencap image with caption
    async def post_image(self, ctx, search=None, caption=None):
        screencap = await self.get_screencap(ctx, search)

        if screencap is not None:
            await ctx.send(await screencap.get_meme_url(caption))

    # Post a gif, if generating, post generating loading message and then edit message to include gif with the
    # generated url
    async def post_gif(self, ctx, search=None, caption=None, generate=True):
        screencap = await self.get_screencap(ctx, search)

        if screencap is not None:
            gif_url = await screencap.get_gif_url(caption)

            if generate:
                sent = await ctx.send(f'Generating {screencap.key}... <a:loading:410316176510418955>')

                try:
                    generated_url = await self.api.generate_gif(gif_url)
                    await sent.edit(content=generated_url)

                except compuglobal.APIPageStatusError as error:
                    await self.bot.LOGGING.send(error)
                    await ctx.send(error)

                except discord.NotFound:
                    pass

            else:
                await ctx.send(gif_url)
