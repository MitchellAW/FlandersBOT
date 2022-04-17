import random

import compuglobal
import discord
from compuglobal.aio import Frinkiac
from compuglobal.aio import FrinkiHams
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from cogs.tvshows import TVShowCog
from cogs.events import Events


class Simpsons(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Frinkiac())
        self.frinkihams = FrinkiHams()
        self.frinkiac = Frinkiac()

    # Messages a random Simpsons quote with gif if no search terms are given, otherwise, search for Simpsons quote using
    # search terms and post gif
    @commands.command(aliases=['simpsonsgif', 'simpson', 'sgif'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def simpsons(self, ctx, *, search_terms: str = None):
        # Handle possible custom captions
        if search_terms is not None and ' | ' in search_terms:
            args = search_terms.split(' | ', 1)
            await self.post_gif(ctx, args[0], args[1])

        # Use default caption
        else:
            await self.post_gif(ctx, search_terms)

    # Generate a random Steamed Hams gif and post it
    @commands.command(aliases=['steamed', 'steam', 'hams', 'ham', 'aurora', 'borealis', 'frinkiac', 'frink'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def steamedhams(self, ctx):
        # Steamed hams episode key
        steamed_hams_key = 'S07E21'

        # The middle timestamp of the skit  (start: 483532, end: 652200)
        middle_timestamp = 567866

        # Send gif generation message, will be later edited to display generated gif url
        emoji = await Events.use_emoji(ctx, '<a:loading:410316176510418955>', '⌛ ')
        sent = await ctx.send(f'Steaming your hams... {emoji}')

        # Get all frames for the steamed hams skit
        # Skit duration is 2:48 (168 seconds), get frames 80 seconds before and 80 seconds after mid point
        # 4 seconds are subtracted from start and end to allow for 7 second gif length and prevent displaying parts of
        # other skits
        try:
            frames = await self.frinkiac.get_frames(steamed_hams_key, middle_timestamp, 80000, 80000)

            # Check frames are returned
            if len(frames) > 0:
                steamed_ham = random.choice(frames)
                screencap = await self.frinkiac.get_screencap(steamed_hams_key, steamed_ham.timestamp)

                # Ensure valid screencap
                if screencap is not None:
                    gif_url = await screencap.get_gif_url()

                    # Generate the gif and replace loading message with generated url
                    generated_url = await self.frinkiac.generate_gif(gif_url)
                    await sent.edit(content=generated_url)

        except compuglobal.APIPageStatusError as error:
            await sent.edit(content=TVShowCog.format_error(error))

        except discord.NotFound:
            pass


async def setup(bot):
    await bot.add_cog(Simpsons(bot))
