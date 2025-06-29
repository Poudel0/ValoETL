import os
import json
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValorantDataProcessor:
    def __init__(self, db_config):
        """
        Initialize the data processor with database configuration
        
        db_config should contain: host, database, user, password, port
        """
        self.db_config = db_config
        self.conn = None
        
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute SQL query with error handling"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                self.conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def insert_tournament(self, event_data):
        """Insert tournament data"""
        query = """
        INSERT INTO Tournament (eventID, eventType, eventFormat, eventTier, startDate, 
                              eventName, eventSlug, childEvent, childEventSlug)
        VALUES (%(eventID)s, %(eventType)s, %(eventFormat)s, %(eventTier)s, %(startDate)s,
                %(eventName)s, %(eventSlug)s, %(childEvent)s, %(childEventSlug)s)
        ON CONFLICT (eventID) DO UPDATE SET
            eventName = EXCLUDED.eventName,
            startDate = EXCLUDED.startDate
        """
        
        # Map the event data to database fields
        tournament_data = {
            'eventID': event_data.get('parentEventId'),
            'eventType': event_data.get('eventType', 'VCT'),
            'eventFormat': event_data.get('eventFormat', 'LAN'),
            'eventTier': self._determine_event_tier(event_data.get('parentEventName', '')),
            'startDate': self._parse_date(event_data.get('startDate')),
            'eventName': event_data.get('parentEventName'),
            'eventSlug': event_data.get('parentEventSlug'),
            'childEvent': event_data.get('eventChildLabel'),
            'childEventSlug': event_data.get('eventSlug')
        }
        
        self.execute_query(query, tournament_data)
        logger.info(f"Inserted tournament: {tournament_data['eventName']}")
    
    def insert_teams(self, team_data_list):
        """Insert team data"""
        query = """
        INSERT INTO Teams (teamID, teamName, teamShort, region)
        VALUES (%(teamID)s, %(teamName)s, %(teamShort)s, %(region)s)
        ON CONFLICT (teamID) DO UPDATE SET
            teamName = EXCLUDED.teamName,
            teamShort = EXCLUDED.teamShort
        """
        
        for team in team_data_list:
            team_params = {
                'teamID': team.get('id'),
                'teamName': team.get('name'),
                'teamShort': team.get('shortName'),
                'region': team.get('region')  # May need to be extracted differently
            }
            self.execute_query(query, team_params)
        
        logger.info(f"Inserted {len(team_data_list)} teams")
    
    def insert_players(self, player_data_list):
        """Insert player data"""
        query = """
        INSERT INTO Player (playerID, ign, oldIgn, currentTeamID)
        VALUES (%(playerID)s, %(ign)s, %(oldIgn)s, %(currentTeamID)s)
        ON CONFLICT (playerID) DO UPDATE SET
            ign = EXCLUDED.ign,
            currentTeamID = EXCLUDED.currentTeamID
        """
        
        for player in player_data_list:
            player_params = {
                'playerID': player.get('id'),
                'ign': player.get('ign'),
                'oldIgn': player.get('oldIgn'),
                'currentTeamID': player.get('currentTeamID')
            }
            self.execute_query(query, player_params)
        
        logger.info(f"Inserted {len(player_data_list)} players")
    
    def insert_match(self, match_data, event_id):
        """Insert match data"""
        query = """
        INSERT INTO Matches (matchID, eventID, eventStage, bracket, vlrID, team1ID, team2ID,
                           eventRegionID, division, t1Score, t2Score, bestOf, patchID)
        VALUES (%(matchID)s, %(eventID)s, %(eventStage)s, %(bracket)s, %(vlrID)s, %(team1ID)s,
                %(team2ID)s, %(eventRegionID)s, %(division)s, %(t1Score)s, %(t2Score)s,
                %(bestOf)s, %(patchID)s)
        ON CONFLICT (matchID) DO UPDATE SET
            t1Score = EXCLUDED.t1Score,
            t2Score = EXCLUDED.t2Score
        """
        
        match_params = {
            'matchID': match_data.get('id'),
            'eventID': event_id,
            'eventStage': match_data.get('eventStage'),
            'bracket': match_data.get('bracket'),
            'vlrID': match_data.get('vlrid'),
            'team1ID': match_data.get('team1', {}).get('id'),
            'team2ID': match_data.get('team2', {}).get('id'),
            'eventRegionID': match_data.get('eventRegionID'),
            'division': match_data.get('division'),
            't1Score': match_data.get('team1Score'),
            't2Score': match_data.get('team2Score'),
            'bestOf': match_data.get('bestOf'),
            'patchID': match_data.get('patchID')
        }
        
        self.execute_query(query, match_params)
        logger.info(f"Inserted match: {match_params['matchID']}")
    
    def insert_match_maps(self, maps_data, match_id):
        """Insert match maps data"""
        query = """
        INSERT INTO matchMaps (mapID, matchID, mapNum, lengthInMilli, attackingFirst,
                             winner, t1Score, t2Score, vodURL)
        VALUES (%(mapID)s, %(matchID)s, %(mapNum)s, %(lengthInMilli)s, %(attackingFirst)s,
                %(winner)s, %(t1Score)s, %(t2Score)s, %(vodURL)s)
        ON CONFLICT (mapID) DO UPDATE SET
            winner = EXCLUDED.winner,
            t1Score = EXCLUDED.t1Score,
            t2Score = EXCLUDED.t2Score
        """
        
        for i, map_data in enumerate(maps_data):
            map_params = {
                'mapID': map_data.get('id'),
                'matchID': match_id,
                'mapNum': i + 1,
                'lengthInMilli': map_data.get('lengthInMillis'),
                'attackingFirst': map_data.get('attackingFirst'),
                'winner': map_data.get('winner'),
                't1Score': map_data.get('team1Score'),
                't2Score': map_data.get('team2Score'),
                'vodURL': map_data.get('vodURL')
            }
            self.execute_query(query, map_params)
        
        logger.info(f"Inserted {len(maps_data)} maps for match {match_id}")
    
    def insert_map_stats(self, stats_data, map_id):
        """Insert map stats data"""
        query = """
        INSERT INTO matchMapStats (mapID, playerID, kills, deaths, assists, ribRating,
                                 ribRatingAttack, ribRatingDefense)
        VALUES (%(mapID)s, %(playerID)s, %(kills)s, %(deaths)s, %(assists)s, %(ribRating)s,
                %(ribRatingAttack)s, %(ribRatingDefense)s)
        ON CONFLICT (mapID, playerID) DO UPDATE SET
            kills = EXCLUDED.kills,
            deaths = EXCLUDED.deaths,
            assists = EXCLUDED.assists,
            ribRating = EXCLUDED.ribRating
        """
        
        for player_stats in stats_data:
            stats_params = {
                'mapID': map_id,
                'playerID': player_stats.get('playerId'),
                'kills': player_stats.get('kills'),
                'deaths': player_stats.get('deaths'),
                'assists': player_stats.get('assists'),
                'ribRating': player_stats.get('ribRating'),
                'ribRatingAttack': player_stats.get('ribRatingAttack'),
                'ribRatingDefense': player_stats.get('ribRatingDefense')
            }
            self.execute_query(query, stats_params)
        
        logger.info(f"Inserted stats for {len(stats_data)} players on map {map_id}")
    
    def insert_reference_data(self):
        """Insert reference data that has no dependencies"""
        logger.info("Inserting reference data...")
        
        # Insert regions (if you have region data)
        regions_data = [
            {'regionID': 1, 'name': 'Americas'},
            {'regionID': 2, 'name': 'EMEA'},
            {'regionID': 3, 'name': 'Pacific'},
            {'regionID': 4, 'name': 'China'}
        ]
        
        region_query = """
        INSERT INTO Regions (regionID, name)
        VALUES (%(regionID)s, %(name)s)
        ON CONFLICT (regionID) DO NOTHING
        """
        
        for region in regions_data:
            try:
                self.execute_query(region_query, region)
            except Exception as e:
                logger.error(f"Failed to insert region {region['name']}: {e}")
        
        # Insert maps available (if you have map data)
        # This would need to be populated based on your actual map data
        # For now, adding common Valorant maps
        maps_data = [
            {'id': 1, 'name': 'Ascent', 'riotID': 'ascent'},
            {'id': 2, 'name': 'Bind', 'riotID': 'bind'},
            {'id': 3, 'name': 'Haven', 'riotID': 'haven'},
            {'id': 4, 'name': 'Split', 'riotID': 'split'},
            {'id': 5, 'name': 'Icebox', 'riotID': 'icebox'},
            {'id': 6, 'name': 'Breeze', 'riotID': 'breeze'},
            {'id': 7, 'name': 'Fracture', 'riotID': 'fracture'},
            {'id': 8, 'name': 'Pearl', 'riotID': 'pearl'},
            {'id': 9, 'name': 'Lotus', 'riotID': 'lotus'},
            {'id': 10, 'name': 'Sunset', 'riotID': 'sunset'}
        ]
        
        maps_query = """
        INSERT INTO mapsAvailable (id, name, riotID)
        VALUES (%(id)s, %(name)s, %(riotID)s)
        ON CONFLICT (id) DO NOTHING
        """
        
        for map_data in maps_data:
            try:
                self.execute_query(maps_query, map_data)
            except Exception as e:
                logger.error(f"Failed to insert map {map_data['name']}: {e}")
        
        logger.info("Reference data insertion completed")
    
    def insert_rounds_data(self, rounds_data, match_id, map_id):
        """Insert rounds data - placeholder for rounds processing"""
        # This will need to be implemented based on the actual structure of rounds data
        logger.info(f"Processing {len(rounds_data)} rounds for map {map_id}")
        # TODO: Implement rounds, kills, events processing
    
    def collect_all_data(self, data_folder_path):
        """Collect all data files for ordered processing"""
        extra_files = []
        details_files = []
        
        for root, dirs, files in os.walk(data_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.endswith('_extra.json'):
                    extra_files.append(file_path)
                elif file.endswith('_details.json'):
                    details_files.append(file_path)
        
        return extra_files, details_files
    
    def process_data_folder(self, data_folder_path):
        """Process all data in the correct hierarchical order"""
        logger.info("Starting hierarchical data processing...")
        
        # Collect all files first
        extra_files, details_files = self.collect_all_data(data_folder_path)
        
        # PHASE 1: Extract and collect all data without inserting
        logger.info("Phase 1: Collecting all data...")
        all_tournaments = {}
        all_teams = {}
        all_players = {}
        all_matches = {}
        all_maps = {}
        all_agents = {}
        all_weapons = {}
        all_abilities = {}
        
        # Process extra files for metadata
        for file_path in extra_files:
            try:
                logger.info(f"Collecting from extra file: {file_path}")
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Collect tournament data
                if 'event' in data:
                    event = data['event']
                    all_tournaments[event.get('parentEventId')] = event
                
                # Collect team data
                if 'team1' in data:
                    team = data['team1']
                    all_teams[team.get('id')] = team
                if 'team2' in data:
                    team = data['team2']
                    all_teams[team.get('id')] = team
                
                # Collect match and player data
                if 'matches' in data:
                    for match in data['matches']:
                        all_matches[match.get('id')] = {
                            'match_data': match,
                            'event_id': data.get('event', {}).get('parentEventId')
                        }
                        
                        # Collect players from matches
                        for player_obj in match.get('players', []):
                            if 'player' in player_obj:
                                player = player_obj['player']
                                all_players[player.get('id')] = player
                
            except Exception as e:
                logger.error(f"Error collecting from file {file_path}: {e}")
                continue
        
        # Process details files for detailed data
        for file_path in details_files:
            try:
                logger.info(f"Collecting from details file: {file_path}")
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                match_id = data.get('matchId')
                
                # Collect maps data
                if 'maps' in data:
                    for map_data in data['maps']:
                        all_maps[map_data.get('id')] = {
                            'map_data': map_data,
                            'match_id': match_id
                        }
                
                # Collect agents, weapons, abilities if present
                # (This depends on your JSON structure - adjust as needed)
                
            except Exception as e:
                logger.error(f"Error collecting from file {file_path}: {e}")
                continue
        
        # PHASE 2: Insert in correct hierarchical order
        logger.info("Phase 2: Inserting data in hierarchical order...")
        
        try:
            # Step 1: Insert reference data (no dependencies)
            logger.info("Step 1: Inserting reference data...")
            self.insert_reference_data()
            
            # Step 2: Insert tournaments
            logger.info("Step 2: Inserting tournaments...")
            for tournament_id, tournament_data in all_tournaments.items():
                try:
                    self.insert_tournament(tournament_data)
                except Exception as e:
                    logger.error(f"Failed to insert tournament {tournament_id}: {e}")
            
            # Step 3: Insert teams
            logger.info("Step 3: Inserting teams...")
            for team_id, team_data in all_teams.items():
                try:
                    self.insert_teams([team_data])
                except Exception as e:
                    logger.error(f"Failed to insert team {team_id}: {e}")
            
            # Step 4: Insert players
            logger.info("Step 4: Inserting players...")
            for player_id, player_data in all_players.items():
                try:
                    self.insert_players([player_data])
                except Exception as e:
                    logger.error(f"Failed to insert player {player_id}: {e}")
            
            # Step 5: Insert matches
            logger.info("Step 5: Inserting matches...")
            for match_id, match_info in all_matches.items():
                try:
                    self.insert_match(match_info['match_data'], match_info['event_id'])
                except Exception as e:
                    logger.error(f"Failed to insert match {match_id}: {e}")
            
            # Step 6: Insert maps and their dependent data
            logger.info("Step 6: Inserting maps and dependent data...")
            for map_id, map_info in all_maps.items():
                try:
                    # Insert the map
                    self.insert_match_maps([map_info['map_data']], map_info['match_id'])
                    
                    # Insert map stats
                    if 'playerStats' in map_info['map_data']:
                        self.insert_map_stats(map_info['map_data']['playerStats'], map_id)
                    
                    # Insert rounds and other detailed data
                    if 'rounds' in map_info['map_data']:
                        self.insert_rounds_data(map_info['map_data']['rounds'], 
                                              map_info['match_id'], map_id)
                
                except Exception as e:
                    logger.error(f"Failed to insert map {map_id}: {e}")
            
            logger.info("Hierarchical data processing completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during hierarchical processing: {e}")
            raise
    
    def _determine_event_tier(self, event_name):
        """Determine event tier based on event name"""
        event_name_lower = event_name.lower()
        if 'champions' in event_name_lower:
            return 'SSS'
        elif 'masters' in event_name_lower:
            return 'SS'
        elif any(region in event_name_lower for region in ['americas', 'pacific', 'emea', 'china']):
            return 'A'
        else:
            return 'B'  # Default tier
    
    def _parse_date(self, date_string):
        """Parse date string to timestamp"""
        if not date_string:
            return None
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except:
            return None

def main():
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'valorant_test1',
        'user': 'postgres',
        'password': 'Password',
        'port': 5432
    }
    
    # Initialize processor
    processor = ValorantDataProcessor(db_config)
    
    try:
        # Connect to database
        processor.connect_db()
        
        # Process all data in the Data folder
        data_folder = './Data'
        processor.process_data_folder(data_folder)
        
        logger.info("Data processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
    
    finally:
        processor.close_db()

if __name__ == "__main__":
    main()