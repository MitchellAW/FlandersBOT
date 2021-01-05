-- Create table for storing all user votes
CREATE TABLE IF NOT EXISTS vote_history (
	vote_id serial PRIMARY KEY,
	user_id bigint,
	vote_type text CHECK (vote_type IN ('upvote', 'test')),
	is_weekend boolean NOT NULL,
	voted_at timestamp DEFAULT (NOW() at time zone 'utc') NOT NULL
);

-- Every trivia match (multiple questions)
CREATE TABLE IF NOT EXISTS matches (
	match_id serial PRIMARY KEY,
	guild_id bigint NOT NULL,
	trivia_category text NOT NULL,
	is_complete boolean DEFAULT false NOT NULL
);

-- Every trivia round (single question) in a trivia match
CREATE TABLE IF NOT EXISTS rounds (
	round_id serial PRIMARY KEY,
	match_id serial REFERENCES matches(match_id),
	question_index int NOT NULL,
	is_complete boolean DEFAULT false NOT NULL
);

-- Every answer recorded within a trivia round
CREATE TABLE IF NOT EXISTS answers (
	answer_id serial PRIMARY KEY,
	round_id serial REFERENCES rounds(round_id),
	user_id bigint NOT NULL,
	username text NOT NULL,
	is_correct boolean NOT NULL,
	answer_index int NOT NULL,
	answer_time int NOT NULL
);

-- Leaderboard of trivia players and their stats
CREATE TABLE IF NOT EXISTS leaderboard ( 
	user_id bigint PRIMARY KEY,
	username text NOT NULL,
	privacy int DEFAULT 0 NOT NULL,
	score bigint DEFAULT 0 NOT NULL,
	wins int DEFAULT 0 NOT NULL,
	losses int DEFAULT 0 NOT NULL,
	correct_answers int DEFAULT 0 NOT NULL,
	incorrect_answers int DEFAULT 0 NOT NULL,
	fastest_answer int DEFAULT 20000 NOT NULL,
	current_streak int DEFAULT 0 NOT NULL,
	longest_streak int DEFAULT 0 NOT NULL
);

-- Create table for storing all custom guild prefixes
CREATE TABLE IF NOT EXISTS prefixes (
	prefix_id serial PRIMARY KEY,
	guild_id bigint NOT NULL,
	prefix VARCHAR(10) NOT NULL,
	UNIQUE (guild_id, prefix)
);

-- Check if user has voted in the last 24 hours
CREATE OR REPLACE FUNCTION has_voted_today(p_user_id bigint) 
RETURNS boolean AS $$
	BEGIN
		RETURN (
			SELECT COUNT(v.voted_at) FROM vote_history v 
			WHERE v.user_id = p_user_id
			AND v.voted_at BETWEEN (
				NOW() AT time zone 'utc') - INTERVAL '24 HOURS' AND (
				NOW() AT time zone 'utc')
		) != 0;
	END;
$$ LANGUAGE plpgsql;

-- Get the user_id of user that won match,
-- Winner is determined based on correct answers, then fastest answer if tie
CREATE OR REPLACE FUNCTION get_winner(p_match_id bigint)
RETURNS bigint AS $$
    BEGIN
        RETURN (
            SELECT user_id FROM (
                SELECT * FROM answers a
                INNER JOIN rounds r
                ON a.round_id = r.round_id
                WHERE r.match_id = p_match_id
            ) match_answers
            GROUP by user_id
            ORDER BY COUNT(CASE WHEN is_correct THEN 1 END) DESC, MIN(answer_time) ASC
            LIMIT 1
            );
    END;
$$ LANGUAGE plpgsql;

