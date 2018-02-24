import asyncio


class TVShowCog:
    def __init__(self, bot, api):
        self.bot = bot
        self.api = api

    # Post a random moment
    async def post_image(self, ctx, search_text=None, caption=None):
        if search_text is None:
            moment = await self.api.get_random_moment()

        else:
            moment = await self.api.search_for_moment(search_text)

        if moment is not None:
            ctx.bot.cached_moments.update({ctx.message.channel.id: moment})
            await ctx.send(moment.get_meme_url(caption))

    # Post generating message, generate gif then post generated Url
    async def post_gif(self, ctx, search_text=None, caption=None):
        if search_text is None:
            moment = await self.api.get_random_moment()

        else:
            moment = await self.api.search_for_moment(search_text)

        if moment is not None:
            ctx.bot.cached_moments.update({ctx.message.channel.id: moment})
            gif_url = await moment.get_gif_url(caption)
            sent = await ctx.send('Generating {}... '.format(moment.key)
                                  + '<a:loading:410316176510418955>')

            generated_url = await self.api.generate_gif(gif_url)
            await sent.edit(content=generated_url)

    # Ask user to post a custom caption, take custom caption and generate
    # custom gif, then delete request for caption and post custom gif
    async def post_custom_gif(self, ctx, search_text=None):
        first = await ctx.send('Please post the caption you would like to use',
                               delete_after=30)
        try:
            def check(message):
                return message.author == ctx.message.author

            resp = await self.bot.wait_for('message', check=check, timeout=30)
            await first.delete()
            await self.post_gif(ctx, search_text, resp.content)

        except asyncio.TimeoutError:
            pass
