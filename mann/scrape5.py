import requests
import json
import os
import pandas as pd
import time
import re

# File to store scraped seriesIds
scraped_series_ids_file = 'scraped_series_ids.txt'


tourney_urls_file = 'tourney_urls.txt'


# Function to sanitize filenames and directory names
def sanitize_filename(filename):
    filename= re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename

# Function to load scraped seriesIds from file
def load_scraped_series_ids():
    if os.path.exists(scraped_series_ids_file):
        with open(scraped_series_ids_file, 'r') as file:
            return file.read().splitlines()
    else:
        return []

# Function to save scraped seriesIds to file
def save_scraped_series_ids(scraped_series_ids):
    with open(scraped_series_ids_file, 'w') as file:
        for series_id in scraped_series_ids:
            file.write(f"{series_id}\n")

# Load scraped seriesIds from file
scraped_series_ids = load_scraped_series_ids()

# Function to extract JSON data from HTML
def extract_json_data(response_text):
    start_index = response_text.find('<script id="__NEXT_DATA__" type="application/json">')
    start_index += len('<script id="__NEXT_DATA__" type="application/json">')
    end_index = response_text.find('</script>', start_index)
    json_string = response_text[start_index:end_index].strip()
    return json.loads(json_string)

# Function to get series header data and match IDs
def SeriesHeader(seriesId):
    print(f"Fetching series header data for series ID: {seriesId}")
    url = f'https://www.rib.gg/series/{seriesId}'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'Failed trying to scrape series header: {e}')
        return None, None

    stats_data_raw = extract_json_data(response.text)
    matches = stats_data_raw['props']['pageProps']['series']['matches']
    match_ids = [match['id'] for match in matches]
    return stats_data_raw, match_ids

# Function to update IGN and ID data
def update_ign_and_id(stats_data):
    print("Updating IGN and ID data")
    csv_file = 'ignfile.csv'
    
    matches = stats_data['props']['pageProps']['series']['matches']
    ids, igns = [], []

    for match in matches:
        players = match['players']
        for player_obj in players:
            ids.append(player_obj['player']['id'])
            igns.append(player_obj['player']['ign'])

    df = pd.DataFrame({'id': ids, 'name': igns}).drop_duplicates(subset=['id', 'name'])

    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        existing_df = pd.read_csv(csv_file)
    else:
        existing_df = pd.DataFrame()

    combined_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset=['id', 'name'])
    try:
        combined_df.to_csv(csv_file, index=False)
        print(f"IGN and ID data saved to {csv_file}")
    except Exception as e:
        print(f"Failed to save IGN and ID data: {e}")

# Function to update team data
def update_team(stats_data):
    print("Updating team data")
    csv_file = 'teamfile.csv'

    keys = ['id', 'name', 'shortName']
    t1 = stats_data['props']['pageProps']['series']['team1']
    t2 = stats_data['props']['pageProps']['series']['team2']

    df1 = pd.DataFrame([t1], columns=keys).drop_duplicates(subset=keys)
    df2 = pd.DataFrame([t2], columns=keys).drop_duplicates(subset=keys)

    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        existing_df = pd.read_csv(csv_file)
    else:
        existing_df = pd.DataFrame()

    combined_df = pd.concat([existing_df, df1, df2], ignore_index=True).drop_duplicates(subset=keys)
    try:
        combined_df.to_csv(csv_file, index=False)
        print(f"Team data saved to {csv_file}")
    except Exception as e:
        print(f"Failed to save team data: {e}")

# Function to update abilities data
def update_abilities(stats_data):
    print("Updating abilities data")
    csv_file = 'abilities.csv'

    abilities = stats_data['props']['pageProps']['content']['abilities']

    ids, names, types, agentId, damages = [], [], [], [], []

    for agent in abilities:
        ids.append(agent['id'])
        names.append(agent['name'])
        types.append(agent['type'])
        agentId.append(agent['agentId'])
        damages.append(agent['damages'])

    df = pd.DataFrame({'id': ids, 'name': names, 'type': types, 'agentId': agentId, 'damages': damages})

    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        existing_df = pd.read_csv(csv_file)
    else:
        existing_df = pd.DataFrame()

    combined_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset=['id', 'name', 'type', 'agentId', 'damages'])
    try:
        combined_df.to_csv(csv_file, index=False)
        print(f"Abilities data saved to {csv_file}")
    except Exception as e:
        print(f"Failed to save abilities data: {e}")

# Function to process bracketJson for different types
def process_bracket_json(bracketJson, bracket_title):
    series_ids = []

    bracket_type = bracketJson['type']
    if bracket_type == 'weekly':
        for week in bracketJson['weekly']['weeks']:
            for series in week['series']:
                series_ids.append(series['id'])
    elif bracket_type == 'double':
        for section in ['winners', 'losers']:
            for round_data in bracketJson[section]:
                for seed in round_data['seeds']:
                    series_ids.append(seed['seriesId'])
    elif bracket_type == 'single':
        for section in ['winners']:
            for round_data in bracketJson[section]:
                for seed in round_data['seeds']:
                    series_ids.append(seed['seriesId'])
    elif bracket_type == 'group':
        for group in bracketJson.get('groups', []):
            for seed in group.get('seeds', []):
                series_ids.append(seed.get('id'))
    else:
        print(f"Unhandled bracket type: {bracket_type}")

    return bracket_type, series_ids

