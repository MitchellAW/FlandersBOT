import discord

commands_list = ('''
Hi-diddly-ho, neighborino! Here are the commands, shout them out anytime and
I'll happily oblige! Well, so long as the reverend approves of course.

**COMMAND PREFIXES**

`ned`, `diddly`, `doodly`

**COMMANDS**
*All commands must start with one of the command prefixes or 
<@221609683562135553>!*

**GENERAL**

**help** - Will send this list of commands.
**info** - Will send a personal message with more information about me.
**prefix** - Will post the prefixes I respond to on your server.
**setprefix [prefix]** - Sets a prefix I will respond to on your server.
**feedback [message]** - Send a feedback message or suggestions.
**invite** - Will post an invite link for me to join your server.
**vote** - Will post the benefits of voting for me and a link to vote.
**update** - Will post the highlights of my last major update.
**stats** - Will post some of my statist-diddly-istics.

**TV SHOWS**

**tvshows** - Will post a list of commands for all currently supported TV shows.

*I currently support commands for The Simpsons, Futurama, Rick and Morty, 
30 Rock and West Wing.*

**For Example:** `ned info`, `diddly help tvshows`, `doodly-simpsons`
''')

tv_shows = '''
**TV SHOWS**

**simpsons** - Will post a random Simpsons gif with caption.
**simpsons [quote]** - Searches for a Simpsons gif using the quote.
**simpsonstrivia** - Starts a game of trivia using 100+ Simpsons questions.

**futurama** - Will post a random Futurama gif with caption.
**futurama [quote]** - Searches for a Futurama gif using the quote.
**futuramatrivia** - Starts a game of trivia using 100+ Futurama questions.

**rickandmorty** - Will post a random Rick and Morty gif with caption.
**rickandmorty [quote]** - Searches for a Rick and Morty gif using the quote.

**30rock** - Will post a random 30 Rock gif with caption.
**30rock [quote]** - Searches for a 30 Rock gif using the quote.

**westwing** - Will post a random West Wing gif with caption.
**westwing [quote]** - Searches for a West Wing gif using the quote.

**For Example:** `ned info`, `diddly help`, `doodly-simpsons`
'''

bot_info = ('''Hi-diddly-ho, neighborino! I hear you wanted some 
mor-diddly-ore information...
Well, If it's clear and yella', you've got juice there, fella. If it's tangy 
and brown, you're in cider town.
Now, there's two exceptions and it gets kinda tricky here...

__**INFO**__

Framework: Discord.py (version=''' + discord.__version__ + ''')
Author: <@210898009242861568> (Discord)
Support Server: <https://discord.gg/xMmxMYg>
Invite URL: <https://discordapp.com/oauth2/authorize?client_id=''' +
            '''221609683562135553&scope=bot&permissions=19456>
GitHub Source: <https://github.com/MitchellAW/FlandersBOT>
If you'd like to hel-diddly-elp me grow in popularity, use `ned vote`
''')