-- Get the user_id of the user that had the fastest correct answer in the match
CREATE OR REPLACE FUNCTION get_fastest_answer(p_match_id bigint)
RETURNS bigint AS $$
    BEGIN
        RETURN (
            SELECT user_id FROM answers a
            INNER JOIN rounds r
            ON a.round_id = r.round_id
            WHERE a.is_correct = true and r.match_id = p_match_id
            GROUP BY a.user_id
            ORDER BY MIN(answer_time) ASC
            LIMIT 1
        );
    END;
$$ LANGUAGE plpgsql;

-- Check if answer is a new unique answer
CREATE OR REPLACE FUNCTION is_unique_answer(p_user_id bigint, p_question_index int) 
RETURNS boolean AS $$
	BEGIN
		RETURN (
		 	SELECT COUNT(a.user_id) FROM answers a
		 	INNER JOIN rounds r
		 	ON a.round_id = r.round_id 
		 	WHERE r.question_index = p_question_index AND 
		 		a.is_correct = true AND a.user_id = p_user_id
		) = 0;
	END;
$$ LANGUAGE plpgsql;

-- Calculates the level using a users score
CREATE OR REPLACE FUNCTION calculate_level(score bigint) 
RETURNS int AS $$
	DECLARE
		level int := 0;
		total bigint := 0;
	BEGIN
		WHILE total < score LOOP
			level := level + 1;
			total := total + (255 * level);
		END LOOP;

		RETURN level;
	END;
$$ LANGUAGE plpgsql;

-- Gets a users current level based on their score
CREATE OR REPLACE FUNCTION get_level(p_user_id bigint) 
RETURNS int AS $$
	DECLARE
		level int;
	BEGIN
		WITH user_score AS (
			SELECT score FROM leaderboard l WHERE l.user_id = p_user_id
		)
		SELECT calculate_level(user_score) INTO level;
		RETURN level;
	END;
$$ LANGUAGE plpgsql;

-- Adds the vote xp multiplier to points gained, rounds to nearest 5
CREATE OR REPLACE FUNCTION vote_multiply(p_user_id bigint, points bigint)
RETURNS bigint as $$
	DECLARE
		vote_multiplier float := (CASE WHEN has_voted_today(p_user_id) THEN 1.5 ELSE 1 END);
		new_points int;
	BEGIN
		SELECT 5 * ROUND(vote_multiplier * points / 5) INTO new_points;
		RETURN new_points;
	END;
$$ LANGUAGE plpgsql;

-- Update a users statistics when a user answers
CREATE OR REPLACE FUNCTION update_stats() RETURNS TRIGGER AS $BODY$
	DECLARE 
		question int := (SELECT question_index 
			             FROM rounds 
			             WHERE round_id = new.round_id);
	BEGIN
		-- Insert user that answers into leaderboard
		INSERT INTO leaderboard (user_id, username) 
		VALUES (new.user_id, new.username) ON CONFLICT DO NOTHING;

		-- Update stats for correct answer (100 points for correct, increase streak)
		IF new.is_correct THEN

			-- 500 Bonus points for correctly answering  a unique answer
			IF (SELECT is_unique_answer(new.user_id, question)) THEN
				UPDATE leaderboard SET score = score + (SELECT vote_multiply(user_id, 500))
				WHERE user_id = new.user_id;
			END IF;

			-- 100 points for correct answer, 10 bonus points multiplier for each correct in a row
		    UPDATE leaderboard SET score = score + (SELECT vote_multiply(user_id, 100 + (10 * current_streak))), 
		        correct_answers = correct_answers + 1,
		        -- New fastest answer
		        fastest_answer = LEAST(fastest_answer, new.answer_time), 
		        -- Update consecutive answer streaks
		        current_streak = current_streak + 1, 
		        longest_streak = GREATEST(longest_streak, current_streak + 1)
		    WHERE user_id = new.user_id;

		-- Update stats for incorrect answer (5 points, reset streak)
		ELSE
	        UPDATE leaderboard SET score = score + (SELECT vote_multiply(user_id, 5)), 
	        incorrect_answers = incorrect_answers + 1, 
	        current_streak = 0
	        WHERE user_id = new.user_id;
		END IF;
		RETURN NEW;
	END;
