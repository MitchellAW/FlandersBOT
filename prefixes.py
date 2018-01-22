import asyncio
import discord
import json

# Find the index of the server in prefixes.json
def findServer(server):
    if server == None:
        return -1

    with open('prefixes.json', 'r') as serverList:
        data = json.load(serverList)
        for i in range(len(data)):
            if data[i]['serverID'] == server.id:
                serverList.close()
                return i

        serverList.close()
    return -1

# Get all the prefixes the server can use
async def prefixesFor(server):
    serverIndex = findServer(server)
    if serverIndex == -1:
        return ['ned ', 'diddly-', 'doodly-', 'diddly ', 'doodly ']

    else:
        with open('prefixes.json', 'r') as serverList:
            serverData = json.load(serverList)
            serverList.close()

        customPrefix = serverData[serverIndex]['prefix']
        return ['ned ', 'diddly-', 'doodly-', 'diddly ', 'doodly', customPrefix]
