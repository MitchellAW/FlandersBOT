import logging

import discord
from discord.ext import commands
from tabulate import tabulate

from flanders.bot import FlandersBOT

log = logging.getLogger(__name__)


class Owner(commands.Cog):
    def __init__(self, bot: FlandersBOT) -> None:
        self.bot = bot

    # Get the number of all the commands executed
    @commands.command(name="history", hidden=True)
    @commands.is_owner()
    async def command_history(self, ctx: commands.Context, *, modifier: str | None = None) -> None:
        # Get command counts ordered alphabetically
        query = """SELECT command, COUNT(command) AS command_count FROM command_history
                    WHERE failed = false AND ($1::text IS NULL or prefix = $1)
                    GROUP BY command
                    ORDER BY command
                """

        rows = await self.bot.db.fetch(query, modifier)

        # Display each command stats on separate line and format using tabulate
        command_data = ([row["command"], row["command_count"]] for row in rows)
        message = tabulate(command_data, headers=["Command Name", "Count"], tablefmt="presto", colalign=("right",))
        await ctx.send(f"```{message}```")

    # Loads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def load(self, ctx: commands.Context, *, cog: str) -> None:
        try:
            await self.bot.load_extension(cog)
        except Exception:
            await ctx.message.add_reaction("❌")
            log.exception("Error loading extension")
        else:
            await ctx.message.add_reaction("✅")

    # Unloads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def unload(self, ctx: commands.Context, *, cog: str) -> None:
        try:
            await self.bot.unload_extension(cog)
        except Exception:
            await ctx.message.add_reaction("❌")
            log.exception("Error unloading extension")
        else:
            await ctx.message.add_reaction("✅")

    # Reloads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def reload(self, ctx: commands.Context, *, cog: str) -> None:
        try:
            await self.bot.unload_extension(cog)
            await self.bot.load_extension(cog)
        except Exception:
            await ctx.message.add_reaction("❌")
            log.exception("Error reloading extension")
        else:
            await ctx.message.add_reaction("✅")

    # Manually syncs commands to the guild, or globally if followed by global
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, *, globe: str | None = None) -> None:
        if ctx.guild is None:
            return

        guild = discord.Object(id=ctx.guild.id)
        self.bot.tree.copy_global_to(guild=guild)

        if globe == "global":
            synced = await ctx.bot.tree.sync()
        else:
            synced = await ctx.bot.tree.sync(guild=ctx.guild)

        await ctx.send(f"Synced {len(synced)} commands {'globally' if globe == 'global' else 'to the current guild.'}")

    # Manually unsyncs all commands from the guild, or globally if followed by global
    @commands.command()
    @commands.is_owner()
    async def unsync(self, ctx: commands.Context, *, globe: str | None = None) -> None:
        if ctx.guild is None:
            return

        guild = discord.Object(id=ctx.guild.id)
        self.bot.tree.clear_commands(guild=guild)
        if globe == "global":
            await ctx.bot.tree.sync()

        else:
            await ctx.bot.tree.sync(guild=ctx.guild)

        await ctx.send(f"Unsynced commands {'globally' if globe == 'global' else 'to the current guild.'}")

    # Shuts the bot down - usable by the bot owner - requires confirmation
    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def shutdown(self, ctx: commands.Context) -> None:
        # Make confirmation message based on bots username to prevent myself from shutting wrong bot down.
        def check(message: discord.Message) -> bool:
            return message.author.id == self.bot.config.owner_id

        try:
            await ctx.send("Reply in 10 seconds to shutdown.", delete_after=10)
            response = await self.bot.wait_for("message", check=check, timeout=10)
            await response.add_reaction("✅")
            await self.bot.db.close()
            await self.bot.close()

        except TimeoutError:
            pass


async def setup(bot: FlandersBOT) -> None:
    await bot.add_cog(Owner(bot))
