import discord

commandsList = '''
Hi-diddly-ho, neighborino! Here are the commands, shout them out anytime and I'll
happily oblige! Well, so long as the reverend approves of course.

__**COMMANDS**__

`!help`
Will send a personal mesage to the sender with a list of the commands.

`!info`
Will send a personal message to the sender with more information regarding the bot.
(Framework, Author, invite URL etc.)

`!simpsons`
Will post a random Simpsons quote with accompanying picture.

`!simpsons [quote to search for]`
Searches for a Simpsons quote using all text following the command, grabs the first result and sends the resulting quote with accompanying gif.

`!simpsonsgif`
Will post a random Simpsons quote with accompanying gif.

`!futurama`
Will post a random Futurama quote with accompanying picture.

`!futurama [quote to search for]`
Searches for a Futurama quote using all text following the command, grabs the first result and sends the resulting quote with accompanying gif.

`!futuramagif`
Will post a random Futurama quote with accompanying gif.

`!rickandmorty`
Will post a random Rick and Morty quote with accompanying picture.

`!rickandmorty [quote to search for]`
Searches for a Rick and Morty quote using all text following the command, grabs the first result and sends the resulting quote with accompanying gif.

`!rickandmortygif`
Will post a random Rick and Morty quote with accompanying gif.
'''

botInfo = ('''Hi-diddly-ho, neighborino! I hear you wanted some more information...
Well, If it's clear and yella', you've got juice there, fella.
If it's tangy and brown, you're in cider town.
Now, there's two exceptions and it gets kinda tricky here...

Framework: Discord.py (version=''' + discord.__version__ + ''')
Author: Mitch#8293 (Discord)
Invite URL: <https://discordapp.com/api/oauth2/authorize?client_id=221609683562135553&permissions=0&scope=bot>
GitHub Source: https://github.com/MitchellAW/FlandersBOT''')
