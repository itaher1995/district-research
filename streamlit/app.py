import json

import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns

from district_research.viz import plot_district_characteristic
from district_research.data.pvi import clean_pvi

import views as vw

def center_obj(obj, title):
    container = st.beta_container()
    col1, col2, col3 = container.beta_columns([1, 4, 1])

    col1.write('')
    col2.subheader(title)
    col2.write(obj)
    col3.write('')

def main():
    st.set_page_config(layout='wide')
    # read in data
    house_df = vw.read_general_election_df('house')
    senate_df = vw.read_general_election_df('senate')
    president_df = vw.read_general_election_df('president')

    pvi_df = pd.read_csv('data/pvi.csv')
    pvi_df['Dist'] = pvi_df['Dist'].str.replace('-AL', '-01')
    pvi_df['pvi_pct'] = clean_pvi(pvi_df['PVI'], True)

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

    # some districts may have disappeared by 2020 because of redistricting that
    # happened because of the 2010 Census. Therefore we only look at districts
    # that were valid in 2010. TODO: make this flexible, based on previous
    # election year or something.
    district_list = (
        np.unique(
            house_df
            [(house_df['state_po'] == state) & (house_df['year'] == 2020)]
            ['district'].values
        )
        .tolist() 
    )

    district_num = st.sidebar.selectbox('Select District', district_list)
    CD = f'{state}-{district_num}'

    # to center title
    c1 = st.beta_container()
    t1, t2, t3 = c1.beta_columns([3, 10, 1])
    t1.write('')
    t2.title(f'District Research for {CD}')
    t3.write('')

    center_obj(
        vw.get_historical_turnout_plot(house_df, state, district_num),
        'Historical District General Election Results*'
    )

    cd_ind = cd_df[cd_df['CD'] == CD][list(indicators.values())].T
    cd_ind.columns = ['Indicator Values']
    center_obj(cd_ind, 'Congressional District Indicators')

    c2 = st.beta_container()
    p1, p2, p3 = c2.beta_columns([3, 10, 1])
    p2.markdown(vw.get_pvi_sentence(pvi_df, CD))

    voting_age_pop_cd_ct = cd_df[cd_df['CD'] == CD]['Voting Age Population (Citizens)'].values[0]
    voting_age_pop_state_ct = state_df[state_df['STUSAB'] == state]['Voting Age Population (Citizens)'].values[0]
    house_tbl = vw.get_historical_turnout_table(house_df, state, district_num, voting_age_pop_cd_ct)
    senate_tbl = vw.get_historical_turnout_table(senate_df, state, None, voting_age_pop_state_ct)
    president_tbl = vw.get_historical_turnout_table(president_df, state, None, voting_age_pop_state_ct)
    
    center_obj(house_tbl, 'House (District)*')
    center_obj(senate_tbl, 'Senate (Statewide)')
    center_obj(president_tbl, 'President (Statewide)')

    ind = st.sidebar.selectbox('Plot Census Indicator', list(indicators_rev.keys()))

    # empty line to separate election data from maps
    st.text("")
    # center map
    map_con = st.beta_container()
    em_map1, map2, em_map3 = map_con.beta_columns([1, 6, 1])

    fig = plot_district_characteristic(map_df, f'{state}-{district_num}', 
        indicators_rev[ind], ind)
    
    em_map1.write('')
    map2.pyplot(fig)
    em_map3.write('')

    st.markdown("***")
    st.subheader('Notes:')
    st.write('\* You may see a column that looks like Democrat/Republican (x), where x is a number. This will happen in states like California, where its possible to see two candidates of the same party in the general election.')
    
    st.subheader('References')
    st.markdown('1. "Data." *[MIT Election Data + Science Lab](https://electionlab.mit.edu/data)*')
    st.markdown('2. "American Community Survey 1 Year Data, 2019." *[Census](https://www.census.gov/data/developers/data-sets/acs-1year.2019.html)*')
    st.markdown('3. "American Community Survey 5 Year Data, 2019." *[Census](https://www.census.gov/data/developers/data-sets/acs-5year.2019.html)*')
    st.markdown('4. "TIGER/Line Shapefiles, 2019." *[Census](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)*')
    st.markdown('5. "Geographic Corresponence Engine." *[Missouri Census Data Center](https://mcdc.missouri.edu/applications/geocorr2018.html)*')

if __name__ == '__main__':
    main()