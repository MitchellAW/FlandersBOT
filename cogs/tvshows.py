import asyncio

import compuglobal


class TVShowCog:
    def __init__(self, bot, api):
        self.bot = bot
        self.api = api

    # Post a random screencap
    async def post_image(self, ctx, search=None, caption=None):
        if search is None:
            screencap = await self.api.get_random_screencap()

        else:
            try:
                screencap = await self.api.search_for_screencap(search)

            except compuglobal.APIPageStatusError as error:
                await ctx.send(error)
                return

            except compuglobal.NoSearchResultsFound as error:
                await ctx.send(error)
                return

        if screencap is not None:
            ctx.bot.cached_screencaps.update(
                {ctx.message.channel.id: screencap}
            )
            await ctx.send(screencap.get_meme_url(caption))

    # Post a gif, if generating, post generating loading message and then edit
    # message to include gif with the generated url
    async def post_gif(self, ctx, search=None, caption=None, generate=True):
        if search is None:
            screencap = await self.api.get_random_screencap()

        else:
            try:
                screencap = await self.api.search_for_screencap(search)

            except compuglobal.APIPageStatusError as error:
                await ctx.send(error)
                return

            except compuglobal.NoSearchResultsFound as error:
                await ctx.send(error)
                return

        if screencap is not None:
            ctx.bot.cached_screencaps.update(
                {ctx.message.channel.id: screencap}
            )
            gif_url = await screencap.get_gif_url(caption)

            if generate:
                sent = await ctx.send('Generating {}... '.format(screencap.key)
                                      + '<a:loading:410316176510418955>')
                generated_url = await self.api.generate_gif(gif_url)
                await sent.edit(content=generated_url)

            else:
                await ctx.send(gif_url)

    # Ask user to post a custom caption, take custom caption and generate
    # custom gif, then delete request for caption and post custom gif
    async def post_custom_gif(self, ctx, search=None):
        first = await ctx.send('Please post the caption you would like to use',
                               delete_after=30)
        try:
            def check(message):
                return message.author == ctx.message.author

            resp = await self.bot.wait_for('message', check=check, timeout=30)
            await first.delete()
            await self.post_gif(ctx, search, resp.content)

        except asyncio.TimeoutError:
            pass