def scrapeSeries(series_url):
    series_id = series_url.rstrip('/').split('/')[-1]
    if series_id in scraped_series_ids:
        print(f"Series ID {series_id} already scraped. Skipping...")
        return

    print(f"Scraping data for series ID: {series_id}")
    header_for_extra_data, match_ids = SeriesHeader(series_id)
    if header_for_extra_data is not None:
        bracket_folder = os.path.abspath(f'./Data/{series_id}')
        os.makedirs(bracket_folder, exist_ok=True)
        print(f"Created directory for series ID {series_id} at {bracket_folder}")

        # Save series data to series_id_extra.json
        series_data = header_for_extra_data['props']['pageProps']['series']
        with open(f'{bracket_folder}/{series_id}_extra.json', 'w') as json_file:
            json.dump(series_data, json_file)
        print(f"Series extra data saved to {bracket_folder}/{series_id}_extra.json")

        update_abilities(header_for_extra_data)
        update_ign_and_id(header_for_extra_data)
        update_team(header_for_extra_data)
        for match_id in match_ids:
            print(f"Fetching details for match ID: {match_id}")
            try:
                response = requests.get(f'https://be-prod.rib.gg/v1/matches/{match_id}/details')
                response.raise_for_status()
                details = response.json()
                with open(f'{bracket_folder}/{match_id}_details.json', 'w') as json_file:
                    json.dump(details, json_file)
                print(f"Details for match ID {match_id} saved to {bracket_folder}")
            except requests.RequestException as e:
                print(f'Failed to fetch details for match ID {match_id}: {e}')
            except json.JSONDecodeError:
                print(f"Failed to decode JSON for match ID {match_id}")
            time.sleep(3)

        scraped_series_ids.append(series_id)
        save_scraped_series_ids(scraped_series_ids)


# Function to scrape tournament data
# Function to scrape tournament data
def scrapeTourney(tourney_url):
    print(f"Scraping tournament data from URL: {tourney_url}\n")
    try:
        response = requests.get(tourney_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'Failed trying to scrape tournament data: {e}\n')
        return

    stats_data_raw = extract_json_data(response.text)
    child_events = stats_data_raw['props']['pageProps']['event']['childEvents']

    for event in child_events:
        event_title = sanitize_filename(event.get('name', 'unknown_event'))
        event_folder = os.path.abspath(f'./Data/{event_title}')
        os.makedirs(event_folder, exist_ok=True)
        bracketJson = event.get('bracketJson', {})
        
        if not bracketJson:
            print(f"\nNo bracketJson found for event: {event_title}\n")
            continue

        bracket_type, series_ids = process_bracket_json(bracketJson, event_title)

        for series_id in series_ids:
            if series_id in scraped_series_ids:
                print(f"Series ID {series_id} already scraped. Skipping...")
                continue

            bracket_folder = os.path.abspath(f'./Data/{event_title}/{bracket_type}/{series_id}')
            os.makedirs(bracket_folder, exist_ok=True)
            # print(f"Created directory for series ID {series_id} at {bracket_folder}")

            header_for_extra_data, match_ids = SeriesHeader(series_id)
            if header_for_extra_data is not None:
                with open(f'{bracket_folder}/{series_id}_extra.json', 'w') as json_file:
                    json.dump(header_for_extra_data['props']['pageProps']['series'], json_file)
                # update_abilities(header_for_extra_data)
                update_ign_and_id(header_for_extra_data)
                update_team(header_for_extra_data)
                for match_id in match_ids:
                    print(f"Fetching details for match ID: {match_id}")
                    try:
                        response = requests.get(f'https://be-prod.rib.gg/v1/matches/{match_id}/details')
                        response.raise_for_status()
                        details = response.json()
                        with open(f'{bracket_folder}/{match_id}_details.json', 'w') as json_file:
                            json.dump(details, json_file)
                        # print(f"Details for match ID {match_id} saved to {bracket_folder}")
                    except requests.RequestException as e:
                        print(f'Failed to fetch details for match ID {match_id}: {e}')
                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON for match ID {match_id}")
                    time.sleep(2)

            scraped_series_ids.append(series_id)
            save_scraped_series_ids(scraped_series_ids)

# Function to scrape multiple tournaments from a list of URLs
def scrapeAllTourney(tourney_urls_file):
    if os.path.exists(tourney_urls_file):
        with open(tourney_urls_file, 'r') as file:
            tourney_urls = file.read().splitlines()
            for tourney_url in tourney_urls:
                time.sleep(10)  # Add a delay between requests to avoid overloading the server
                scrapeTourney(tourney_url)
    else:
        print(f"No such file: {tourney_urls_file}")

# Uncomment to run scraping
# scrapeTourney(tourney_url)
# scrapeSeries(series_url)
# To scrape all tournaments from the tourney_urls.txt file
scrapeAllTourney(tourney_urls_file)
