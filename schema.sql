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

CREATE TABLE crawl_queue (
    puuid TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending' or 'done'
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);