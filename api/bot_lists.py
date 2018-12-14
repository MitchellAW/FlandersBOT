import aiohttp


# Post guild count to update count for bot_listing sites
async def update_guild_counts(bot):
    for listing in bot.config['bot_listings']:
        async with aiohttp.ClientSession() as session:
            url = listing['url'].format(str(bot.user.id))
            data = {
                listing['payload']['guild_count']: len(bot.guilds)
            }
            headers = listing['headers']

            # Check if api needs payload posted as data or json
            if listing['posts_data']:
                await session.post(url, data=data, headers=headers, timeout=15)

            else:
                await session.post(url, json=data, headers=headers, timeout=15)
