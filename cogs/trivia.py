import asyncio
import json
import random
import time

import discord
from discord.ext import commands


class Trivia:
    def __init__(self, bot):
        self.bot = bot
        self.channels_playing = []

    # Starts a game of trivia using fileName as the questions file
    async def start_trivia(self, ctx, file_name, category_colour,
                           thumbnail_url):
        self.channels_playing.append(ctx.channel.id)
        with open('cogs/data/' + file_name, 'r') as trivia_questions:
            trivia_data = json.load(trivia_questions)
            random.shuffle(trivia_data)
            trivia_questions.close()

        still_playing = True
        while still_playing and len(trivia_data) > 0:
            # Gather all question information needed
            question_data = trivia_data.pop()
            question = question_data['question']
            answers = question_data['answers']
            correct_answer = answers[0]

            # Shuffle answers, by default correct answer is always first
            random.shuffle(answers)
            correct_choice = chr(answers.index(correct_answer) + 65)

            answer_msg = ('**A:** {}\n**B:** {}\n**C:** {} \n\nSend a letter ' +
                          'below to answer!').format(answers[0],
                                                     answers[1],
                                                     answers[2])

            embed = discord.Embed(title=question,
                                  colour=category_colour,
                                  description=answer_msg)
            embed.set_thumbnail(url=thumbnail_url)

            # Send the trivia question
            await ctx.send(embed=embed)

            # Check for confirming an answer was made (case-insensitive)
            def is_answer(message):
                return message.content.upper() in ['A', 'B', 'C']

            # Wait for answers from users for 10 secs, storing all answers
            answers = {}
            end_time = time.time() + 15
            try:
                while time.time() < end_time:
                    message = await self.bot.wait_for('message',
                                                      check=is_answer,
                                                      timeout=(end_time -
                                                               time.time()))

                    if message.author.id not in answers:
                        answers.update({message.author:
                                        message.content.upper()})

            except asyncio.TimeoutError:
                pass

            # Count correct answers
            correct_count = 0
            for key in answers:
                if answers[key] == correct_choice:
                    correct_count += 1

            # Check the results of the trivia question
            embed.title = '**Answer**'
            if len(answers) == 0:
                embed.description = ('**' + correct_choice + ':** ' +
                                     correct_answer +
                                     '\n\n⛔ **No answers given! Trivia has ' +
                                     'ended.**')
                self.channels_playing.remove(ctx.channel.id)
                still_playing = False

            elif len(answers) > 0 and correct_count == 0:
                embed.description = ('**' + correct_choice + ':** ' +
                                     correct_answer +
                                     '\n\n**No correct answers!**')

            elif len(answers) == 1 and correct_count == 1:
                embed.description = ('**' + correct_choice + ':** ' +
                                     correct_answer +
                                     '\n\n**Correct!**')
            else:
                embed.description = ('**' + correct_choice + ':** ' +
                                     correct_answer + '\n\n**' +
                                     str(correct_count) +
                                     ' correct answer(s)!**')
                for key in answers:
                    if answers[key] == correct_choice:
                        embed.description += '\n' + key.name

            await ctx.send(embed=embed)

        if len(trivia_data) == 0:
            await ctx.send('No trivia questions remaining. Trivia has ended.')

    # Starts a game of trivia using the simpsons trivia questions
    @commands.command(aliases=['Simpsonstrivia', 'SIMPSONSTRIVIA'])
    async def simpsonstrivia(self, ctx):
        if ctx.channel.id not in self.channels_playing:
            simpsons_yellow = discord.Colour(0xffef06)
            await self.start_trivia(ctx, 'simpsonsTrivia.json',
                                    simpsons_yellow,
                                    'https://github.com/MitchellAW/MitchellAW' +
                                    '.github.io/blob/master/images/donut-disc' +
                                    'ord.gif?raw=true')

    # Starts a game of trivia using the futurama trivia questions
    @commands.command(aliases=['Futuramatrivia', 'FUTURAMATRIVIA'])
    async def futuramatrivia(self, ctx):
        if ctx.channel.id not in self.channels_playing:
            fry_red = discord.Colour(0x9b2525)
            await self.start_trivia(ctx, 'futuramaTrivia.json', fry_red,
                                    'https://github.com/MitchellAW/MitchellAW' +
                                    '.github.io/blob/master/images/planet-exp' +
                                    'ress-discord.gif?raw=true')

    # Starts a game of trivia using the rick and morty trivia questions
    @commands.command(aliases=['Rickandmortytrivia', 'RICKANDMORTYTRIVIA'])
    async def rickandmortytrivia(self, ctx):
        portal_gif = ('https://github.com/MitchellAW/MitchellAW.github.io/blo' +
                      'b/master/images/rick-morty-portal.gif?raw=true')
        rick_blue = discord.Colour(0xaad3ea)


def setup(bot):
    bot.add_cog(Trivia(bot))
