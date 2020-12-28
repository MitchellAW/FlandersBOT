import json


def read_prefixes():
    with open('cogs/data/prefixes.json', 'r') as prefix_list:
        prefix_data = json.load(prefix_list)
        prefix_list.close()

    return prefix_data


# Writes the prefix to prefixes.json
def write_prefixes(prefix_data):
    # Write the new prefix to the file
    with open('cogs/data/prefixes.json', 'w') as prefix_list:
        json.dump(prefix_data, prefix_list, indent=4)
        prefix_list.close()


# Find the index of the guild in prefixes.json
def find_guild(guild, prefix_data):
    if guild is None:
        return -1

    for i in range(len(prefix_data)):
        if prefix_data[i]['guildID'] == guild.id:
            return i

    return -1


# Get all the prefixes the guild can use
def prefixes_for(guild, prefix_data):
    guild_index = find_guild(guild, prefix_data)
    if guild_index == -1:
        return [
            'ned ', 'Ned ', 'NED ', 'diddly-', 'doodly-', 'diddly ', 'doodly '
        ]

    else:
        custom_prefix = prefix_data[guild_index]['prefix']
        return [
            'ned ', 'Ned ', 'NED ', 'diddly-', 'doodly-', 'diddly ', 'doodly ', custom_prefix
        ]
