-- Create table for storing all user votes
CREATE TABLE IF NOT EXISTS vote_history (
	vote_id serial PRIMARY KEY,
	user_id bigint NOT NULL,
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
	user_id bigint REFERENCES leaderboard(user_id) NOT NULL,
	is_correct boolean NOT NULL,
	answer_index int NOT NULL,
	answer_time int NOT NULL
);

-- Leaderboard of trivia players and their stats
CREATE TABLE IF NOT EXISTS leaderboard ( 
	user_id bigint PRIMARY KEY,
	username text NOT NULL,
	score bigint DEFAULT 0 NOT NULL,
	wins int DEFAULT 0 NOT NULL,
	losses int DEFAULT 0 NOT NULL,
	draws int DEFAULT 0 NOT NULL,
	correct_answers int DEFAULT 0 NOT NULL,
	incorrect_answers int DEFAULT 0 NOT NULL,
	fastest_answer int DEFAULT 20000 NOT NULL,
	current_streak int DEFAULT 0 NOT NULL,
	longest_streak int DEFAULT 0 NOT NULL
);

-- Check if user has voted in the last 24 hours
CREATE OR REPLACE FUNCTION has_voted_today(p_user_id bigint) 
RETURNS boolean AS $$
	BEGIN
		PERFORM (
			SELECT v.voted_at FROM vote_history v 
			WHERE v.user_id = p_user_id
			AND v.voted_at BETWEEN (
				NOW() AT time zone 'utc') - INTERVAL '24 HOURS' AND (
				NOW() AT time zone 'utc')
		);
		RETURN FOUND;
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

-- Adds the vote multiplier to points gained, rounds to nearest 5
CREATE OR REPLACE FUNCTION multiply(p_user_id bigint, points bigint)
RETURNS bigint as $$
	DECLARE
		multiplier int := (CASE WHEN has_voted_today(p_user_id) THEN 1.5 ELSE 1 END);
		new_points int;
	BEGIN
		SELECT 5 * ROUND(multiplier * points / 5 ) INTO new_points;
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
		-- 100 Bonus points for correctly answering  a unique answer
		IF (SELECT is_unique_answer(new.user_id, question)) THEN
			UPDATE leaderboard SET score = score + 100
			WHERE user_id = new.user_id;
		END IF;

		-- Update stats for correct answer (100 points for correct, increase streak)
		IF new.is_correct THEN

			-- 100 points for correct answer, 10 bonus points multiplier for each correct in a row
		    UPDATE leaderboard SET score = score + (SELECT multiply(new.user_id, 100 + (10 * current_streak))), 
		        correct_answers = correct_answers + 1,
		        -- New fastest answer
		        fastest_answer = LEAST(fastest_answer, new.answer_time), 
		        -- Update consecutive answer streaks
		        current_streak = current_streak + 1, 
		        longest_streak = GREATEST(longest_streak, current_streak + 1)
		    WHERE user_id = new.user_id;

		-- Update stats for incorrect answer (5 points, reset streak)
		ELSE
	        UPDATE leaderboard SET score = score + (SELECT multiply(new.user_id, 5)), 
	        incorrect_answers = incorrect_answers + 1, 
	        current_streak = 0
	        WHERE user_id = new.user_id;
		END IF;
		RETURN NEW;
	END;
$BODY$
language plpgsql;

-- TODO: add bonus points for being first to answer correctly, and 
-- being only one to correctly answer
CREATE OR REPLACE FUNCTION end_round() RETURNS TRIGGER AS $BODY$
	DECLARE

	BEGIN 

		RETURN NEW;
	END;
$BODY$
language plpgsql;

-- TODO: Add bonus points for being winner, loser, draw etc.,
-- and being fastest answer, also require that 5 rounds were played, 
-- and with more than one player
CREATE OR REPLACE FUNCTION end_match() RETURNS TRIGGER AS $BODY$
	DECLARE
		-- Get number of rounds
		round_count := (SELECT COUNT(DISTINCT round_id) AS round_count 
						FROM rounds WHERE match_id = new.match_id);

		-- Get number of players that participated
		player_count := (SELECT COUNT(DISTINCT user_id) FROM answers a 
			             INNER JOIN rounds r
			             ON a.round_id = r.round_id
			             WHERE r.match_id = 3);
	BEGIN
		-- Check that it counts as a valid multiplayer match 
		-- (more than 1 player, at least 5 rounds)
		IF (round_count >= 5 AND player_count > 1) THEN

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

CREATE TRIGGER update_round
	BEFORE UPDATE ON rounds
	FOR EACH ROW
	EXECUTE FUNCTION end_round();

CREATE TRIGGER update_match
	BEFORE UPDATE ON matches
	FOR EACH ROW
	EXECUTE FUNCTION end_match();


-- INDEX user_id in vote_history, match_id in matches, 
--
--

