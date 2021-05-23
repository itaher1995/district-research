import json

import streamlit as st
import numpy as np
import pandas as pd

from district_research.viz import plot_district_characteristic

import views as vw

def main():

    # read in data
    house_df = vw.read_general_election_df('house')
    senate_df = vw.read_general_election_df('senate')
    president_df = vw.read_general_election_df('president')
    states_list = np.unique(house_df['state_po'].values).tolist()
    map_df = vw.make_map_table()

    with open('conf/indicators.json', 'r') as f:
        indicators = json.load(f)
    indicators_rev = {v: k for k,v in indicators.items()}

    cd_df = (
        pd.read_csv('data/acs1-congressional-district-indicators-2019.csv')
        .rename(columns=indicators)
    )
    state_df = (
        pd.read_csv('data/acs1-state-indicators-2019.csv')
        .rename(columns=indicators)
    )
    
    state = st.sidebar.selectbox('Select State', states_list)

    district_list = (
        np.unique(house_df[house_df['state_po'] == state]['district'].values)
        .tolist() 
    )

    district_num = st.sidebar.selectbox('Select District', district_list)
    CD = f'{state}-{district_num}'
    st.title(f'District Research for {CD}')

    st.subheader('Historical District General Election Results')
    st.line_chart(vw.get_historical_turnout_table(house_df, state, district_num).drop('TOTAL', axis = 1))

    st.subheader('Congressional District Indicators')
    st.write(cd_df[cd_df['CD'] == CD][list(indicators.values())].T)

    # Need to match necessary formats
    st.subheader('House (District)')
    voting_age_pop_cd_ct = cd_df[cd_df['CD'] == CD]['Voting Age Population (Citizens)'].values[0]
    st.write(vw.get_historical_turnout_table(house_df, state, district_num, voting_age_pop_cd_ct))

    st.subheader('Senate (Statewide)')
    voting_age_pop_state_ct = state_df[state_df['STUSAB'] == state]['Voting Age Population (Citizens)'].values[0]
    st.write(vw.get_historical_turnout_table(senate_df, state, None, voting_age_pop_state_ct))

    st.subheader('President (Statewide)')
    st.write(vw.get_historical_turnout_table(president_df, state, None, voting_age_pop_state_ct))

    plot_maps = st.sidebar.selectbox('Plot Census Maps', [False, True])
    if plot_maps and district_num != 'SN':
        ind = st.selectbox('Select Indicator to Plot', list(indicators_rev.keys()))
        st.subheader(ind)
        fig = plot_district_characteristic(map_df, f'{state}-{district_num}', 
            indicators_rev[ind])
        st.pyplot(fig)



if __name__ == '__main__':
	main()