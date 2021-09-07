"""IL-16 Data Request

Counties in IL-16 and IL-16
-Age
-Race
-Income distribution
-Turnout by party in the last 5 congressional elections (primary and general)
    - download and put in il-16

put outputs in il-16 folder
"""
import os

import pandas as pd
import numpy as np

from district_research.data.acs import get_acs_data_table
from district_research.data.elections import get_general_election_results

def create_il16_primary_county_results():

    files = [os.path.join('adhoc-data/il-16', f) for f in os.listdir('adhoc-data/il-16') if 'GP' in f and 'Cty' in f]
    dfs = [pd.read_excel(f) for f in files]
    dfs = [df[df['OfficeName'] == '16TH CONGRESS'][['Election', 'CanFirstName', 'CanLastName', 'PartyName', 'County', 'Votes']] for df in dfs]
    county_df = pd.concat(dfs).reset_index(drop=True)
    county_df['CandidateName'] = county_df['CanFirstName'] + ' ' + county_df['CanLastName']
    p2018 = pd.read_csv('adhoc-data/il-16/53-400-16TH CONGRESS-2018GP.csv')
    p2018 = p2018.groupby(['CandidateName', 'PartyName', 'JurisName']).sum()['VoteCount'].reset_index()
    p2018 = p2018[~p2018['CandidateName'].isin(['Blank Ballots', 'Over Votes', 'Under Votes'])]
    p2018['Election'] = 'GP 2018'
    p2018 = p2018.rename(columns={'JurisName': 'County', 'VoteCount': 'Votes'})
    cols = ['Election', 'CandidateName', 'PartyName', 'County', 'Votes']
    county_df = pd.concat([county_df[cols], p2018[cols]])
    county_df['Year'] = county_df['Election'].str.split(' ').str.slice(start=1).str.join('').astype(int)
    return county_df.drop('Election', axis=1)


def create_il16_general_county_results():

    files = [os.path.join('adhoc-data/il-16', f) for f in os.listdir('adhoc-data/il-16') if 'GE' in f and 'Cty' in f]
    dfs = [pd.read_excel(f) for f in files]
    dfs = [df[df['OfficeName'] == '16TH CONGRESS'][['Election', 'CanFirstName', 'CanLastName', 'PartyName', 'County', 'Votes']] for df in dfs]
    county_df = pd.concat(dfs).reset_index(drop=True)
    county_df['CandidateName'] = county_df['CanFirstName'] + ' ' + county_df['CanLastName']
    cols = ['Election', 'CandidateName', 'PartyName', 'County', 'Votes']
    county_df = county_df[cols]
    county_df['Year'] = county_df['Election'].str.split(' ').str.slice(start=1).str.join('').astype(int)
    return county_df.drop('Election', axis=1)


def create_il16_primary_results():
    files = [os.path.join('adhoc-data/il-16', f) for f in os.listdir('adhoc-data/il-16') if 'GP' in f and 'Tot' in f]
    dfs = [pd.read_excel(f) for f in files]
    dfs = [df[df['OfficeName'] == '16TH CONGRESS'][['Election', 'CanFirstName', 'CanLastName', 'PartyName', 'Votes']] for df in dfs]
    county_df = pd.concat(dfs).reset_index(drop=True)
    county_df['CandidateName'] = county_df['CanFirstName'] + ' ' + county_df['CanLastName']
    cols = ['Election', 'CandidateName', 'PartyName', 'Votes']
    county_df = county_df[cols]
    county_df['Year'] = county_df['Election'].str.split(' ').str.slice(start=1).str.join('').astype(int)
    return county_df.drop('Election', axis=1)


def _create_house_view():
    """Creates the house view that'll be used to plot general election results."""
    df = (
        pd.read_csv('data/1976-2018-house3.csv')
        [['year', 'state_po', 'district', 'party', 'candidatevotes', 'stage']]
    )
    df2020 = (
        pd.read_csv('data/2020-house-full.csv')
        [['year', 'state_po', 'district', 'party', 'candidatevotes', 'stage']]
    )

    final_df = pd.concat([df, df2020], axis=0)

    final_df['district'] = (
        final_df['district']
        .replace(0, 1)
        .astype(str)
        .str.pad(2, 'left', '0')
    )

    return final_df