$BODY$
language plpgsql;

-- Add bonus points for being the fastest and only correct answer
CREATE OR REPLACE FUNCTION end_round() RETURNS TRIGGER AS $BODY$
	DECLARE
		-- Get user_id of user that answered correctly fastest
		fastest_user bigint := (SELECT user_id FROM answers a
								WHERE a.round_id = new.round_id AND a.is_correct = true
								GROUP BY a.user_id
								ORDER BY MIN(answer_time) ASC
								LIMIT 1);

		-- Get number of correct answers for round
		correct_count int := (SELECT COUNT(CASE WHEN is_correct THEN 1 END) FROM answers a
						  WHERE a.round_id = new.round_id AND a.is_correct = true);

		-- Get user_id of top answer (only used if correct_count is 1)
		only_answer bigint := (SELECT user_id FROM answers a
							   WHERE a.round_id = new.round_id AND a.is_correct = true
							   LIMIT 1);
	BEGIN
		-- 50 Bonus points for fastest answer in round
		UPDATE leaderboard SET score = score + vote_multiply(user_id, 50)
		WHERE user_id = fastest_user;

		-- 50 Bonus points for being only correct answer
		IF (correct_count = 1) THEN
			UPDATE leaderboard SET score = score + vote_multiply(user_id, 50)
			WHERE user_id = only_answer;
		END IF;
		RETURN NEW;
	END;
$BODY$
language plpgsql;

-- Add bonus points for being winner, loser, and being fastest answer,
-- requires that 5 rounds were played, with more than one player
CREATE OR REPLACE FUNCTION end_match() RETURNS TRIGGER AS $BODY$
	DECLARE
		-- Get number of rounds
		round_count int := (SELECT COUNT(DISTINCT round_id) AS round_count
						    FROM rounds 
						    WHERE match_id = new.match_id);

		-- Get number of players that participated
		player_count int := (SELECT COUNT(DISTINCT user_id) FROM answers a 
			             INNER JOIN rounds r
			             ON a.round_id = r.round_id
			             WHERE r.match_id = new.match_id);

		-- Get user_id of winner of match
	    winner bigint := (SELECT get_winner(new.match_id));

	    -- Get user_id of fastest answer in match
	    fastest_user bigint := (SELECT get_fastest_answer(new.match_id));
	BEGIN
		-- Check that it counts as a valid multiplayer match 
		-- (more than 1 player, at least 5 rounds)
		IF (round_count >= 5 AND player_count > 1) THEN

			-- 1,000 Bonus Points for winning, +1 Win
		    UPDATE leaderboard SET wins = wins + 1,
		    score = score + (SELECT vote_multiply(user_id, 1000))
		    WHERE user_id = winner;

		    -- 100 Bonus Points for losing, +1 Loss, 
		    UPDATE leaderboard SET losses = losses + 1,
		    score = score + (SELECT vote_multiply(user_id, 100))
		    WHERE user_id != winner;

		    -- 100 Bonus points for being fastest correct answer in match
		    UPDATE leaderboard SET score = score + (SELECT vote_multiply(user_id, 100))
		    WHERE user_id = fastest_user;
		END IF;
		RETURN NEW;
	END;
$BODY$
language plpgsql;

-- Trigger stats update on inserted answer
CREATE TRIGGER insert_answer
	BEFORE INSERT ON answers
	FOR EACH ROW
	EXECUTE FUNCTION update_stats();

-- Trigger stat updates on round end
CREATE TRIGGER update_round
	BEFORE UPDATE ON rounds
	FOR EACH ROW
	EXECUTE FUNCTION end_round();

-- Trigger stat updates on match end
CREATE TRIGGER update_match
	BEFORE UPDATE ON matches
	FOR EACH ROW
	EXECUTE FUNCTION end_match();

