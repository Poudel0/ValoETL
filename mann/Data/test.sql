-- CREATE DATABASE IF NOT EXISTS ATVal 

CREATE Table IF NOT EXISTS Tournament(
    eventID INTEGER PRIMARY KEY NOT Null,
    context varchar NOT Null,
    startDate varchar,
    eventName varchar,
    childEvent varchar,
    childEventID INTEGER,
);

CREATE TABLE Matches(
    matchID,
    eventID,
    eventStage,
    bracket,
    vlrid,
    team1,
    team2,
    vctRegion,
    division,
    t1ID,
    t2ID,
    t1Score,
    t2Score,
    bestOf,
    patchID,
);

CREATE TABLE Maps(
    mapid,
    mapNum,
    maplistID,
    lengthinmilli,
    attackingfirst,
    winner,
    t1Score,
    t@score,
    vodURL,
);
CREATE Table MapStats(
    mapID,
    playerID,
    kills,
    deaths,
    assists,
    ribRating,
    ribRatingAttack,
    ribRatingDefense,
)

CREATE Table MapRounds(
    roundID,
    matchID,
    roundNum,
    winCondition,
    winnerTeam,
    ceremony,
    t1LoadoutTier,
    t2LoadoutTier,
    attickingTeam,
)

CREATE Table MapKills(
    matchId, 
    id,
    roundId, 
    killerId,
    victimId,
    roundTimeMillis,
    gameTimeMillis,
    victimLocationX,
    victimLocationY,
    damageType,
    abilityType,
    weaponId,
    secondaryFireMode,
    isfirst,
    tradedByKillId,
    tradedForKillId,
    weapon,
    weaponCategory,
    killerTeamNumber,
    victimTeamNumber,
    side,
    assistants,
)
CREATE Table xvys(
    matchId, 
    teamId, 
    teamNumber, 
    side, 
    situation, 
    team1Count, 
    team2Count, 
    delta, 
    wins, 
    losses
)

create table playerStatsonRounds{
    matchId, 
    roundId, 
    roundNumber, 
    playerId, 
    teamNumber, 
    side, 
    acs, 
    kills, 
    firstKills, 
    deaths, 
    firstDeaths, 
    assists, 
    damage, 
    headshots, 
    bodyshots, 
    legshots, 
    plants, 
    defusals, 
    clutches, 
    clutchOpponents, 
    clutchOpportunities, 
    impact, 
    kastRounds
}

create table playerStatsonMaps(
    matchId, 
    playerId, 
    score, 
    roundsPlayed, 
    kills, 
    deaths, 
    assists, 
    playtimeMillis, 
    impact, 
    rating, 
    attackingRating, 
    defendingRating
)

create table eventsonMaps(
    roundId, 
    roundNumber, 
    roundTimeMillis, 
    killId, 
    tradedByKillId, 
    tradedForKillId, 
    bombId, 
    resId, 
    playerId, 
    assists, 
    referencePlayerId, 
    eventType, 
    damageType, 
    weaponId, 
    ability, 
    impact, 
    attackingWinProbabilityBefore, 
    attackingWinProbabilityAfter, 
    attackingTeamNumber
)
create locationsonMaps(
    roundNumber, 
    playerId, 
    roundTimeMillis, 
    locationX, 
    locationY, 
    viewRadians
)
create table economiesonMaps(
    roundId, 
    roundNumber, 
    playerId, 
    agentId, 
    score, 
    weaponId, 
    armorId, 
    remainingCreds, 
    spentCreds, 
    loadoutValue, 
    survived, 
    kast
)

CREATE TABLE player(
    playerID,
    ign,
    currentTeam,
);