def main():

    # get desired indicators in dict format
    # pull for all cd filter to il-16
    # pull for all counties filter to counties in il-16
    with open('conf/censuskey.txt', 'r') as f:
        api_key = f.read()
    
    state_codes = pd.read_csv('data/state_codes.txt', sep='|')
    state_codes['STATE'] = state_codes['STATE'].astype(str).str.pad(2, 'left', '0')

    indicators = {
        "DP05_0033E": "Total Population",
        "DP05_0087E": "Voting Age Population (Citizens)",
        "DP05_0078PE": "Percent Black",
        "DP05_0077PE": "Percent White",
        "DP05_0071PE": "Percent Latino",
        "DP05_0080PE": "Percent Asian",
        "DP05_0081PE": "Percent Native Hawaiian and Other Pacific Islander",
        "DP05_0079PE": "Percent American Indian and Alaska Native",
        "DP05_0018E": "Median Age",
        "DP03_0052PE": "$10,000 or less",
        "DP03_0053PE": "$10,000 to $14,999",
        "DP03_0054PE": "$15,000 to $24,999",
        "DP03_0055PE": "$25,000 to $34,999",
        "DP03_0056PE": "$35,000 to $49,999",
        "DP03_0057PE": "$50,000 to $74,999",
        "DP03_0058PE": "$75,000 to $99,999",
        "DP03_0059PE": "$100,000 to $149,999",
        "DP03_0060PE": "$150,000 to $199,999",
        "DP03_0061PE": "Over $200,000"
    }

    # County level work
    il16_counties = (
        pd.DataFrame.from_dict({
            '007': 'Boone',
            '011': 'Bureau',
            '063': 'Grundy',
            '075': 'Iroquois',
            '099': 'La Salle',
            '103': 'Lee',
            '105': 'Livingston',
            '141': 'Ogle',
            '155': 'Putnam',
            '037': 'DeKalb',
            '053': 'Ford',
            '175': 'Stark',
            '197': 'Will',
            '201': 'Winnebago'
        }, orient='index').reset_index()
        .rename(columns={0:'county_name', 'index': 'county'})
    )

    # used acs5 because acs1 had limited coverage of counties
    # county indicators
    county_df = (
        get_acs_data_table(api_key, 'acs5', 2019, 'COUNTY', '*', *indicators)
        .rename(columns={'state':'STATE'})
        .merge(state_codes, how='left', on='STATE')
        .drop([c+'A' for c in indicators], axis=1)
        .rename(columns=indicators)
    )
    illinois_county_df = (
        county_df[county_df['STUSAB'] == 'IL']
        .merge(il16_counties, how='inner', on='county')
        [['county_name'] + list(indicators.values())]
    )

    # county race results
    county_primary_res = create_il16_primary_county_results()
    county_gen_res = create_il16_general_county_results()
    
    
    # Congressional District level work
    
    # indicators acs1
    cd_df = (
        get_acs_data_table(
            api_key,
            'acs1',
            2019,
            'congressional district',
            '*',
            *indicators)
        .rename(columns={'state':'STATE'})
        .merge(state_codes, how='left', on='STATE')
        .drop([c+'A' for c in indicators], axis=1)
        .rename(columns=indicators)
    )
    il_16_series = cd_df[
        (cd_df['STUSAB'] == 'IL') 
        & (cd_df['congressional district'] == '16')
    ][indicators.values()].T

    # election results -- general
    house_df = _create_house_view()
    il_16_cong_elections = (house_df[
        (house_df['state_po'] == 'IL')
        & (house_df['district'] == '16')
        & (house_df['year'] >= 2010)
    ])

    # election results -- primary
    il_16_primary = create_il16_primary_results()

    # save data
    il_16_primary.to_csv('adhoc-data/il-16-outputs/il16_primary_results.csv', index=False)
    il_16_cong_elections.to_csv('adhoc-data/il-16-outputs/il16_general_results.csv', index=False)
    il_16_series.to_csv('adhoc-data/il-16-outputs/il16_census_indicators.csv', index=False)
    illinois_county_df.to_csv('adhoc-data/il-16-outputs/il16_county_census_indicators.csv', index=False)
    county_primary_res.to_csv('adhoc-data/il-16-outputs/il16_county_primary_results.csv', index=False)
    county_gen_res.to_csv('adhoc-data/il-16-outputs/il16_county_general_results.csv', index=False)


if __name__ == '__main__':
    main()