# FlandersBOT
A discord bot built in python using the discord.py API with commands surrounding The Simpsons, Futurama and Rick and Morty.

FlandersBOT is entirely focused toward providing commands for The Simpsons, Futurama and Rick and Morty quotes/content. FlandersBOT uses Frinkiac, Morbotron and Master of All Science to provide commands for both random and searchable Simpsons, Futurama and Rick and Morty images/gifs with their appropriate quotes embedded.

## Invite URL
https://discordapp.com/oauth2/authorize?client_id=221609683562135553&scope=bot&permissions=19456

## Usage:
The bot commands can be executed with three methods/prefixes, to minimise clashing with other discord bots. The command can be prefixed with an exclamation point `!`, an @mention to the bot followed by a space `@FlandersBOT#0680 `, or an @mention to the bot followed by a space and an exclamation point `@FlandersBOT#0680 !`

**For example:**

`!info`  
`@FlandersBOT#0680 info`  
`@FlandersBOT#0680 !info`

*All three examples above are valid ways of executing any command below.*

## Commands
| Command | Description |
| --- | --- |
| info | Will send a personal message to the sender with more information   regarding the bot. (Framework, Author, invite URL etc.) |
| help | Will send a personal mesage to the sender with a list of the commands. |
| simpsons | Will post a random Simpsons quote with accompanying picture. |
| simpsons [quote to search for] | Searches for a Simpsons quote using all text following the command, grabs the first result and sends the resulting quote with accompanying gif. |
| simpsonsgif | Will post a random Simpsons quote with accompanying gif. |
| futurama | Will post a random Futurama quote with accompanying picture. |
| futurama [quote to search for] | Searches for a Futurama quote using all text following the command, grabs the first result and sends the resulting quote with accompanying gif. |
| futuramagif | Will post a random Futurama quote with accompanying gif. |
| rickandmorty | Will post a random Rick and Morty quote with accompanying picture. |
| rickandmorty [quote to search for] | Searches for a Rick and Morty quote using all text following the command, grabs the first result and sends the resulting quote with accompanying gif. |
| rickandmortygif | Will post a random Rick and Morty quote with accompanying gif. |

## Requirements
Requires discord.py to be installed.
The bot also depends entirely on https://frinkiac.com/, https://morbotron.com/ and https://masterofallscience.com/ for all of its commands and may fail if the API for these sites change.

## Support Server
https://discord.gg/xMmxMYg

![Flanders](https://MitchellAW.github.io/images/flanders.png)
