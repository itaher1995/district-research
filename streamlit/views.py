"""Code to create views that are used as input to streamlit for visualizations.
    TODO(itaher): Add documentation
"""
import pandas as pd
import numpy as np
import geopandas as gpd
import streamlit as st
import plotly.graph_objects as go

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


def get_historical_turnout_table(df, state, district_num=None, voting_age_pop_ct=None):

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

def get_historical_turnout_plot(df, state, district_num=None, voting_age_pop_ct=None):
    
    subset = get_historical_turnout_table(df, state, district_num, voting_age_pop_ct)
    subset = subset.drop('TOTAL', axis=1).reset_index()
    subset_pivot = subset.melt(id_vars='year', var_name='PARTY', value_name='VOTES')

    fig = go.Figure()

    for p in subset_pivot['PARTY'].unique():
        party_sub = subset_pivot[subset_pivot['PARTY'] == p]
        fig.add_trace(go.Scatter(x=party_sub['year'], y=party_sub['VOTES'], mode='lines+markers', name=p))
    
    fig.update_layout(
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis_title='YEAR', 
        yaxis_title='Number of Votes'
    )
    return fig


def get_pvi_sentence(df, district):
    d = df[df['Dist'] == district]
    pct = np.round(d['pvi_pct'].values[0] * 100, 2)

    if pct > 50:
        substr = f'bottom {100 - pct}%'
    else:
        substr = f'top {pct}%'

    return f'This district\'s PVI is **{d["PVI"].values[0]}**. That\'s in the **{substr}** most Democratic districts. Ideally this should be **at least D+16**.'



@st.cache(allow_output_mutation=True)
def make_map_table():

    indicator_df = pd.read_csv('data/acs-zcta5-cong-dist-indicators-2019.csv')
    indicator_df['ZCTA5'] = indicator_df['ZCTA5'].astype(str).str.pad(5, 'left', '0')

    shape_df = (
        gpd.read_file('data/tl_2019_us_zcta510/tl_2019_us_zcta510.shp')
        .rename(columns={'ZCTA5CE10': 'ZCTA5'})
    )
    return gpd.GeoDataFrame(indicator_df.merge(shape_df, how = 'left', on = 'ZCTA5'))
