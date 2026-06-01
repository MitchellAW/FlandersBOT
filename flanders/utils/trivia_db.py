import asyncpg

from flanders.models import TriviaAnswer, TriviaCategory, TriviaLeaderboardType, TriviaScoreboard

LEADERBOARD_SORT_ORDERS: dict[TriviaLeaderboardType, str] = {
    TriviaLeaderboardType.FASTEST_ANSWER: "ASC",
}

LEADERBOARD_EXPRESSIONS: dict[TriviaLeaderboardType, str] = {
    TriviaLeaderboardType.FASTEST_ANSWER: "CONCAT(CAST(fastest_answer AS FLOAT) / 1000, 's')"
}


class TriviaDB:
    def __init__(self, db: asyncpg.Pool) -> None:
        self.db = db

    # Insert new trivia match into DB
    async def insert_match(self, guild_id: int, category: TriviaCategory) -> int:
        query = """INSERT INTO matches (guild_id, trivia_category)
                   VALUES ($1, $2) RETURNING match_id
                """
        match_id = await self.db.fetchval(query, guild_id, category.category_name)
        return match_id

    # Insert new trivia round into DB
    async def insert_round(self, match_id: int, question_index: int) -> int:
        query = """INSERT INTO rounds (match_id, question_index) VALUES ($1, $2)
                   RETURNING round_id
                """
        round_id = await self.db.fetchval(query, match_id, question_index)
        return round_id

    # Insert answer for round into DB
    async def insert_answer(self, round_id: int, answer: TriviaAnswer) -> None:
        query = """INSERT INTO answers (round_id, user_id, username,
                               is_correct, answer_index, answer_time)
                               VALUES ($1, $2, $3, $4, $5, $6)
                            """
        await self.db.execute(
            query,
            round_id,
            answer.user_id,
            answer.username,
            answer.is_correct,
            answer.answer_index,
            answer.answer_time,
        )

    # Set the match as complete (Triggers leaderboard stat updates)
    async def complete_match(self, match_id: int) -> None:
        query = """UPDATE matches SET is_complete = true
                       WHERE match_id = $1
                    """
        await self.db.fetch(query, match_id)

    # Set round as complete (Triggers leaderboard stat updates)
    async def complete_round(self, round_id: int) -> None:
        query = """UPDATE rounds SET is_complete = true
                   WHERE round_id = $1
                """
        await self.db.fetch(query, round_id)

    async def get_leaderboard_count(self) -> int:
        query = "SELECT COUNT(user_id) FROM leaderboard WHERE privacy = 0"
        return await self.db.fetchval(query)

    # Get the username and result for the top N (limit) users from the leaderboard
    async def get_leaderboard_results(
        self, leaderboard_type: TriviaLeaderboardType, limit: int = 5
    ) -> list[tuple[str, int]]:
        order = LEADERBOARD_SORT_ORDERS.get(leaderboard_type, "DESC")
        column = LEADERBOARD_EXPRESSIONS.get(leaderboard_type, leaderboard_type)

        query = f"""
        SELECT username, {column} AS result
        FROM leaderboard WHERE privacy = 0
        ORDER BY {leaderboard_type} {order} LIMIT $1
        """  # noqa: S608 - Only injecting columns and sorting methods

        results = await self.db.fetch(query, limit)
        return [(result["username"], result["result"]) for result in results]

    async def get_latest_match_details(self, guild_id: int) -> tuple[int, str] | None:
        query = """SELECT match_id, trivia_category FROM matches
                WHERE guild_id = $1 AND is_complete = true AND (
                    SELECT get_participant_count(match_id)
                ) > 0
                ORDER BY match_id DESC
                LIMIT 1
                """
        match = await self.db.fetchrow(query, guild_id)
        if match is None:
            return None

        return match["match_id"], match["trivia_category"]

    async def get_user_stats(self, user_id: int) -> dict[str, int] | None:
        query = """
        SELECT
            score, (SELECT get_rank($1, 'score')) AS score_rank,
            wins, (SELECT get_rank($1, 'wins')) AS wins_rank,
            losses, (SELECT get_rank($1, 'losses')) AS losses_rank,
            correct_answers, (SELECT get_rank($1, 'correct_answers'))  AS correct_answers_rank,
            incorrect_answers, (SELECT get_rank($1, 'incorrect_answers')) AS incorrect_answers_rank,
            fastest_answer, (SELECT get_rank($1, 'fastest_answer'))   AS fastest_answer_rank,
            current_streak, (SELECT get_rank($1, 'current_streak'))   AS current_streak_rank,
            longest_streak, (SELECT get_rank($1, 'longest_streak'))   AS longest_streak_rank
        FROM leaderboard
        WHERE user_id = $1
        """

        row = await self.db.fetchrow(query, user_id)
        return dict(row) if row else None

    async def get_scoreboard(self, match_id: int) -> TriviaScoreboard | None:
        query = """
            WITH match_answers AS (
                SELECT a.user_id, a.username, a.is_correct, a.answer_time
                FROM answers a
                INNER JOIN rounds r ON a.round_id = r.round_id
                WHERE r.match_id = $1
            ),
            player_stats AS (
                SELECT
                    username,
                    COUNT(CASE WHEN is_correct THEN 1 END) AS correct,
                    CAST(COUNT(CASE WHEN is_correct THEN 1 END) AS FLOAT) /
                        CAST(COUNT(user_id) AS FLOAT) AS accuracy,
                    MIN(CASE WHEN is_correct THEN answer_time END) AS fastest_time
                FROM match_answers
                GROUP BY user_id, username
            )
            SELECT
                (SELECT COUNT(DISTINCT user_id) FROM match_answers) AS participant_count,
                (SELECT COUNT(DISTINCT round_id) FROM rounds
                    WHERE match_id = $1 AND round_id IN (
                        SELECT DISTINCT round_id FROM answers
                    )
                ) AS question_count,
                username,
                correct,
                accuracy,
                fastest_time
            FROM player_stats
            ORDER BY correct DESC, accuracy DESC, fastest_time ASC
        """
        rows = await self.db.fetch(query, match_id)
        if not rows:
            return None

        return TriviaScoreboard(
            participant_count=rows[0]["participant_count"],
            question_count=rows[0]["question_count"],
            top_scorers=[(r["username"], r["correct"]) for r in sorted(rows, key=lambda r: r["correct"], reverse=True)],
            highest_accuracy=[
                (r["username"], r["accuracy"]) for r in sorted(rows, key=lambda r: r["accuracy"], reverse=True)
            ],
            fastest_answers=[
                (r["username"], r["fastest_time"])
                for r in sorted(rows, key=lambda r: r["fastest_time"])
                if r["fastest_time"] is not None
            ],
        )
