import aiohttp

import settings.config


# Post guild count to update count at https://discordbots.org/
async def update_guild_count(bot):
    db_url = "https://discordbots.org/api/bots/" + str(bot.user.id) + "/stats"
    db_headers = {"Authorization" : settings.config.DBTOKEN}
    db_payload = {"server_count": len(bot.guilds)}

    async with aiohttp.ClientSession() as aio_client:
        await aio_client.post(db_url, data=db_payload, headers=db_headers)


# Get a list of user IDs who have upvoted FlandersBOT
async def get_upvoters():
    async with aiohttp.ClientSession() as aio_client:
        db_headers = {"Authorization" : settings.config.DBTOKEN}
        resp = await aio_client.get('https://discordbots.org/api/bots/2216096' +
                                    '83562135553/votes?onlyids=true',
                                    headers=db_headers)
        if resp.status == 200:
            upvoters = await resp.json()
            return upvoters
