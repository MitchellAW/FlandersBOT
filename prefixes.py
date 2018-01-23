import asyncio
import discord
import json

# Find the index of the guild in prefixes.json
def findGuild(guild):
    if guild == None:
        return -1

    with open('prefixes.json', 'r') as guildList:
        data = json.load(guildList)
        for i in range(len(data)):
            if data[i]['guildID'] == guild.id:
                guildList.close()
                return i

        guildList.close()
    return -1

# Get all the prefixes the guild can use
async def prefixesFor(guild):
    guildIndex = findGuild(guild)
    if guildIndex == -1:
        return ['ned ', 'diddly-', 'doodly-', 'diddly ', 'doodly ']

    else:
        with open('prefixes.json', 'r') as guildList:
            guildData = json.load(guildList)
            guildList.close()

        customPrefix = guildData[guildIndex]['prefix']
        return ['ned ', 'diddly-', 'doodly-', 'diddly ', 'doodly', customPrefix]
