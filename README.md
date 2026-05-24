![Flanders](https://github.com/MitchellAW/MitchellAW.github.io/blob/master/images/flanders-bannerBOT.png?raw=true)

# Flanders
![Python Versions](https://img.shields.io/pypi/pyversions/compuglobal.svg)
![Discord Support Server](https://img.shields.io/discord/403154226790006784?label=support)
![FlandersBOT License MIT](https://img.shields.io/github/license/MitchellAW/FlandersBOT)

### A bot for sharing your favourite references!

A discord bot with commands surrounding The Simpsons, Futurama, Rick and Morty and more!

Flanders provides commands for sharing gifs and comics from The Simpsons, Futurama and Rick and Morty. Flanders uses [Frinkiac](https://frinkiac.com/), [Morbotron](https://morbotron.com/) and [Master of All Science](https://masterofallscience.com/) to share the requested Simpsons, Futurama and Rick and Morty images/gifs with their subtitles.

## Add Flanders to your Discord Server

To view Flanders in Discord's application directory and more easily add Flanders to your own servers, [click here](https://discord.com/application-directory/221609683562135553).
To invite Flanders to your own discord server and start using it now, [click here](https://discordapp.com/oauth2/authorize?client_id=221609683562135553&scope=bot&permissions=281664)


## Usage
To share references from The Simpsons, Futurama, or Rick and Morty, you can use the `/simpsons`, `/futurama`, and `/rickandmorty` commands, followed by the quote that you'd like to search.

For example:

`/simpsons nothing at all`

`/futurama shut up and take my money`

`/rickandmorty you pass butter`

Then press the **Send Gif** or **Send Comic** button to share the reference in the channel!

> [!TIP]
> You can also edit the captions used in the gif/comic before sending by using the **Edit Captions** button!

## Preview
<img src="https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/flanders-preview-new.gif">

## Support Server
If you need any help with Flanders, would like to provide feedback, suggestions or have any other questions regarding Flanders, join the Flanders Support Server on discord:

[![Flanders Support](https://discordapp.com/api/guilds/403154226790006784/widget.png?style=banner2)](https://discord.gg/xMmxMYg)

## Requirements
I'd prefer that instead of running an instance of Flanders yourself you'd just [Invite Flanders](https://discordapp.com/oauth2/authorize?client_id=221609683562135553&scope=bot&permissions=19456) to your own server.
[Or go ahead anyway.](https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/refs/heads/master/images/im-a-sign-not-a-cop.jpg)

### Dependencies
*Requires Python 3.13+ and uv*

*Utilises the latest version of [discord.py](https://github.com/Rapptz/discord.py)*
*Depends upon [CompuGlobal](https://github.com/MitchellAW/CompuGlobal)*

*Requires PostgreSQL 17*

Building and running with docker recommended:

```sh
docker build -t flanders .
docker compose up -d
```

### Config
Update settings/config.json with required credentials.

## Database Setup

### Create Database
```sh
sudo -u postgres psql
```

```sql
CREATE ROLE ned WITH LOGIN PASSWORD '<password>';
CREATE DATABASE flandersdb OWNER ned;
```

### Create Tables
```sh
$ psql -h 127.0.0.1 -d flandersdb -U ned -f bot.sql
```


## Credits
**Creators of [Frinkiac](https://frinkiac.com/), [Morbotron](https://morbotron.com/), [Master of All Science](https://masterofallscience.com/), [GoodGod Lemon](https://goodgodlemon.com/) and [Capital Beat Us](https://capitalbeat.us/):**

[Paul Kehrer](https://twitter.com/reaperhulk)
[Sean Schulte](https://twitter.com/sirsean)
[Allie Young](https://twitter.com/seriousallie)
**Source of the higher quality Adventures of Ned Flanders image**
[/u/nmcfaden](https://i.redd.it/3m7txitrcjgy.png)
