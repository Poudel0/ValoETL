-- Valorant Esports PostgreSQL Schema

-- 1. Tournament Table
CREATE TABLE IF NOT EXISTS Tournament (
    eventID INTEGER PRIMARY KEY, --parentEventId
    eventType VARCHAR(20) NOT NULL CHECK (eventType IN ('VCT', 'OffSeason', 'MidSeason')), -- All curremtly VCT events
    eventFormat VARCHAR(10) NOT NULL CHECK (eventFormat IN ('LAN', 'Online')), -- All currently LANS
    eventTier VARCHAR(7) NOT NULL CHECK (eventTier IN ('SSS', 'SS', 'S', 'A', 'B', 'C', 'D', 'F')),-- Champions 202X is SSS, Masters is SS, Americas/Pacific/EMEA/China is A,
    startDate Timestamptz, 
    eventName TEXT, --parentEventName
    eventSlug VARCHAR, --parentEventSlug
    childEvent VARCHAR(20),  --eventChildLabel
    childEventSlug VARCHAR(30) --eventSlug
    -- childEventID INTEGER REFERENCES Tournament(eventID) 
);


-- 2. Matches Table
CREATE TABLE IF NOT EXISTS Matches (
    matchID  Integer PRIMARY KEY, --id
    eventID INTEGER REFERENCES Tournament(eventID), --parentEventId
    eventStage VARCHAR(15) , --childEventLabel
    bracket VARCHAR(15),  --bracket
    vlrID Integer, --vlrid
    team1ID INTEGER, --
    team2ID INTEGER,
    -- vctRegion VARCHAR,
    eventRegionID INTEGER,
    division VARCHAR(10),
    t1Score INTEGER,
    t2Score INTEGER,
    bestOf INTEGER,
    patchID VARCHAR
);

-- 3. Teams Table
CREATE TABLE IF NOT EXISTS Teams (
    teamID INTEGER PRIMARY KEY,
    teamName VARCHAR NOT NULL,
    teamShort VARCHAR,
    region VARCHAR
);

-- 4. Players Table
CREATE TABLE IF NOT EXISTS Player (
    playerID INTEGER PRIMARY KEY,
    ign VARCHAR(20) NOT NULL,
    oldIgn VARCHAR,
    currentTeamID INTEGER
);

-- 5. Map Catalog
CREATE TABLE IF NOT EXISTS mapsAvailable (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    riotID TEXT
);

-- 6. Match Map Pick/Bans
CREATE TABLE IF NOT EXISTS matchMapPickBans (
    matchID INTEGER NOT NULL REFERENCES Matches(matchID),
    seqNum INTEGER NOT NULL,
    teamID INTEGER NOT NULL REFERENCES Teams(teamID),
    mapID INTEGER NOT NULL REFERENCES mapsAvailable(id),
    pickBanType VARCHAR NOT NULL CHECK (pickBanType IN ('pick', 'ban')),
    isLeftover BOOLEAN NOT NULL,
    teamSeqNum INTEGER NOT NULL,
    PRIMARY KEY (matchID, seqNum)
);

-- 7. Match Maps
CREATE TABLE IF NOT EXISTS matchMaps (
    mapID INTEGER PRIMARY KEY,
    matchID INTEGER REFERENCES Matches(matchID),
    mapNum INTEGER,
    lengthInMilli INTEGER,
    attackingFirst VARCHAR,
    winner INTEGER,
    t1Score INTEGER,
    t2Score INTEGER,
    vodURL TEXT
);

-- 8. Map Stats
CREATE TABLE IF NOT EXISTS matchMapStats (
    mapID INTEGER REFERENCES matchMaps(mapID),
    playerID INTEGER REFERENCES Player(playerID),
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER,
    ribRating FLOAT,
    ribRatingAttack FLOAT,
    ribRatingDefense FLOAT,
    PRIMARY KEY (mapID, playerID)
);

-- 9. Map Rounds
CREATE TABLE IF NOT EXISTS matchMapRounds (
    roundID INTEGER PRIMARY KEY,
    matchID INTEGER REFERENCES Matches(matchID),
    roundNum INTEGER,
    winCondition VARCHAR,
    winnerTeam INTEGER,
    ceremony VARCHAR,
    t1LoadoutTier VARCHAR,
    t2LoadoutTier VARCHAR,
    attackingTeam INTEGER
);

-- 10. Kills
CREATE TABLE IF NOT EXISTS matchMapKills (
    id INTEGER PRIMARY KEY,
    matchID INTEGER REFERENCES Matches(matchID),
    roundID INTEGER REFERENCES matchMapRounds(roundID),
    killerID INTEGER REFERENCES Player(playerID),
    victimID INTEGER REFERENCES Player(playerID),
    roundTimeMillis INTEGER,
    gameTimeMillis INTEGER,
    victimLocationX FLOAT,
    victimLocationY FLOAT,
    damageType VARCHAR,
    abilityType VARCHAR,
    weaponID VARCHAR,
    secondaryFireMode BOOLEAN,
    isFirst BOOLEAN,
    tradedByKillID INTEGER,
    tradedForKillID INTEGER,
    weapon VARCHAR,
    weaponCategory VARCHAR,
    killerTeamNumber INTEGER,
    victimTeamNumber INTEGER,
    side VARCHAR,
    assistants TEXT
);

