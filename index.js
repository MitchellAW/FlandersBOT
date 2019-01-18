const config = require('./settings/config.json');
const DBL = require('dblapi.js');
const { Pool } = require('pg');

// Query to get the total points (weekend = 2, weekday = 1)
const POINTS_QUERY = `SELECT SUM(CASE WHEN isWeekend THEN 2 ELSE 1 END) 
					  AS points FROM voteHistory WHERE voteType = 'upvote';`;

// Query to insert a new vote into the history
const INSERT_QUERY = `INSERT INTO VoteHistory (userID, voteType,  isWeekend) 
				      VALUES ($1, $2, $3);`

// Records any missing votes since webhook was last ran. Inserts
// missing votes as null userID into vote_history table
async function updateMissingVotes() {
	var bot = await dbl.getBot(config.bot_id);

    // Count votes currently in history
    var response = await pool.query(POINTS_QUERY);
    var voteCount = response['rows'][0].points;

    // Calculate missing votes
    var votesMissing = bot.points - voteCount;

    // For each missing vote, insert value with null user and 
    // is_weekend as false
    console.log('Inserting ' + votesMissing + ' missing votes...');
    for (var i = 0; i < votesMissing; i++) {
        await pool.query(INSERT_QUERY, [null, 'upvote', false]);
    }
}

// Start the webhook server, insert any votes recorded into 
// vote_history table
async function startWebhook() {
    await dbl.webhook.on('ready', async hook => {
        console.log(`Webhook running at http://${hook.hostname}:${hook.port}${hook.path}`);
    });

    // Voting webhook, inserts vote into vote_history table
    await dbl.webhook.on('vote', async vote => {
        await pool.query(INSERT_QUERY, [vote.user, vote.type, vote.isWeekend]);
        await pool.query(`NOTIFY vote, \'${vote.user}\';`);
        console.log(`User with ID ${vote.user} just voted!`);
    });
}

// Configure database pool
const pool = new Pool(config.db_credentials);

// Initalise dbl object using dbl authorization token
var dbl = new DBL(config.dbl_token, config.webhook);

updateMissingVotes();
startWebhook();
