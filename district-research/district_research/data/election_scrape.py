"""Code to scrape and clean data from USA Today and CNN to create the 2020 
    congressional election results. Combine both sources to get full coverage
    of elections.
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import numpy as np
import json

def _create_2020_results(soup):
    """Uses a soup object returned from parsing USA Today to get election
        metadata for a given house race.

        Args:
            soup (BeautifulSoup): parsed html object that contains election
            metadata
        Returns:
            A DataFrame of election metadata for a given house race.
    """
    # state and district
    race = soup.find('h4', {'class': 'result-table-header'}).text
    
    results = soup.find('div', {'class': 'result-table-container'}).find('tr', {'class': 'result-table-row'})
    
    # candidate name and party
    candidates = results.find_all('td', {'class': 'result-table-col-candidate'})
    candidates = [re.sub('(?:\d|,|%|\.)', '', x.text.replace('\n', ' ')) for x in candidates]
    candidates = [re.search('([A-Za-z\s\.\-]+ \([A-Z]+\))', x).group(1) for x in candidates]
    
    # votes and percent
    vote_info = results.find_all('td', {'class': 'result-table-col-votes'})
    vote_info = [re.search('((?:\d+)).*\D(\d+\.\d+).*', str(x).replace(',','').replace('%', '')) for x in vote_info]
    vote_info = [[x.group(1), x.group(2)] for x in vote_info]
    
    # Separating candidate and party to match politico schema, plus good for 
    # analysis. Separating the state and district out from race because we need
    # to get the state abbreviation for each state from state_codes
    res_df = pd.DataFrame(vote_info, columns = ['candidatevotes', 'candidatepct'])
    res_df['race'] = race
    res_df['candidate'] = candidates

    return res_df


def scrape_usa_today():
    """Scrapes USA Today for 2020 election data for house general elections."""
    url = 'https://www.usatoday.com/elections/results/2020-11-03/us-house/'
    response = requests.get(url)
    html = response.text.encode()
    soup = BeautifulSoup(html, 'html.parser')
    # each block represents a district race
    data = soup.find_all('div', {'class': 'result-table-block'})
    usa_today = pd.concat([_create_2020_results(x) for x in data])

    usa_today[['candidate', 'party']] = usa_today['candidate'].str.extract('(.*) \(([A-Z]+)\)')
    usa_today[['state', 'district']] = usa_today['race'].str.extract('(.*) District (\d+)')
    usa_today['stage'] = 'gen'
    
    # will always be 2020
    usa_today['year'] = 2020

    return (
        usa_today[[
            'year', 'state', 'district', 'candidate', 
            'party', 'candidatevotes', 'stage'
        ]]
    )


def _create_df_from_records(candidate_jsons, i):
    df = pd.DataFrame.from_records(candidate_jsons)
    df['district'] = i
    return df


def _create_2020_results_by_state(state):
    url = f'https://www.cnn.com/election/2020/results/state/{state.lower().replace(" ", "-")}/house/'
    html = requests.get(url).text.encode()
    soup = BeautifulSoup(html, 'html.parser')
    race_json_str = str(soup.find('script', {'id': '__NEXT_DATA__'}))[51:-9]
    races = json.loads(race_json_str)['props']['pageProps']['districtRaces']
    df = pd.concat([_create_df_from_records(races[i]['candidates'], i+1) for i in range(len(races))]).reset_index(drop = True)
    df['state'] = state
    subset = df[['fullName', 'candidatePartyCode', 'voteNum', 'state', 'district']]
    return subset


def scrape_cnn(states):
    """Given a list of states scrape CNN for results of congressional elections."""
    # assumes that non-states are not included (e.g. no DC)
    res = pd.concat([_create_2020_results_by_state(x) for x in states])
    res = res.rename(columns = {'fullName': 'candidate', 'candidatePartyCode': 'party', 'voteNum': 'candidatevotes'})
    res['year'] = 2020
    res['stage'] = 'gen'
    
    return (
        res[[
            'year', 'state', 'district', 'candidate', 
            'party', 'candidatevotes', 'stage'
        ]]
    )
   