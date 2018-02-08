import aiohttp

import settings.config

# Post guild count to update count at https://discordbots.org/
async def updateGuildCount(bot):
    dbUrl = "https://discordbots.org/api/bots/" + str(bot.user.id) + "/stats"
    dbHeaders = {"Authorization" : settings.config.DBTOKEN}
    dbPayload = {"server_count"  : len(bot.guilds)}

    async with aiohttp.ClientSession() as aioClient:
        resp = await aioClient.post(dbUrl, data=dbPayload, headers=dbHeaders)

# Get a list of user IDs who have upvoted FlandersBOT
async def getUpvoters():
    async with aiohttp.ClientSession() as aioClient:
        dbHeaders = {"Authorization" : settings.config.DBTOKEN}
        resp = await aioClient.get('https://discordbots.org/api/bots/221609683562135553/votes?onlyids=true', headers=dbHeaders)
        upvoters = await resp.json()
        return upvoters
