![Flanders](https://github.com/MitchellAW/MitchellAW.github.io/blob/master/images/flanders-bannerBOT.png?raw=true)

# FlandersBOT
### A bot for sharing your favourite references! 

A discord bot with commands surrounding The Simpsons, Futurama, Rick and Morty and more!

FlandersBOT provides commands for The Simpsons, Futurama and Rick and Morty quoting/searching/content. FlandersBOT uses [Frinkiac](https://frinkiac.com/), [Morbotron](https://morbotron.com/) and [Master of All Science](https://masterofallscience.com/) to provide commands for both random and searchable Simpsons, Futurama and Rick and Morty images/gifs with their appropriate quotes embedded.

## Add FlandersBOT to your Discord Server
<img align="right" src="https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/flanders-cirlce.png?raw=true" height="256" width="256"></img>

To invite FlandersBOT to your own discord server and start using it now, [click here](https://discordapp.com/oauth2/authorize?client_id=221609683562135553&scope=bot&permissions=19456)

Thanks to https://discordbots.org/ for listing FlandersBOT!  
If you like FlandersBOT, help the bot grow by voting [here](https://discordbots.org/bot/221609683562135553/vote)


<a href="https://discordbots.org/bot/221609683562135553" >
  <img src="https://discordbots.org/api/widget/221609683562135553.svg" alt="Discord Music Bot" />
</a>

## Requirements
I'd prefer that instead of running an instance of FlandersBOT yourself you'd just [invite FlandersBOT](https://discordapp.com/oauth2/authorize?client_id=221609683562135553&scope=bot&permissions=19456) to your own server.   
[Or go ahead anyway.](https://i.imgur.com/mSHi8.jpg)

### Dependencies
*Requires Python 3.5+*  
`python3 -m pip install -U -r requirements.txt`

*Utilises the latest version of [discord.py](https://github.com/Rapptz/discord.py) *  
*Depends upon [CompuGlobal](https://github.com/MitchellAW/CompuGlobal/tree/async)*

*Requires PostgreSQL 9.6+*  
```sh
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install postgresql
```  

*Requires Node.js v11.6+ for dbl webhook*
```sh
$ npm install dblapi.js
$ npm install pg
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

## Usage
The bot commands can be executed using several different methods/prefixes, to minimise clashing with other discord bots. Any command can be prefixed with an @mention, ned or diddly/doodly when you really want to flaunt those Flanders-isms.

If you're not a fan of any of these prefixes, you can add a new prefix to your server using the setprefix command. (Requires Manage Server Pemissions)

**Usage Examples:**

`@FlandersBOT#0680 info`  
`ned info`  
`diddly info`  
`doodly info`  
`diddly-info`  
`doodly-info`

*All examples above are valid methods of executing any command below.*

## Commands

### General

<div style="overflow-x:auto;">
  <table width=180 style='table-layout:fixed'>
    <col width=20>
 	<col width=100>
    <thead>
      <tr>
        <th>Command</th>
        <th>Description</th>
      </tr>
    </thead>
    <tr>
      <td><b>help</b></td>
      <td>Will send a personal message with a list of the commands.</td>
    </tr>
    <tr>
      <td><b>info</b></td>
      <td>Will send a personal message with more information about the bot.</td>
    </tr>
    <tr>
      <td><b>prefix</b></td>
      <td>Will post the prefixes FlandersBOT responds to on your server.</td>
    </tr>
    <tr>
      <td><b>setprefix [prefix]</b></td>
      <td>Sets a prefix FlandersBOT will respond to on your server. (Manage Server Pemissions)</td>
    </tr>
    <tr>
      <td><b>feedback</b></td>
      <td>Send a feedback message or suggestions.</td>
    </tr>
    <tr>
      <td><b>stats</b></td>
      <td>Will post some of FlandersBOT's statistics.</td>
    </tr>
    <tr>
      <td><b>notifications</b></td>
      <td>Toggle notifications for when you are able to vote.</td>
    </tr>
    <tr>
      <td><b>epinfo</b></td>
      <td>Will post episode information on the last post made by FlandersBOT in the channel.</td>
    </tr>
    <tr>
      <td><b>meme [caption]</b></td>
      <td>Will repost the last gif made by FlandersBOT in the channel with the new caption.</td>
    </tr>
  </table>
</div>

### Simpsons

<div style="overflow-x:auto;">
  <table width=180 style='table-layout:fixed'>
    <col width=20>
 	<col width=100>
    <thead>
      <tr>
        <th>Command</th>
        <th>Description</th>
      </tr>
    </thead>
    <tr>
      <td><b>simpsons</b></td>
      <td>Will post a random Simpsons gif with caption.</td>
    </tr>
    <tr>
      <td><b>simpsons [quote]</b></td>
      <td>Searches for a Simpsons gif using the quote.</td>
    </tr>
    <tr>
      <td><b>simpsonstrivia</b></td>
      <td>Will start a game of trivia using 100+ questions</td>
    </tr>
  </table>
</div>

### Futurama

<div style="overflow-x:auto;">
  <table width=180 style='table-layout:fixed'>
    <col width=20>
 	<col width=100>
    <thead>
      <tr>
        <th>Command</th>
        <th>Description</th>
      </tr>
    </thead>
    <tr>
      <td><b>futurama</b></td>
      <td>Will post a random Futurama gif with caption.</td>
    </tr>
    <tr>
      <td><b>futurama [quote]</b></td>
      <td>Searches for a Futurama gif using the quote.</td>
    </tr>
    <tr>
      <td><b>futuramatrivia</b></td>
      <td>Will start a game of trivia using 100+ questions</td>
    </tr>
  </table>
</div>

### Rick and Morty

<div style="overflow-x:auto;">
  <table width=180 style='table-layout:fixed'>
    <col width=20>
 	<col width=100>
    <thead>
      <tr>
        <th>Command</th>
        <th>Description</th>
      </tr>
    </thead>
    <tr>
      <td><b>rickandmorty</b></td>
      <td>Will post a random Rick and Morty gif with caption.</td>
    </tr>
    <tr>
      <td><b>rickandmorty [quote]</b></td>
      <td>Searches for a Rick and Morty gif using the quote.</td>
    </tr>
  </table>
</div>

## Preview
<img src="https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/flanders-preview.gif" width="450" height="350">


## Support Server
If you need any help with FlandersBOT, would like to provide feedback, suggestions or have any other questions regarding FlandersBOT, join the FlandersBOT Support Server on discord:

[![FlandersBOT Support](https://discordapp.com/api/guilds/403154226790006784/widget.png?style=banner2)](https://discord.gg/xMmxMYg)


## Credits
**Creators of [Frinkiac](https://frinkiac.com/), [Morbotron](https://morbotron.com/), [Master of All Science](https://masterofallscience.com/), [GoodGod Lemon](https://goodgodlemon.com/) and [Capital Beat Us](https://capitalbeat.us/):**

[Paul Kehrer](https://twitter.com/reaperhulk)
[Sean Schulte](https://twitter.com/sirsean)  
[Allie Young](https://twitter.com/seriousallie)  
**Source of the higher quality Adventures of Ned Flanders image**  
[/u/nmcfaden](https://i.redd.it/3m7txitrcjgy.png)
