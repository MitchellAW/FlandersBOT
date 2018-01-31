import asyncio
import discord
import json

def readPrefixes():
    with open('cogs/data/prefixes.json', 'r') as prefixList:
        prefixData = json.load(prefixList)
        prefixList.close()

    return prefixData

# Writes the prefix to prefixes.json
def writePrefixes(prefixData):
    # Write the new prefix to the file
    with open('cogs/data/prefixes.json', 'w') as guildList:
        json.dump(prefixData, guildList, indent=4)
        guildList.close()

# Find the index of the guild in prefixes.json
def findGuild(guild, prefixData):
    if guild == None:
        return -1

    for i in range(len(prefixData)):
        if prefixData[i]['guildID'] == guild.id:
            return i

    return -1

# Get all the prefixes the guild can use
async def prefixesFor(guild, prefixData):
    guildIndex = findGuild(guild, prefixData)
    if guildIndex == -1:
        return [
        'ned ', 'Ned ', 'NED ', 'diddly-', 'doodly-', 'diddly ', 'doodly '
        ]

    else:
        customPrefix = prefixData[guildIndex]['prefix']
        return [
        'ned ', 'Ned ', 'NED ', 'diddly-', 'doodly-', 'diddly ', 'doodly',
        customPrefix
        ]
