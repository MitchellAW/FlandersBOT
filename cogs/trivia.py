import asyncio
import discord
import json
import random
import time

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Trivia():
    def __init__(self, bot):
        self.bot = bot
        self.channelsPlaying = []

    # Starts a game of trivia using fileName as the questions file
    async def trivia(self, ctx, fileName, categoryColour):
        self.channelsPlaying.append(ctx.channel.id)
        with open(fileName, 'r') as triviaQuestions:
            triviaData = json.load(triviaQuestions)
            random.shuffle(triviaData)
            triviaQuestions.close()

        stillPlaying = True
        while stillPlaying and len(triviaData) > 0:
            # Gather all question information needed
            questionData = triviaData.pop()
            question = questionData['question']
            answers = questionData['answers']
            correctAnswer = answers[0]

            # Shuffle answers, by default correct answer is always first
            random.shuffle(answers)
            correctChoice = chr(answers.index(correctAnswer) + 65)

            answerMsg = ('**A:** {}\n**B**: {}\n**C:** {} \n\nSend a letter ' +
                            'below to answer!').format(answers[0],
                            answers[1],
                            answers[2])

            embed = discord.Embed(title=question,
                                  colour=categoryColour,
                                  description=answerMsg)

            # Send the trivia question
            await ctx.send(embed=embed)

            # Check for confirming an answer was made (case-insensitive)
            def isAnswer(message):
                return message.content.upper() in ['A', 'B', 'C']

            # Wait for answers from users for 10 secs, storing all answers
            answers = {}
            endTime = time.time() + 10
            try:
                while time.time() < endTime:
                    message = await self.bot.wait_for('message',
                                                      check=isAnswer,
                                                      timeout=(endTime -
                                                               time.time()))

                    if message.author.id not in answers:
                        answers.update({message.author:message.content.upper()})

            except asyncio.TimeoutError:
                pass

            # Count correct answers
            correctCount = 0
            for key in answers:
                if answers[key] == correctChoice:
                    correctCount += 1

            # Check the results of the trivia question
            embed.title = '**Answer**'
            if len(answers) == 0:
                embed.description = ('**' + correctChoice + ':** ' + correctAnswer +
                                     '\n\n⚠ No answers given! Trivia has ended.')
                self.channelsPlaying.remove(ctx.channel.id)
                stillPlaying = False

            elif len(answers) > 0 and correctCount == 0:
                embed.description = ('**' + correctChoice + ':** ' + correctAnswer +
                                     '\n\nNo correct answers!')

            elif len(answers) == 1 and correctCount == 1:
                embed.description = ('**' + correctChoice + ':** ' + correctAnswer +
                                     '\n\n**Correct!**')
            else:
                embed.description = ('**' + correctChoice + ':** ' + correctAnswer +
                                     '\n\n**' + str(correctCount) +
                                     ' correct answer(s)!**')
                for key in answers:
                    if answers[key] == correctChoice:
                        embed.description += '\n' + key.name

            await ctx.send(embed=embed)

        if len(triviaData) == 0:
            await ctx.send('No trivia questions remaining. Trivia has ended.')

    # Starts a game of trivia using the simpsons trivia questions
    @commands.command()
    async def simpsonstrivia(self, ctx):
        if ctx.channel.id not in self.channelsPlaying:
            await self.trivia(ctx, 'simpsonsTrivia.json', discord.Colour(0xffef06))

    # Starts a game of trivia using the futurama trivia questions
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def futuramatrivia(self, ctx):
        fryRed = discord.Colour(0x920f1d)
        await ctx.send('Coming soon!')

    # Starts a game of trivia using the rick and morty trivia questions
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortytrivia(self, ctx):
        await ctx.send('Coming soon!')
        rickBlue = discord.Colour(0xaad3ea)

def setup(bot):
    bot.add_cog(Trivia(bot))
