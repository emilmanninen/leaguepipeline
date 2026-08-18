CREATE TABLE champions (
    champion_id INT PRIMARY KEY,
    name TEXT NOT NULL,
    riot_id TEXT
);

CREATE TABLE items (
    item_id INT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE matches (
    match_id TEXT PRIMARY KEY,
    patch TEXT NOT NULL,
    queue_id INT NOT NULL,
    game_duration INT NOT NULL,
    game_creation_ts TIMESTAMPTZ NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE participants (
    match_id TEXT REFERENCES matches(match_id),
    puuid TEXT NOT NULL,
    champion_id INT REFERENCES champions(champion_id),
    team_id INT NOT NULL,
    role TEXT NOT NULL,          -- from teamPosition
    win BOOLEAN NOT NULL,
    kills INT NOT NULL,
    deaths INT NOT NULL,
    assists INT NOT NULL,
    gold_earned INT NOT NULL,
    items INT[] NOT NULL,        -- item0..item6 collected into an array
    cs INT NOT NULL,              -- totalMinionsKilled + neutralMinionsKilled
    PRIMARY KEY (match_id, puuid)
);

CREATE TABLE timeline_frames (
    match_id TEXT REFERENCES matches(match_id),
    puuid TEXT NOT NULL,
    minute INT NOT NULL,
    gold INT NOT NULL,
    xp INT NOT NULL,
    cs INT NOT NULL,
    position_x INT,
    position_y INT,
    PRIMARY KEY (match_id, puuid, minute)
);

CREATE TABLE timeline_events (
    id SERIAL PRIMARY KEY,
    match_id TEXT REFERENCES matches(match_id),
    timestamp INT NOT NULL,       -- ms from game start, straight from Riot
    event_type TEXT NOT NULL,
    actor_puuid TEXT,
    victim_puuid TEXT,
    details JSONB NOT NULL
);

CREATE TABLE champion_matchups (
    champion_id INT REFERENCES champions(champion_id),
    opponent_champion_id INT REFERENCES champions(champion_id),
    role TEXT NOT NULL,
    games_played INT NOT NULL DEFAULT 0,
    wins INT NOT NULL DEFAULT 0,
    PRIMARY KEY (champion_id, opponent_champion_id, role)
);

CREATE TABLE item_win_rates (
    item_id INT REFERENCES items(item_id),
    champion_id INT REFERENCES champions(champion_id),
    games_played INT NOT NULL DEFAULT 0,
    wins INT NOT NULL DEFAULT 0,
    PRIMARY KEY (item_id, champion_id)
);

CREATE TABLE crawl_queue (
    puuid TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending' or 'done'
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);