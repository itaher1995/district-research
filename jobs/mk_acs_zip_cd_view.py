
"""This script combines several sources to create a view that contains a ZCTA,
    congressional district, several socioeconomic indicators and associated ZCTA 
    geometries. These indicators can either be plotted on a map or saved to be
    used in separate analysis.
"""
import argparse
import logging
import json

import pandas as pd
import geopandas as gpd

from district_research.data.acs import get_acs_data_table
from district_research.viz import plot_district_characteristic

def main(args):
    logging.basicConfig(level=logging.INFO)

    logging.info('Reading configs...')
    API_KEY = args['API_KEY']
    YEAR = args['YEAR']
    EST = args['EST']

    with open('conf/districts.txt', 'r') as f:
        districts = f.readlines()
        districts = [x.replace('\n','').strip() for x in districts]
    with open('conf/indicators.json', 'r') as f:
        indicators = json.load(f)

    logging.info('Reading zip code shape files...')
    shape_df = (
        gpd.read_file(f'data/tl_{YEAR}_us_zcta510/tl_{YEAR}_us_zcta510.shp')
        .rename(columns={'ZCTA5CE10': 'ZCTA5'})
    )
    logging.info(f'\tcount: {len(shape_df)}')

    logging.info('Creating ztca to congressional district path')
    ztca_cd_df = (
        pd.read_csv('data/geocorr2018.csv', header=1)
        .rename(columns={
            'ZIP census tabulation area': 'ZCTA5', 
            'State abbreviation': 'STUSAB', 
            '116th Congressional district': 'district'
        })
    )

    ztca_cd_df['CD'] = (
        ztca_cd_df['STUSAB'].str.pad(3, 'right', '-') 
        + ztca_cd_df['district'].astype(str).str.pad(2, 'left', '0').replace('00', '01')
    )

    ztca_cd_df['ZCTA5'] = ztca_cd_df['ZCTA5'].astype(str).str.pad(5, 'left', '0')

    logging.info('Getting indicator data for ZCTAs from ACS API')
    vars_to_plot = get_acs_data_table(
        API_KEY, EST, YEAR, 'zip code tabulation area', '*', *indicators
    ).rename(columns = {'zip code tabulation area': 'ZCTA5'})
    logging.info(f'\tcount: {len(vars_to_plot)}')

    logging.info('Merging dataframes to create final output...')
    df = gpd.GeoDataFrame(
        ztca_cd_df
        .merge(shape_df, how='left', on='ZCTA5')
        .merge(vars_to_plot, how='left', on='ZCTA5')
        [['ZCTA5', 'CD', 'geometry', *indicators] + [x+'A' for x in indicators]]
    )
    logging.info(f'\tcount: {len(df)}')
    logging.info(f'\tnull rate:\n\t\t{pd.isnull(df).sum()/len(df)}')
    if args['SAVE_MAPS']:
        for d in districts:
            logging.info(f'Making maps for {d}...')
            for i in indicators:
                plot_district_characteristic(
                    df, d, i,
                    title=f'{indicators[i]} ({d})', save_dir=f'outputs/{d}'
                )
    else:
        logging.info('Saving dataset without geometry...')

        # renaming columns to ensure that column names are not overwritten
        (        
            pd.DataFrame(df.drop('geometry', axis=1))
            .to_csv(f'data/acs-zcta5-cong-dist-indicators-{YEAR}.csv')
        )

    logging.info('Done')
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--API_KEY', type=str, help='the Census API Key')
    parser.add_argument('--EST', type=str, help='Year estimate')
    parser.add_argument('--YEAR', type=str, help='year to collect data for')
    parser.add_argument('--PLOT_MAPS', dest='SAVE_MAPS', action='store_true',
        help="""Plots characteristics at zip code level for congressional 
            districts using shapefiles""")
    parser.add_argument('--SAVE_VIEW', dest='SAVE_MAPS', action='store_false',
        help="""Saves dataset created from this script.""")
    parser.set_defaults(SAVE_MAPS=True)
    args = vars(parser.parse_args())

    main(args)