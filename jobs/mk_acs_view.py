"""Make an dataset of socioeconomic indicators sourced from the one year estimates
    the American Community Survey provides. This code is generally used to populate
    congressional district and state socioeconomic indicators.
"""
import argparse
import logging
import yaml

import pandas as pd
from district_research.data.acs import get_acs_data_table

def main(args):
    logging.basicConfig(level=logging.INFO)

    logging.info('Reading configs...')
    API_KEY = args['API_KEY']
    START_YEAR = args['START_YEAR']
    END_YEAR = args['END_YEAR']
    GEO = args['GEO'].replace('_', ' ')
    EST = args['EST']

    with open('conf/indicators.yml', 'r') as f:
        indicators = yaml.safe_load(f)
    logging.info('Reading in state codes...')
    state_codes = pd.read_csv('data/state_codes.txt', sep='|')
    state_codes['STATE'] = state_codes['STATE'].astype(str).str.pad(2, 'left', '0')
    logging.info(f'\tcount: {len(state_codes)}')

    logging.info(f'Getting indicator data for {GEO}s from ACS API from {START_YEAR} to {END_YEAR}')

    data = pd.concat([(
        get_acs_data_table(API_KEY, EST, str(y), GEO, '*', *indicators['current'])
        .rename(columns={'state':'STATE'})
        .rename(columns=indicators['current'])
        .rename(columns={
            '{}A'.format(k): '{} Error Code'.format(v) for k,v in indicators['current'].items()
        })
        .merge(state_codes, how='left', on='STATE')
    ) if y>=2017 else
    (
        get_acs_data_table(API_KEY, EST, str(y), GEO, '*', *indicators['past'])
        .rename(columns={'state':'STATE'})
        .rename(columns=indicators['past'])
        .rename(columns={
            '{}A'.format(k): '{} Error Code'.format(v) for k,v in indicators['past'].items()
        })
        .merge(state_codes, how='left', on='STATE')
    ) for y in range(START_YEAR, END_YEAR+1)]).reset_index(drop=True)

    if GEO == 'congressional district':
        data['CD'] = (data['STUSAB'] 
            + '-' 
            + data['congressional district']
                .astype(str)
                .str.pad(2, 'left', '0')
                .replace('00','01')
        )
    
        data = data[~data['CD'].str.endswith('ZZ')][['CD', 'YEAR', *indicators['current'].values()]]

    elif args['GEO'] == 'state':
        data = data[['STUSAB', 'YEAR', *indicators['current'].values()]]

    logging.info(f'\tcount: {len(data)}')
    logging.info('Writing File...')
    data.to_csv(
        f'data/{EST}-{GEO.replace(" ", "-")}-indicators-{START_YEAR}-{END_YEAR}.csv', 
        index=False
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--API_KEY', type=str, help='the Census API Key')
    parser.add_argument('--EST', type=str, help='Type of acs estimate (acs5 or acs1)')
    parser.add_argument('--START_YEAR', type=int, help='first year to collect data for')
    parser.add_argument('--END_YEAR', type=int, help='last year to collect data for')
    parser.add_argument('--GEO', type=str, help='geography to collect data for')
    args = vars(parser.parse_args())

    main(args)
