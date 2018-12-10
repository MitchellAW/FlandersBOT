import aiohttp

import settings.config


# Post guild count to update count for either discordbots.org or bots.discord.pw
async def update_guild_count(bot, url, token):
    if 'bots.discord.pw' in url:
        url += 'api/v1/bots/' + str(bot.user.id) + '/stats'
    else:
        url += 'api/bots/' + str(bot.user.id) + '/stats'
    headers = {"Authorization": token}
    payload = {"server_count": len(bot.guilds)}

    async with aiohttp.ClientSession() as session:
        if 'bots.discord.pw' in url:
            await session.post(url, json=payload, headers=headers, timeout=15)

        else:
            await session.post(url, data=payload, headers=headers, timeout=15)


# Get a list of user IDs who have upvoted FlandersBOT
async def get_upvoters():
    async with aiohttp.ClientSession() as aio_client:
        db_headers = {"Authorization": settings.config.DB_TOKEN}
        resp = await aio_client.get('https://discordbots.org/api/bots/2216096' +
                                    '83562135553/votes?onlyids=true',
                                    headers=db_headers)
        if resp.status == 200:
            upvoters = await resp.json()
            return upvoters

        else:
            return []
