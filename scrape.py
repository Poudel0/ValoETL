import requests
import json
import os
import pandas as pd
# from helium import *

url = "https://www.rib.gg/series/sentinels-vs-g2-esports-champions-tour-2025-americas-stage-1/89503"


def scrape(url):
    response = requests.get(url)

    if response.status_code == 200:
        start_index= response.text.find('<script id="__NEXT_DATA__" type="application/json">' )
        start_index= start_index + len('<script id="__NEXT_DATA__" type="application/json">')
        end_index= response.text.find('</script>',start_index)
        json_string = response.text[start_index:end_index].strip()

        stats_data_raw = json.loads(json_string)

        return stats_data_raw
    else:
        print('Failed trying to scrape')
        return None
    # matchesplayed =[]
    # matches = stats_data_raw['props']['pageProps']['series']['matches']
    # for match in matches:
    #     matchesplayed.append(matches[match]['id'])

    
def update_ign_and_id(stats_data):
    data = stats_data

    # Extract player data
    matches = data['props']['pageProps']['series']['matches']

    # Create lists to store IDs and in-game names (IGNs)
    ids = []
    igns = []

    # Iterate over all matches to retrieve player data
    for match in matches:
        players = match['players']
        for player_obj in players:
            ids.append(player_obj['player']['id'])
            igns.append(player_obj['player']['ign'])

    # Create a DataFrame from the lists without adding index column
    df = pd.DataFrame({'id': ids, 'name': igns})
    df = df.drop_duplicates(subset=['id', 'name'])

    # Check if the CSV file exists
    csv_file = 'ignfile.csv'
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        # Read existing data from the CSV file
        existing_df = pd.read_csv(csv_file)
    else:
        # Initialize existing_df as an empty DataFrame
        existing_df = pd.DataFrame()

    # Combine existing data with new data from DataFrame
    combined_df = pd.concat([existing_df, df], ignore_index=True)

    # Drop duplicates based on ID and IGN
    combined_df = combined_df.drop_duplicates(subset=['id', 'name'])


    # Write the combined data to the CSV file without index
    combined_df.to_csv(csv_file, index=False)


def update_team(stats_data):
    data = stats_data

    keys= ['id', 'name', 'shortName']

    # Extract matches data
    t1 = data['props']['pageProps']['series']['team1']
    team1 = {key: t1[key] for key in keys}

    t2 = data['props']['pageProps']['series']['team2']
    team2 = {key: t2[key] for key in keys}


    df1= pd.DataFrame([team1]).drop_duplicates(subset=keys)
    df2= pd.DataFrame([team2]).drop_duplicates(subset=keys)


    # Check if the CSV file exists
    csv_file = 'teamfile.csv'
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        # Read existing data from the CSV file
        existing_df = pd.read_csv(csv_file)
    else:
        # Initialize existing_df as an empty DataFrame
        existing_df = pd.DataFrame()

    # Combine existing data with new data from DataFrames
    combined_df = pd.concat([existing_df, df1, df2], ignore_index=True)

    # Drop duplicates based on ID, name, and shortName again to ensure no duplicates when combining
    combined_df = combined_df.drop_duplicates(subset=['id', 'name', 'shortName'])

    # Write the combined data to the CSV file without index
    combined_df.to_csv(csv_file, index=False)

def update_abilities(stats_data):
    abilities = stats_data['props']['pageProps']['content']['abilities']

    # Create lagentsts to store agentDs and agentn-game names (IGNs)
    ids = []
    names = []
    types= []
    agentId=[]
    damages=[]

    for agent in abilities:
        ids.append(agent['id'])
        names.append(agent['name'])
        types.append(agent['type'])
        agentId.append(agent['agentId'])
        damages.append(agent['damages'])

    df = pd.DataFrame({'id': ids, 'name': names, 'type': types, 'agentId': agentId, 'damages':damages})
    # df = df.drop_duplicates(subset=['id', 'name','roleId','role'])

        # Check if the CSV file exists
    csv_file = 'abilities.csv'
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
            # Read existing data from the CSV file
            existing_df = pd.read_csv(csv_file)
    else:
            # Initialize existing_df as an empty DataFrame
            existing_df = pd.DataFrame()

        # Combine existing data with new data from DataFrame
    combined_df = pd.concat([existing_df, df], ignore_index=True)

        # Drop duplicates based on ID and IGN
    combined_df = combined_df.drop_duplicates(subset=['id', 'name', 'type','agentId', 'damages'])


        # Write the combined data to the CSV file without index
    combined_df.to_csv(csv_file, index=False)

def scrapeTourney(tourney_url):
    response = requests.get(url)

    if response.status_code == 200:
        start_index= response.text.find('<script id="__NEXT_DATA__" type="application/json">' )
        start_index= start_index + len('<script id="__NEXT_DATA__" type="application/json">')
        end_index= response.text.find('</script>',start_index)
        json_string = response.text[start_index:end_index].strip()

        stats_data_raw = json.loads(json_string)

        # return stats_data_raw
    else:
        print('Failed trying to scrape')
        # return None 
    winners = stats_data_raw['props']['pageProps']['event']['childEvents'][0]['bracketJson']['winners']

    extracted_data = []

    for round_data in winners:
        bracket = round_data['title']
        for seed in round_data['seeds']:
            series_id = seed['seriesId']
            extracted_data.append({'bracket': bracket, 'seriesId': series_id})
    
    




stats_data_raw = scrape(url)
# update_ign_and_id(stats_data_raw)
# update_team(stats_data_raw)
# update_abilities(stats_data_raw)
with open("stats_raw_json.json",'w') as json_file:
    json.dump(stats_data_raw,json_file,indent=4)



