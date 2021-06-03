"""Make an dataset of socioeconomic indicators sourced from the one year estimates
    the American Community Survey provides. This code is generally used to populate
    congressional district and state socioeconomic indicators.
"""
import argparse
import logging
import json

import pandas as pd
from district_research.data.acs import get_acs_data_table

def main(args):
    logging.basicConfig(level=logging.INFO)

    logging.info('Reading configs...')
    API_KEY = args['API_KEY']
    YEAR = args['YEAR']
    GEO = args['GEO'].replace('_', ' ')
    EST = args['EST']

    with open('conf/indicators.json', 'r') as f:
        indicators = json.load(f)
    logging.info('Reading in state codes...')
    state_codes = pd.read_csv('data/state_codes.txt', sep='|')
    state_codes['STATE'] = state_codes['STATE'].astype(str).str.pad(2, 'left', '0')
    logging.info(f'\tcount: {len(state_codes)}')

    logging.info(f'Getting indicator data for {GEO}s from ACS API')
    data = (
        get_acs_data_table(API_KEY, EST, YEAR, GEO, '*', *indicators)
        .rename(columns={'state':'STATE'})
        .merge(state_codes, how='left', on='STATE')
    )
    if GEO == 'congressional district':
        data['CD'] = (data['STUSAB'] 
            + '-' 
            + data['congressional district']
                .astype(str)
                .str.pad(2, 'left', '0')
                .replace('00','01')
        )
    
        data = data[~data['CD'].str.endswith('ZZ')][['CD', *indicators]]

    elif args['GEO'] == 'state':
        data = data[['STUSAB', *indicators]]

    logging.info(f'\tcount: {len(data)}')
    logging.info('Writing File...')
    data.to_csv(
        f'data/{EST}-{GEO.replace(" ", "-")}-indicators-2019.csv', 
        index=False
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--API_KEY', type=str, help='the Census API Key')
    parser.add_argument('--EST', type=str, help='Type of acs estimate (acs5 or acs1)')
    parser.add_argument('--YEAR', type=str, help='year to collect data for')
    parser.add_argument('--GEO', type=str, help='geography to collect data for')
    args = vars(parser.parse_args())

    main(args)
