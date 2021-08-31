"""Main script to launch streamlit dashboard for district demographic data"""
import json

import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import yaml

from district_research.viz import plot_district_characteristic
from district_research.data.pvi import clean_pvi, clean_pvi_2020
from district_research.data.elections import clean_daily_kos2020

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
    pres_cd_df = clean_daily_kos2020(pd.read_csv(
        'data/Daily Kos Elections 2012, 2016 & 2020 presidential election results for congressional districts used in 2020 elections - Results.csv',
        header=1
        ))

    pvi_2017 = pd.read_csv('data/pvi.csv')
    pvi_2017['Dist'] = pvi_2017['Dist'].str.replace('-AL', '-01')
    pvi_2017['pvi_pct'] = clean_pvi(pvi_2017['PVI'], True)

    state_codes = pd.read_csv('data/state_codes.txt', sep='|')
    pvi_2020 = pd.read_csv('data/tabula-2021 PVI By District.csv', header=None)
    pvi_2020 = clean_pvi_2020(pvi_2020, state_codes)

    states_list = np.unique(house_df['state_po'].values).tolist()
    map_df = vw.make_map_table()

    with open('conf/indicators.yml', 'r') as f:
        indicators = yaml.safe_load(f)
    indicators_rev = {v: k for k,v in indicators['current'].items()}

    cd_df = (
        pd.read_csv('data/acs1-congressional-district-indicators-2012-2019.csv')
    )
    state_df = (
        pd.read_csv('data/acs1-state-indicators-2012-2019.csv')
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
        .tolist() + ['SN']
    )

    district_num = st.sidebar.selectbox('Select District', district_list)
    CD = f'{state}-{district_num}'

    ind = st.sidebar.selectbox('Plot Census Indicator', list(indicators['current'].values()))

    # to center title
    c1 = st.beta_container()
    t1, t2, t3 = c1.beta_columns([3, 10, 1])
    t1.write('')
    t2.title(f'District Research for {CD}')
    t3.write('')

    if district_num != 'SN':
        center_obj(
            vw.get_historical_turnout_plot(
                house_df,  
                state, 
                district_num
            ), 'Historical District-Level House General Election Results* (Counts)'
        )

        center_obj(
            vw.get_presidential_df_historical_pct_plot(pres_cd_df, CD),
            f'Historical District-Level Presidential General Election Results (Percentages)'
        )

        center_obj(
            vw.get_indicator_plot(cd_df, ind, state, district_num),
            f'{ind} Over Time for {state}-{district_num}'
        )
    else:
        center_obj(
            vw.get_historical_turnout_plot(
                senate_df,  
                state, 
                district_num
            ), 'Historical Senate General Election Results*'
        )

        center_obj(
            vw.get_indicator_plot(state_df, ind, state),
            f'{ind} Over Time for {state}'
        )

    if district_num != 'SN':
        ind_df = cd_df[(cd_df['CD'] == CD) & (cd_df['YEAR'] == 2019)][list(indicators['current'].values())].T
    else:
        ind_df = state_df[(state_df['STUSAB'] == state) & (state_df['YEAR'] == 2019)][list(indicators['current'].values())].T

    ind_df.columns = ['Indicator Values']
    center_obj(ind_df, f'{CD} Indicators')

    # TODO(itaher): Implement PVI stats for Senate
    if district_num != 'SN':
        c2 = st.beta_container()
        p1, p2, p3 = c2.beta_columns([3, 10, 1])
        p2.markdown(vw.get_pvi_sentence(pvi_2020, CD, 2021))

        c4 = st.beta_container()
        p41, p42, p43 = c2.beta_columns([3, 10, 1])
        p42.markdown(vw.get_pvi_sentence(pvi_2017, CD, 2017))
    
    c3 = st.beta_container()
    p31, p32, p33 = c3.beta_columns([3, 10, 1])

    if district_num == 'SN':
        p32.markdown(vw.get_diversity_index(state_df, 'STUSAB', state))
    else:
        p32.markdown(vw.get_diversity_index(cd_df, 'CD', CD))

    voting_age_pop_state_ct = state_df[(state_df['STUSAB'] == state) & (state_df['YEAR'] == 2019)]['Voting Age Population (Citizens)'].values[0]

    if district_num != 'SN':
        voting_age_pop_cd_ct = cd_df[(cd_df['CD'] == CD) & (cd_df['YEAR'] == 2019)]['Voting Age Population (Citizens)'].values[0]
        house_tbl = vw.get_historical_turnout_table(
            house_df, state, district_num, voting_age_pop_cd_ct
        )
        center_obj(house_tbl, 'House (District)*')

    senate_tbl = vw.get_historical_turnout_table(senate_df, state, None, voting_age_pop_state_ct)
    president_tbl = vw.get_historical_turnout_table(president_df, state, None, voting_age_pop_state_ct)
    center_obj(senate_tbl, 'Senate (Statewide)')
    center_obj(president_tbl, 'President (Statewide)')


    # empty line to separate election data from maps
    st.text("")
    # center map
    map_con = st.beta_container()
    em_map1, map2, em_map3 = map_con.beta_columns([1, 6, 1])

    fig = plot_district_characteristic(
        map_df, f'{state}-{district_num}', ind
    )
    
    em_map1.write('')
    map2.pyplot(fig)
    em_map3.write('')

    st.markdown("***")
    st.subheader('Notes:')
    st.write('\* You may see a column that looks like Democrat/Republican (x), where x is a number. This will happen in states like California, where its possible to see two candidates of the same party in the general election. It may also happen in states where two Senate seats are being contested. In those situations Democrat and Democrat (2) represent the leading Democrats in their respective races. In Senate races like this, Other is assumed to be total votes for all non-major candidates from both races. Thus, in this case it is possible for Other to have more votes than a major party candidate. This is also possible when the incumbent Senator is an independent (e.g. Bernie Sanders).')
    
    st.subheader('References')
    st.markdown('1. "Data." *[MIT Election Data + Science Lab](https://electionlab.mit.edu/data)*')
    st.markdown('2. "2020 House Election Results & Map." *[USA Today](https://www.usatoday.com/elections/results/2020-11-03/us-house/)*')
    st.markdown('3. "House Election Results 2020." *[CNN](https://www.cnn.com/election/2020/results/house)*')
    st.markdown('4. "Daily Kos Elections\' presidential results by congressional district for 2020, 2016, and 2012." *[Daily Kos](https://www.dailykos.com/stories/2020/11/19/1163009/-Daily-Kos-Elections-presidential-results-by-congressional-district-for-2020-2016-and-2012)*')
    st.markdown('4. "American Community Survey 1 Year Data, 2019." *[Census](https://www.census.gov/data/developers/data-sets/acs-1year.2019.html)*')
    st.markdown('5. "American Community Survey 5 Year Data, 2019." *[Census](https://www.census.gov/data/developers/data-sets/acs-5year.2019.html)*')
    st.markdown('6. "TIGER/Line Shapefiles, 2019." *[Census](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)*')
    st.markdown('7. "Geographic Corresponence Engine." *[Missouri Census Data Center](https://mcdc.missouri.edu/applications/geocorr2018.html)*')

if __name__ == '__main__':
    main()