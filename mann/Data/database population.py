import os
import json
import logging
import psycopg2
from pathlib import Path

# Configure logging
logging.basicConfig(filename='db_population.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Database connection settings (edit as needed)
DB_SETTINGS = {
    'dbname': 'valorant_test1',
    'user': 'postgres',
    'password': '123456',
    'host': 'localhost',
    'port': 5432
}

# Path to schema SQL
SCHEMA_PATH = 'test2.sql'
# Root data directory
DATA_ROOT = Path('./Data')


def create_tables(conn):
    """Create tables from the schema file."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    logging.info('Database schema created or verified.')


def find_json_files(root, pattern):
    """Recursively find JSON files matching the pattern."""
    return list(root.rglob(pattern))


def insert_tournament(data, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO Tournament (eventID, eventType, eventFormat, eventTier, startDate, eventName, eventSlug, childEvent, childEventSlug)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (eventID) DO NOTHING;
            ''', (
                data.get('parentEventId'),
                data.get('eventType', 'VCT'),
                data.get('eventFormat', 'LAN'),
                data.get('eventTier', 'A'),
                data.get('startDate'),
                data.get('parentEventName'),
                data.get('parentEventSlug'),
                data.get('eventChildLabel'),
                data.get('eventSlug')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped Tournament {data.get('parentEventId')}")
    except Exception as e:
        logging.error(f"Tournament insert error: {e}")


def insert_team(team, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO Teams (teamID, teamName, teamShort, region)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (teamID) DO NOTHING;
            ''', (
                team.get('id'),
                team.get('name'),
                team.get('shortName'),
                team.get('vctRegion')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped Team {team.get('id')}")
    except Exception as e:
        logging.error(f"Team insert error: {e}")


def insert_match(match, event_id, bracket, event_region_id, division, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO Matches (matchID, eventID, eventStage, bracket, vlrID, team1ID, team2ID, eventRegionID, division, t1Score, t2Score, bestOf, patchID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (matchID) DO NOTHING;
            ''', (
                match.get('id'),
                event_id,
                match.get('eventStage'),
                bracket,
                match.get('vlrId'),
                match.get('team1Id'),
                match.get('team2Id'),
                event_region_id,
                division,
                match.get('team1Score'),
                match.get('team2Score'),
                match.get('bestOf'),
                match.get('patchId')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped Match {match.get('id')}")
    except Exception as e:
        logging.error(f"Match insert error: {e}")


def insert_player(player, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO Player (playerID, ign, oldIgn, currentTeamID)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (playerID) DO NOTHING;
            ''', (
                player.get('id'),
                player.get('ign'),
                player.get('oldIgn'),
                player.get('currentTeamID')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped Player {player.get('id')}")
    except Exception as e:
        logging.error(f"Player insert error: {e}")


def insert_map(map_data, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO mapsAvailable (id, name, riotID)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            ''', (
                map_data.get('id'),
                map_data.get('name'),
                map_data.get('riotId')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped Map {map_data.get('id')}")
    except Exception as e:
        logging.error(f"Map insert error: {e}")


def insert_pickban(pickban, match_id, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMapPickBans (matchID, seqNum, teamID, mapID, pickBanType, isLeftover, teamSeqNum)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (matchID, seqNum) DO NOTHING;
            ''', (
                match_id,
                pickban.get('seqNum'),
                pickban.get('teamId'),
                pickban.get('mapId'),
                pickban.get('type'),
                pickban.get('isLeftover'),
                pickban.get('teamSeqNum')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped PickBan {match_id}-{pickban.get('seqNum')}")
    except Exception as e:
        logging.error(f"PickBan insert error: {e}")


def insert_match_map(match_map, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMaps (mapID, matchID, mapNum, lengthInMilli, attackingFirst, winner, t1Score, t2Score, vodURL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (mapID) DO NOTHING;
            ''', (
                match_map.get('id'),
                match_map.get('matchId'),
                match_map.get('mapNum'),
                match_map.get('lengthMillis'),
                match_map.get('attackingFirstTeamNumber'),
                match_map.get('winningTeamNumber'),
                match_map.get('team1Score'),
                match_map.get('team2Score'),
                match_map.get('vodUrl')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped MatchMap {match_map.get('id')}")
    except Exception as e:
        logging.error(f"MatchMap insert error: {e}")


def insert_map_stats(stats, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMapStats (mapID, playerID, kills, deaths, assists, ribRating, ribRatingAttack, ribRatingDefense)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (mapID, playerID) DO NOTHING;
            ''', (
                stats.get('mapId'),
                stats.get('playerId'),
                stats.get('kills'),
                stats.get('deaths'),
                stats.get('assists'),
                stats.get('ribRating'),
                stats.get('ribRatingAttack'),
                stats.get('ribRatingDefense')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped MapStats {stats.get('mapId')}-{stats.get('playerId')}")
    except Exception as e:
        logging.error(f"MapStats insert error: {e}")


def insert_round(round_data, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMapRounds (roundID, matchID, roundNum, winCondition, winnerTeam, ceremony, t1LoadoutTier, t2LoadoutTier, attackingTeam)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (roundID) DO NOTHING;
            ''', (
                round_data.get('id'),
                round_data.get('matchId'),
                round_data.get('number'),
                round_data.get('winCondition'),
                round_data.get('winningTeamNumber'),
                round_data.get('ceremony'),
                round_data.get('team1LoadoutTier'),
                round_data.get('team2LoadoutTier'),
                round_data.get('attackingTeamNumber')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped Round {round_data.get('id')}")
    except Exception as e:
        logging.error(f"Round insert error: {e}")


def insert_kill(kill, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMapKills (id, matchID, roundID, killerID, victimID, roundTimeMillis, gameTimeMillis, victimLocationX, victimLocationY, damageType, abilityType, weaponID, secondaryFireMode, isFirst, tradedByKillID, tradedForKillID, weapon, weaponCategory, killerTeamNumber, victimTeamNumber, side, assistants)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            ''', (
                kill.get('id'),
                kill.get('matchId'),
                kill.get('roundId'),
                kill.get('killerId'),
                kill.get('victimId'),
                kill.get('roundTimeMillis'),
                kill.get('gameTimeMillis'),
                kill.get('victimLocationX'),
                kill.get('victimLocationY'),
                kill.get('damageType'),
                kill.get('abilityType'),
                kill.get('weaponId'),
                kill.get('secondaryFireMode'),
                kill.get('first'),
                kill.get('tradedByKillId'),
                kill.get('tradedForKillId'),
                kill.get('weapon'),
                kill.get('weaponCategory'),
                kill.get('killerTeamNumber'),
                kill.get('victimTeamNumber'),
                kill.get('side'),
                json.dumps(kill.get('assistants')) if kill.get('assistants') is not None else None
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped Kill {kill.get('id')}")
    except Exception as e:
        logging.error(f"Kill insert error: {e}")


def insert_xvy(xvy, match_id, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMapXvYs (matchID, teamID, teamNumber, side, situation, team1Count, team2Count, delta, wins, losses)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            ''', (
                match_id,
                xvy.get('teamId'),
                xvy.get('teamNumber'),
                xvy.get('side'),
                xvy.get('situation'),
                xvy.get('team1Count'),
                xvy.get('team2Count'),
                xvy.get('delta'),
                xvy.get('wins'),
                xvy.get('losses')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped XvY for match {match_id} team {xvy.get('teamId')}")
    except Exception as e:
        logging.error(f"XvY insert error: {e}")


def insert_player_stats_on_rounds(stat, match_id, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMapPlayerStatsOnRounds (matchID, roundID, roundNumber, playerID, teamNumber, side, acs, kills, firstKills, deaths, firstDeaths, assists, damage, headshots, bodyshots, legshots, plants, defusals, clutches, clutchOpponents, clutchOpportunities, impact, kastRounds)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            ''', (
                match_id,
                stat.get('roundId'),
                stat.get('roundNumber'),
                stat.get('playerId'),
                stat.get('teamNumber'),
                stat.get('side'),
                stat.get('acs'),
                stat.get('kills'),
                stat.get('firstKills'),
                stat.get('deaths'),
                stat.get('firstDeaths'),
                stat.get('assists'),
                stat.get('damage'),
                stat.get('headshots'),
                stat.get('bodyshots'),
                stat.get('legshots'),
                stat.get('plants'),
                stat.get('defusals'),
                stat.get('clutches'),
                stat.get('clutchOpponents'),
                stat.get('clutchOpportunities'),
                stat.get('impact'),
                stat.get('kastRounds')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped PlayerStatsOnRounds for match {match_id} player {stat.get('playerId')}")
    except Exception as e:
        logging.error(f"PlayerStatsOnRounds insert error: {e}")


def insert_player_stats_on_maps(stat, match_id, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMapPlayerStatsOnMaps (matchID, playerID, score, roundsPlayed, kills, deaths, assists, playtimeMillis, impact, rating, attackingRating, defendingRating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            ''', (
                match_id,
                stat.get('playerId'),
                stat.get('score'),
                stat.get('roundsPlayed'),
                stat.get('kills'),
                stat.get('deaths'),
                stat.get('assists'),
                stat.get('playtimeMillis'),
                stat.get('impact'),
                stat.get('rating'),
                stat.get('attackingRating'),
                stat.get('defendingRating')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped PlayerStatsOnMaps for match {match_id} player {stat.get('playerId')}")
    except Exception as e:
        logging.error(f"PlayerStatsOnMaps insert error: {e}")


def insert_events_on_maps(event, conn):
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO matchMapEventsOnMaps (roundID, roundNumber, roundTimeMillis, killID, tradedByKillID, tradedForKillID)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            ''', (
                event.get('roundId'),
                event.get('roundNumber'),
                event.get('roundTimeMillis'),
                event.get('killId'),
                event.get('tradedByKillId'),
                event.get('tradedForKillId')
            ))
        conn.commit()
        logging.info(f"Inserted/Skipped EventOnMap for round {event.get('roundId')}")
    except Exception as e:
        logging.error(f"EventOnMap insert error: {e}")


def process_match_data(match, conn):
    # Insert match map
    if 'map' in match:
        insert_map(match['map'], conn)
    # Insert stats
    if 'stats' in match:
        for stat in match['stats']:
            insert_map_stats(stat, conn)
    # Insert rounds
    if 'rounds' in match:
        for round_data in match['rounds']:
            insert_round(round_data, conn)
    # Insert kills
    if 'kills' in match:
        for kill in match['kills']:
            insert_kill(kill, conn)
    # Insert XvY
    if 'xvy' in match:
        for xvy in match['xvy']:
            insert_xvy(xvy, match.get('id'), conn)
    # Insert PlayerStatsOnRounds
    if 'playerStatsOnRounds' in match:
        for stat in match['playerStatsOnRounds']:
            insert_player_stats_on_rounds(stat, match.get('id'), conn)
    # Insert PlayerStatsOnMaps
    if 'playerStatsOnMaps' in match:
        for stat in match['playerStatsOnMaps']:
            insert_player_stats_on_maps(stat, match.get('id'), conn)
    # Insert EventsOnMaps
    if 'eventsOnMaps' in match:
        for event in match['eventsOnMaps']:
            insert_events_on_maps(event, conn)
    # TODO: Process and insert other nested data (Locations, Economies, etc.)


def process_extra_json(path, conn):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Insert Tournament
        insert_tournament(data, conn)
        # Insert Teams
        if 'team1' in data:
            insert_team(data['team1'], conn)
        if 'team2' in data:
            insert_team(data['team2'], conn)
        # Insert Matches
        if 'matches' in data:
            for match in data['matches']:
                insert_match(
                    match,
                    data.get('parentEventId'),
                    data.get('bracket'),
                    data.get('eventRegionId'),
                    data.get('division', 'VCT'),
                    conn
                )
                process_match_data(match, conn)
        # Insert PickBans
        if 'pickban' in data:
            for pickban in data['pickban']:
                insert_pickban(pickban, data.get('id'), conn)
        # TODO: Insert players, agents, abilities, weapons, armor, regions, patches, etc.
    except Exception as e:
        logging.error(f'Error processing {path}: {e}')


def main():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        create_tables(conn)
        extra_files = find_json_files(DATA_ROOT, '*_extra.json')
        logging.info(f'Found {len(extra_files)} *_extra.json files.')
        for file_path in extra_files:
            process_extra_json(file_path, conn)
        conn.close()
        logging.info('Database population complete.')
    except Exception as e:
        logging.error(f'Fatal error: {e}')


if __name__ == '__main__':
    main()
