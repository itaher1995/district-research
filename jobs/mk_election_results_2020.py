"""Functions to scrape data to get 2020 general election results for the House
of Representatives. There are two source: CNN and USA Today. We need both
because USA Today is more comprehensive on a race by race basis, but races where
the candidate ran unopposed don't have much data on the website. Therefore we
fill in the blanks with CNN."""

import logging

import pandas as pd
import numpy as np

from district_research.data.election_scrape import scrape_usa_today, scrape_cnn

def main():
    """Parses USA Today website to gather 2020 house general election results.
        Joins to CNN data to get full results."""
    logging.basicConfig(level=logging.INFO)

    logging.info('Reading in state codes data frame...')
    state_codes = (
        pd.read_csv('data/state_codes.txt', sep='|')
        .drop('STATE', axis=1)
        .rename({'STATE_NAME': 'state'}, axis=1)
    )

    # states is passed as input to scrape_cnn because that function iterates
    # over a list of state names to create the 2020 results.
    states = (
        state_codes
        [~state_codes['STUSAB'].isin(['DC', 'AS', 'GU', 'MP', 'PR', 'UM', 'VI'])]
        ['state'].values.tolist()
    )

    # primary source is usa today and the source we are using to fill in 
    # missing data is CNN
    logging.info('Grabbing election data from USA Today...')
    usa_today = scrape_usa_today()
    logging.info(f'\tcount: {len(usa_today)}')

    logging.info('Grabbing election data from CNN...')
    cnn = scrape_cnn(states)
    logging.info(f'\tcount: {len(cnn)}')


    logging.info('Identifying Data Errors...')

    # split to get data from other source,
    # process to merge two datasets together. Identify all improperly formatted
    # individuals and do a inner with politico data on last name and
    # first letter of party.
    properly_formatted = usa_today[~usa_today['state'].isna()]
    improperly_formatted = usa_today[usa_today['state'].isna()][['candidate', 'party']]
    logging.info(f'Fixing the following candidates: {", ".join(improperly_formatted["candidate"].values)}')

    # TODO(itaher): Fix this join
    corrected = (
        improperly_formatted
        .merge(cnn, how ='inner', on=['candidate', 'party'])
        [['year', 'state', 'district', 'party', 'candidate', 'candidatevotes', 'stage']]
    )

    logging.info('Creating and writing full corrected dataframe with state abbreviations...')
    final_df = (
        pd.concat([properly_formatted, corrected], axis=0)
        .merge(state_codes, how='inner', on='state')
        .rename(columns={'STUSAB': 'state_po', 'last_name': 'candidate'})
        [['year', 'state_po', 'district', 'party', 'candidate', 
        'candidatevotes', 'stage']]
    )
    final_df['party'] = (
        final_df['party']
        .replace('D', 'DEMOCRAT')
        .replace('R', 'REPUBLICAN')
    )

    final_df.to_csv('data/2020-house-full.csv', index = False)
    logging.info(f'{len(final_df)}')

if __name__ == '__main__':
    main()