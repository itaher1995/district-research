"""Code to create views that are used as input to streamlit for visualizations.
    TODO(itaher): Determine what code belongs in views.py and what should be
    moved back into district_research
"""
import pandas as pd
import numpy as np
import geopandas as gpd
import streamlit as st
import plotly.graph_objects as go

from district_research.data.elections import get_general_election_results

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


def read_general_election_df(election_type):
    """Depending on the race type, reads in a csv of general election results.
        If its the house, concats two datasets together to create up to date
        results.

        Args:
            election_type (str): A string denoting whether this is a 'house',
                'senate' or 'presidential' race.
        
        Returns:
            A DataFrame of historical general election results.
    """

    if election_type == 'house':
        df = _create_house_view()
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
    """Takes a dataframe of election results and gets the results of elections
        for a given race (e.g. MO-01, MO-SN or MO-Pres) between 2008 and 2020.
        Also provides voter turnout % where the denominator is the 2019 Citizen
        Voting Age Population.

        Args:
            df (Pandas DataFrame): DataFrame of election results
            state (str): The abbreviation of the state we are interested in
                getting results for
            district_num (str): The string that denotes the district number
                e.g. 01, 02, 10, 40, etc.
            voting_age_pop_ct (int): The number of citizens in a district that
                are at least 18.
        Returns:
            A DataFrame that has results for candidates of different parties
                between 2008 and 2020 in a given race.
    """

    if district_num and district_num != 'SN':
        district = state + '-' + district_num
        res = get_general_election_results(df, 2012, 2020, district, True)

    else:
        res = get_general_election_results(df, 2012, 2020, state, False)
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
    """Plots the historical turnout table returned from get_historical_turnout_table.

        Args:
            df (Pandas DataFrame): DataFrame of election results
            state (str): The abbreviation of the state we are interested in
                getting results for
            district_num (str): The string that denotes the district number
                e.g. 01, 02, 10, 40, etc.
            voting_age_pop_ct (int): The number of citizens in a district that
                are at least 18.
        Returns:
            A plotly figure, which is a line graph of historical general election
                results.
    """
    
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


def get_presidential_df_historical_pct_plot(df, district):
    """Plots the presidential election results in each congressional district.

        Arguments:
            df (Pandas DataFrame): DataFrame of percentages of votes for Democrats
            and Republicans between 2012 and 2020
            district (str): The district to plot these results for.
        
        Returns:
            A plotly fig that plots these results.
    """
    subset = df[df['CD'] == district]
    fig = go.Figure()
    for p in subset['PARTY'].unique():
        party_sub = subset[subset['PARTY'] == p]
        fig.add_trace(go.Scatter(x=party_sub['YEAR'], y=party_sub['PCT'], mode='lines+markers', name=p))

    fig.update_layout(
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis_title='Year', 
        yaxis_title='Percentage of Votes'
    )

    return fig        


def get_pvi_sentence(df, district, year):
    """Creates a sentence (str) that denotes what a district's PVI is, how 
        democratic is it relative to ALL OTHER DISTRICTS and a threshold. Uses
        a dataframe of PVI values and the district itself to identify these
        metrics.

        Args:
            df (Pandas DataFrame): DataFrame of PVI data.
            district (str): Name of the district to get PVI data for
        Returns:
            A string that states the PVI, its percentile relative to all other
            districts and the benchmark we'd like to achieve.
    """
    d = df[df['Dist'] == district]
    pct = np.round(d['pvi_pct'].values[0] * 100, 2)

    if pct > 50:
        substr = f'bottom {100 - pct}%'
    else:
        substr = f'top {pct}%'

    return f'This district\'s PVI ({year}) is **{d["PVI"].values[0]}**. That\'s in the **{substr}** most Democratic districts. Ideally this should be **at least D+24**.'


def get_indicator_plot(df, indicator, state, district_num=None):
    """Creates a bar plot for census indicators since 2017.
    
        Args:
            df (Pandas DataFrame): DataFrame at either state or congressional
            district level with ACS data.
            indicator (str): The indicator code from census.
            state (str): State abbreviation
            district_num (str): Two digit district representation (e.g. 01, 10)
        
        Returns:
            Plotly graphical object. Bar plot of indicator since 2017.
    """
    if district_num:
        district = state + '-' + district_num
        subset = df[df['CD'] == district]
    else:
        subset = df[df['STUSAB'] == state]

    fig = go.Figure()

    # TODO(itaher): Fix this to have x as categoricals not numerics when plotting
    fig.add_trace(go.Bar(x=subset['YEAR'].astype(str), y=subset[indicator]))
    fig.update_layout(
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis_title='YEAR', 
        yaxis_title=indicator
    )

    return fig


def get_diversity_index(df, geo, geo_val):
    """Shannon Entropy of Racial Demographics
        Args:
            df (Pandas DataFrame): DataFrame at some geography level with racial
            percentages
            geo (str): Geography level (e.g. state, cd, etc.)
            geo_val (str): Corresponding code to geo
        Returns:
            A string that talks about the racial diversity index.
    """

    subset = df[(df['YEAR'] == 2019)]

    # racial characteristics
    subset_race = subset[[
        'Percent Black',
        'Percent White',
        'Percent Asian',
        'Percent Latino',
        'Percent Native Hawaiian and Other Pacific Islander',
        'Percent American Indian and Alaska Native'
    ]]

    for c in subset_race.columns:
        subset_race[c] = subset_race[c]/100 * np.log(subset_race[c]/100)
    
    subset['racial_diversity'] = -subset_race.sum(axis=1)
    subset['racial_diversity_pct'] = subset['racial_diversity'].rank(pct=True)

    area_vals = subset[subset[geo] == geo_val][[geo, 'racial_diversity_pct', 'Percent White']]

    return f'{geo_val}\'s Racial Diversity Index is {np.round(area_vals["racial_diversity_pct"].values[0], 2)} on a scale of 0.00 to 1.00. It\'s Minority Percentage is {100 - area_vals["Percent White"].values[0]}%.'
    

@st.cache(allow_output_mutation=True)
def make_map_table():
    """Uses shape files and socioeconomic data from the acs five year estimates
        to associate ZCTAs, Congressional Districts and socioeconomic indicators.
    """
    indicator_df = pd.read_csv('data/acs-zcta5-cong-dist-indicators-2019.csv')
    indicator_df['ZCTA5'] = indicator_df['ZCTA5'].astype(str).str.pad(5, 'left', '0')

    shape_df = (
        gpd.read_file('data/tl_2019_us_zcta510/tl_2019_us_zcta510.shp')
        .rename(columns={'ZCTA5CE10': 'ZCTA5'})
    )
    return gpd.GeoDataFrame(indicator_df.merge(shape_df, how = 'left', on = 'ZCTA5'))
