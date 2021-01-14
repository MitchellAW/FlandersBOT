import asyncio
import json
import random
import time

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.trivia_category import FuturamaTrivia
from cogs.trivia_category import SimpsonsTrivia

TRIVIA_ROLE = 'Trivia Moderator'


# If guild has trivia mod role, require users to have role to start matches, otherwise anyone can start matches
def has_trivia_permissions():
    def predicate(ctx):
        # Get custom trivia role from guild and user
        guild_role = discord.utils.get(ctx.guild.roles, name=TRIVIA_ROLE)
        user_role = discord.utils.get(ctx.author.roles, name=TRIVIA_ROLE)

        # Get manage messages permission from user
        manage_messages_perm = ctx.author.guild_permissions.manage_messages

        # If guild doesn't have trivia role, then stop command requires manage messages permissions
        if guild_role is None and ctx.command.qualified_name == 'forcestop':
            return manage_messages_perm

        # If guild doesn't have trivia role, then trivia can be started by anyone
        elif guild_role is None:
            return True

        # If guild has role, trivia role is required to start/stop trivia matches
        else:
            return user_role is not None

    return commands.check(predicate)


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.TIMER_DURATION = 16
        self.channels_playing = []
        self.answer_key = {
            '🇦': 0,
            '🇧': 1,
            '🇨': 2
        }

    # Starts a game of trivia using the simpsons trivia questions
    @commands.command(aliases=['strivia', 'simpsontrivia'])
    @commands.cooldown(10, 300, BucketType.channel)
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    @has_trivia_permissions()
    async def simpsonstrivia(self, ctx):
        if ctx.channel.id not in self.channels_playing:
            await self.start_trivia(ctx, SimpsonsTrivia())

    # Starts a game of trivia using the futurama trivia questions
    @commands.command(aliases=['ftrivia'])
    @commands.cooldown(10, 300, BucketType.channel)
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    @commands.check(has_trivia_permissions)
    async def futuramatrivia(self, ctx):
        if ctx.channel.id not in self.channels_playing:
            # Start the game
            await self.start_trivia(ctx, FuturamaTrivia())

    # TODO: Starts a game of trivia using rick and morty trivia questions
    @commands.command(aliases=['ramtrivia'])
    @commands.cooldown(10, 300, BucketType.channel)
    async def rickandmortytrivia(self, ctx):
        await ctx.send('Coming Soon!')

    # Explain how trivia games end  to users trying to use a stop command
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def stop(self, ctx):
        if ctx.channel.id in self.channels_playing:
            await ctx.send(
                'The game of trivia will end once nobody answers a question or a member with manage server permissions '
                'uses the forcestop command.'
            )

    # Allow users with manage server permissions to force stop trivia games
    @commands.command()
    @has_trivia_permissions()
    async def forcestop(self, ctx):
        if ctx.channel.id in self.channels_playing:
            self.channels_playing.remove(ctx.channel.id)
            await ctx.send('Trivia will terminate at the end of the current round.')

    # Display a users trivia stats
    @commands.command(aliases=['mystatistics', 'mystats', 'mystat', 'triviastat', 'triviastatistics'])
    @commands.cooldown(1, 30, BucketType.user)
    async def triviastats(self, ctx):
        query = '''SELECT user_id, username, score, wins, losses, correct_answers, 
                   incorrect_answers, fastest_answer, longest_streak, current_streak
                   FROM leaderboard
                   WHERE user_id = $1
                   '''
        trivia_stats = await self.bot.db.fetchrow(query, ctx.author.id)

        get_rank = '''SELECT get_rank($1, $2)'''

        if trivia_stats is not None:
            embed = discord.Embed(colour=discord.Colour(0x44981e))
            embed.set_author(name=f'Trivia Statistics for {ctx.author}', icon_url=ctx.author.avatar_url)

            # For all trivia statistics, calculate result, get current rank and add all to embed field
            score = round(trivia_stats['score'], 2)
            rank = await self.bot.db.fetchval(get_rank, ctx.author.id, 'score')
            embed.add_field(name=f':trophy: Score (#{rank:,})', value=f'{score:,}', inline=True)

            wins = round(trivia_stats['wins'], 2)
            rank = await self.bot.db.fetchval(get_rank, ctx.author.id, 'wins')
            embed.add_field(name=f':first_place: Wins (#{rank:,})', value=f'{wins:,}', inline=True)

            losses = round(trivia_stats['losses'], 2)
            rank = await self.bot.db.fetchval(get_rank, ctx.author.id, 'losses')
            embed.add_field(name=f':poop: Losses (#{rank:,})', value=f'{losses:,}', inline=True)

            rank = await self.bot.db.fetchval(get_rank, ctx.author.id, 'correct_answers')
            correct_answers = round(trivia_stats['correct_answers'], 2)
            embed.add_field(name=f':white_check_mark: Correct (#{rank:,})', value=f'{correct_answers:,}', inline=True)

            rank = await self.bot.db.fetchval(get_rank, ctx.author.id, 'incorrect_answers')
            incorrect_answers = round(trivia_stats['incorrect_answers'], 2)
            embed.add_field(name=f':no_entry: Incorrect (#{rank:,})', value=f'{incorrect_answers:,}', inline=True)

            accuracy = round(correct_answers / (incorrect_answers + correct_answers) * 100.0, 2)
            embed.add_field(name=f':bow_and_arrow: Accuracy', value=f'{accuracy:,}%', inline=True)

            rank = await self.bot.db.fetchval(get_rank, ctx.author.id, 'fastest_answer')
            fastest_answer = round(trivia_stats['fastest_answer'] / 1000, 3)
            embed.add_field(name=f':point_up: Fastest Answer (#{rank:,})', value=f'{fastest_answer:,}s', inline=True)

            rank = await self.bot.db.fetchval(get_rank, ctx.author.id, 'current_streak')
            current_streak = round(trivia_stats['current_streak'], 2)
            embed.add_field(name=f':chart_with_upwards_trend: Current Streak (#{rank:,})',
                            value=f'{current_streak:,}', inline=True)

            rank = await self.bot.db.fetchval(get_rank, ctx.author.id, 'longest_streak')
            longest_streak = round(trivia_stats['longest_streak'], 2)
            embed.add_field(name=f':four_leaf_clover: Longest Streak (#{rank:,})',
                            value=f'{longest_streak:,}', inline=True)

            await ctx.send(embed=embed)

        else:
            await ctx.send('You have not participated in any trivia.')

    # Display the global trivia leaderboard
    @commands.command()
    @commands.cooldown(1, 30, BucketType.channel)
    async def leaderboard(self, ctx):
        stats = [
            {
                "query": "SELECT username, score AS result "
                         "FROM leaderboard WHERE privacy = 0 "
                         "ORDER BY score DESC",
                "category": ":trophy: High Scores"
            },
            {
                "query": "SELECT username, wins AS result "
                         "FROM leaderboard WHERE privacy = 0 "
                         "ORDER BY wins DESC",
                "category": ":first_place: Wins"},
            {
                "query": "SELECT username, correct_answers AS result "
                         "FROM leaderboard WHERE privacy = 0 "
                         "ORDER BY correct_answers DESC",
                "category": ":white_check_mark:  Correct Answers"
            },
            {
                "query": "SELECT username, CONCAT(CAST(fastest_answer AS FLOAT) / 1000, 's') AS result "
                         "FROM leaderboard WHERE privacy = 0 "
                         "ORDER BY fastest_answer ASC",
                "category": ":point_up: Fastest Answers"
            },
            {
                "query": "SELECT username, longest_streak AS result "
                         "FROM leaderboard WHERE privacy = 0 "
                         "ORDER BY longest_streak DESC",
                "category": ":four_leaf_clover: Longest Streak"
            }
        ]

        # Scoreboard display embed
        embed = discord.Embed(title='Trivia Leaderboard', colour=discord.Colour(0x44981e))
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        query = 'SELECT COUNT(user_id) FROM leaderboard WHERE privacy = 0'
        leader_count = await self.bot.db.fetchval(query)

        if leader_count >= 1:
            for stat in stats:
                rows = await self.bot.db.fetch(stat['query'])

                scores = ''
                for row in rows[:5]:
                    scores += f'**{row["username"]}**: '
                    result = row['result']
                    if not isinstance(result, str):
                        result = f'{round(result, 2):,}'
                    scores += f'{result}\n'
                embed.add_field(name=stat['category'], value=scores, inline=False)

            if len(embed.fields) > 0:
                await ctx.send(embed=embed)

    # Starts a match of trivia (multiple rounds of questions)
    async def start_trivia(self, ctx, category):
        self.channels_playing.append(ctx.channel.id)

        # Load question data from trivia file
        with open(f'cogs/data/{category.file_name}', 'r') as trivia_data:
            trivia = json.load(trivia_data)
            questions = trivia.copy()
            random.shuffle(questions)
            trivia_data.close()

        # Insert new trivia match into DB
        query = '''INSERT INTO matches (guild_id, trivia_category) 
                   VALUES ($1, $2) RETURNING match_id
                '''
        match_id = await self.bot.db.fetchval(query, ctx.guild.id, category.category_name)

        # Continue playing trivia until exit or out of questions
        while ctx.channel.id in self.channels_playing and len(questions) > 0:
            question_data = questions.pop()
            await self.play_round(ctx, match_id, question_data, trivia, category)

        await self.end_match(ctx, match_id, category)

    # Starts a round of trivia (single question)
    async def play_round(self, ctx, match_id, question_data, trivia, category):
        question_index = trivia.index(question_data)
        question = question_data['question']
        answers = question_data['answers']
        source = question_data['source']
        correct_answer = answers[0]

        # Shuffle the possible answers
        random.shuffle(answers)

        correct_index = answers.index(correct_answer)
        correct_choice = chr(correct_index + 65)

        # Insert new trivia round into DB
        query = '''INSERT INTO rounds (match_id, question_index) VALUES ($1, $2)
                   RETURNING round_id
                '''
        round_id = await self.bot.db.fetchval(query, match_id, question_index)

        # Display the question and answers
        answer_msg = (f'**A:** {answers[0]} \n'
                      f'**B:** {answers[1]} \n'
                      f'**C:** {answers[2]} \n\n'
                      f'React below to answer!')

        embed = discord.Embed(title=question, colour=category.colour, description=answer_msg)
        embed.set_thumbnail(url=category.thumbnail_url)

        # Send the trivia question
        question = await ctx.send(embed=embed, delete_after=self.TIMER_DURATION + 3)

        # Add the answer react boxes
        await question.add_reaction('🇦')
        await question.add_reaction('🇧')
        await question.add_reaction('🇨')

        # Check for confirming a valid answer was made (A, B or C)
        def is_answer(reaction, user):
            return not user.bot and str(reaction.emoji) in ['🇦', '🇧', '🇨'] and reaction.message.channel == ctx.channel

        # Track some important round data
        user_answers = {}
        correct_count = 0

        # Start timer
        end_time = time.time() + self.TIMER_DURATION

        try:
            # Wait until timer ends for each question before displaying results
            while time.time() < end_time:
                react, user = await self.bot.wait_for('reaction_add', check=is_answer, timeout=end_time - time.time())

                # Only accept users first answer
                if user.id not in user_answers:
                    answer_index = trivia[question_index]['answers'].index(answers[self.answer_key[str(react.emoji)]])

                    # Check if correct answer
                    is_correct = answer_index == correct_index
                    if is_correct:
                        correct_count += 1
                    answer_time = int((time.time() - (end_time - self.TIMER_DURATION)) * 1000)

                    # Insert answer into DB
                    query = '''INSERT INTO answers (round_id, user_id, username,
                               is_correct, answer_index, answer_time) 
                               VALUES ($1, $2, $3, $4, $5, $6)
                            '''
                    await self.bot.db.fetch(query, round_id, int(user.id), str(user), is_correct, answer_index,
                                            answer_time)

                    user_answers.update({user.id: {'answer': str(react.emoji)}})

        except asyncio.TimeoutError:
            pass

        # Update usernames in the leaderboard
        await self.update_usernames(ctx, round_id)

        # Set round as complete (Triggers leaderboard stat updates)
        query = '''UPDATE rounds SET is_complete = true
                   WHERE round_id = $1
                '''
        await self.bot.db.fetch(query, round_id)

        # Check the results of the trivia question
        embed.set_thumbnail(url='')
        embed.description = (f'**{correct_choice}:** {correct_answer}\n'
                             f'**Source:** <{source}> \n\n')

        # Give statement about result based on # of correct answers recorded
        if len(user_answers) == 0:
            embed.description += '⛔ **No answers given! Trivia has ended.**'
            if ctx.channel.id in self.channels_playing:
                self.channels_playing.remove(ctx.channel.id)

        elif len(user_answers) > 0 and correct_count == 0:
            embed.description += '**No correct answers!**'

        elif len(user_answers) == 1 and correct_count == 1:
            embed.description += '**Correct!**'

        else:
            embed.description += f'**{str(correct_count)} correct answers!**'
            for key in user_answers:
                if user_answers[key]['answer'] == correct_choice:
                    embed.description += f'\n{key.name}'

        await ctx.send(embed=embed, delete_after=self.TIMER_DURATION + 3)

    # Update usernames in leaderboard
    async def update_usernames(self, ctx, round_id):
        # Get answers from the round
        query = 'SELECT * FROM answers WHERE round_id = $1'
        answers = await self.bot.db.fetch(query, round_id)

        # For each answer in round, update username
        for answer in answers:
            # Add points to score
            query = '''UPDATE leaderboard SET username = $1 
                       WHERE user_id = $2
                    '''
            await self.bot.db.fetch(query, answer['username'], answer['user_id'])

    async def end_match(self, ctx, match_id, category):
        # Set the match as complete (Triggers leaderboard stat updates)
        query = '''UPDATE matches SET is_complete = true
                   WHERE match_id = $1
                '''
        await self.bot.db.fetch(query, match_id)

        # Top Scorers (sorted by correct answers descending)
        query = '''SELECT user_id, username, COUNT(CASE WHEN is_correct THEN 1 END) 
                   AS correct FROM answers a
                   INNER JOIN rounds r
                   ON a.round_id = r.round_id
                   WHERE r.match_id = $1
                   GROUP BY a.user_id, a.username
                   ORDER BY correct DESC;
                '''
        top_scorers = await self.bot.db.fetch(query, match_id)

        # Check if there were anyone competing in the match
        if len(top_scorers) == 0:
            return

        scorers = ''
        top_scorer = top_scorers[0]["username"]
        for scorer in top_scorers[:5]:
            scorers += f'**<@!{scorer["user_id"]}>**: {round(scorer["correct"], 2):,}\n'

        # Scoreboard display embed
        embed = discord.Embed(description=f'**Congratulations to the top scorer, {top_scorer} :trophy:**',
                              color=category.colour)

        embed.set_author(name='Trivia Scoreboard', icon_url=self.bot.user.avatar_url)

        embed.add_field(name='*:medal:Correct Answers*', value=scorers)

        # Highest Accuracy (sorted by accuracy descending)
        query = '''SELECT user_id, username, 
                   CAST(COUNT(CASE WHEN is_correct THEN 1 END) AS FLOAT) / 
                   CAST(COUNT(user_id) AS FLOAT) AS accuracy FROM answers a 
                   INNER JOIN rounds r 
                   ON a.round_id = r.round_id 
                   WHERE r.match_id = $1 
                   GROUP BY a.user_id, a.username
                   ORDER BY accuracy DESC
                '''
        highest_accuracy = await self.bot.db.fetch(query, match_id)

        scorers = ''
        for scorer in highest_accuracy[:5]:
            scorers += f'**<@!{scorer["user_id"]}>**: {round(scorer["accuracy"] * 100.0, 2):,}%\n'
        embed.add_field(name='*:bow_and_arrow: Highest Accuracy*', value=scorers)

        # Fastest Answers (sorted by fastest time ascending)
        query = '''SELECT user_id, username,
                   MIN(answer_time) AS fastest_time 
                   FROM answers a 
                   INNER JOIN rounds r 
                   ON a.round_id = r.round_id 
                   WHERE a.is_correct = true and r.match_id = $1
                   GROUP BY a.user_id, a.username
                   ORDER BY fastest_time ASC
                '''
        fastest_answers = await self.bot.db.fetch(query, match_id)

        scorers = '' if len(fastest_answers) > 0 else '---'
        for scorer in fastest_answers[:5]:
            scorers += f'**<@!{scorer["user_id"]}>**: {round(scorer["fastest_time"]/1000, 3):,}s\n'
        embed.add_field(name='*:point_up: Fastest Answers*', value=scorers)

        # Display the scoreboard
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Trivia(bot))