-- 11. XvY Stats
CREATE TABLE IF NOT EXISTS matchMapXvYs (
    matchID INTEGER REFERENCES Matches(matchID),
    teamID INTEGER REFERENCES Teams(teamID),
    teamNumber INTEGER,
    side VARCHAR,
    situation VARCHAR,
    team1Count INTEGER,
    team2Count INTEGER,
    delta INTEGER,
    wins INTEGER,
    losses INTEGER
);

-- 12. Player Stats per Round
CREATE TABLE IF NOT EXISTS matchMapPlayerStatsOnRounds (
    matchID INTEGER REFERENCES Matches(matchID),
    roundID INTEGER REFERENCES matchMapRounds(roundID),
    roundNumber INTEGER,
    playerID INTEGER REFERENCES Player(playerID),
    teamNumber INTEGER,
    side VARCHAR,
    acs INTEGER,
    kills INTEGER,
    firstKills INTEGER,
    deaths INTEGER,
    firstDeaths INTEGER,
    assists INTEGER,
    damage INTEGER,
    headshots INTEGER,
    bodyshots INTEGER,
    legshots INTEGER,
    plants INTEGER,
    defusals INTEGER,
    clutches INTEGER,
    clutchOpponents INTEGER,
    clutchOpportunities INTEGER,
    impact FLOAT,
    kastRounds INTEGER
);

-- 13. Player Stats per Map
CREATE TABLE IF NOT EXISTS matchMapPlayerStatsOnMaps (
    matchID INTEGER REFERENCES Matches(matchID),
    playerID INTEGER REFERENCES Player(playerID),
    score INTEGER,
    roundsPlayed INTEGER,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER,
    playtimeMillis INTEGER,
    impact FLOAT,
    rating FLOAT,
    attackingRating FLOAT,
    defendingRating FLOAT
);

-- 14. Events
CREATE TABLE IF NOT EXISTS matchMapEventsOnMaps (
    roundID INTEGER REFERENCES matchMapRounds(roundID),
    roundNumber INTEGER,
    roundTimeMillis INTEGER,
    killID INTEGER,
    tradedByKillID INTEGER,
    tradedForKillID INTEGER,
    bombID VARCHAR,
    resID VARCHAR,
    playerID INTEGER REFERENCES Player(playerID),
    assists TEXT,
    referencePlayerID INTEGER,
    eventType VARCHAR,
    damageType VARCHAR,
    weaponID VARCHAR,
    ability VARCHAR,
    impact FLOAT,
    attackingWinProbabilityBefore FLOAT,
    attackingWinProbabilityAfter FLOAT,
    attackingTeamNumber INTEGER
);

-- 15. Locations
CREATE TABLE IF NOT EXISTS matchMapLocationsOnMaps (
    roundNumber INTEGER,
    playerID INTEGER REFERENCES Player(playerID),
    roundTimeMillis INTEGER,
    locationX FLOAT,
    locationY FLOAT,
    viewRadians FLOAT
);

-- 16. Economy Stats
CREATE TABLE IF NOT EXISTS matchMapEconomiesOnMaps (
    roundID INTEGER REFERENCES matchMapRounds(roundID),
    roundNumber INTEGER,
    playerID INTEGER REFERENCES Player(playerID),
    agentID INTEGER,
    score INTEGER,
    weaponID VARCHAR,
    armorID VARCHAR,
    remainingCreds INTEGER,
    spentCreds INTEGER,
    loadoutValue INTEGER,
    survived BOOLEAN,
    kast BOOLEAN
);

-- 17. Agents
CREATE TABLE IF NOT EXISTS Agents (
    agentID INTEGER PRIMARY KEY,
    name VARCHAR,
    role VARCHAR
);

-- 18. Abilities
CREATE TABLE IF NOT EXISTS Abilities (
    abilityID INTEGER PRIMARY KEY,
    agentID INTEGER REFERENCES Agents(agentID),
    name VARCHAR,
    slot VARCHAR
);

-- 19. Weapons
CREATE TABLE IF NOT EXISTS Weapons (
    weaponID VARCHAR PRIMARY KEY,
    name VARCHAR,
    category VARCHAR,
    cost INTEGER
);

-- 20. Armor
CREATE TABLE IF NOT EXISTS Armor (
    armorID VARCHAR PRIMARY KEY,
    name VARCHAR,
    cost INTEGER,
    damageReduction FLOAT
);

-- 21. Regions
CREATE TABLE IF NOT EXISTS Regions (
    regionID INTEGER PRIMARY KEY,
    name VARCHAR
);

-- 22. Patches
CREATE TABLE IF NOT EXISTS Patches (
    patchID VARCHAR PRIMARY KEY,
    releaseDate Timestamptz,
    description TEXT
);
