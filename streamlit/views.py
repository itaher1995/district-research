"""Code to create views that are used as input to streamlit for visualizations.
    Views Needed:
        * Historical vote by district -- district research code
        * Map by district -- district research code
        * House results by district -- district research code
        * Senate results statewide -- district research code
        * Presidential results statewide -- district research code
            * need to pull
"""
import pandas as pd
import numpy as np
import geopandas as gpd
import streamlit as st

from district_research.data.elections import get_general_election_results

def _create_house_2020_view():

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


def read_general_election_df(election_type):

    if election_type == 'house':
        df = _create_house_2020_view()
    elif election_type == 'senate':
        df = (
            pd.read_csv('data/1976-2020-senate.csv')
            .rename(columns={'party_detailed': 'party'})
        )
    else:
        df = (
            pd.read_csv('data/1976-2020-president.csv')
            .rename(columns={'party_detailed': 'party'})
        )
    
    return df


def get_historical_turnout_table(df,state, district_num=None, voting_age_pop_ct=None):

    if district_num and district_num != 'SN':
        district = state + '-' + district_num
        res = get_general_election_results(df, 2008, 2020, district, True)

    else:
        res = get_general_election_results(df, 2008, 2020, state, False)
    vw = (
        res.pivot_table(index='year', columns='party', 
            values='candidatevotes', aggfunc=np.sum)
        .rename_axis(None, axis=1)
    )

    vw['TOTAL'] = vw.sum(axis=1)

    if voting_age_pop_ct:
        vw['VOTER TURNOUT PERCENTAGE'] = vw['TOTAL']/voting_age_pop_ct

    return vw


@st.cache(allow_output_mutation=True)
def make_map_table():

    indicator_df = pd.read_csv('data/acs-zcta5-cong-dist-indicators-2019.csv')
    indicator_df['ZCTA5'] = indicator_df['ZCTA5'].astype(str).str.pad(5, 'left', '0')

    shape_df = (
        gpd.read_file('data/tl_2019_us_zcta510/tl_2019_us_zcta510.shp')
        .rename(columns={'ZCTA5CE10': 'ZCTA5'})
    )
    return gpd.GeoDataFrame(indicator_df.merge(shape_df, how = 'left', on = 'ZCTA5'))
