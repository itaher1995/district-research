"""Calculates Cook PVI for the elections we have data for starting from 2008.
    As of now this ends at 2020. 

    How is PVI defined? The inputs are:

    * Winner of Election in District: (R or D)
    * Average of this year's results and last year's result in district for that
        party
    * Average of this year's results and last year's results in country for that
        party
    
    Then we subtract the district's average from the national average and use the
    party winner to determine the next transformation. If its a democrat, then
    we inverse the result and if its a republican we keep it the same. We do this
    because we want more democratic districts to be negative (left on number scale)
    and more republican districts to be positive (right on number scale.)

    Note the values for congressional district results seem to be slightly off,
    However, we see that the scores are highly correlated, which means that any
    discrepancies come from the input data itself and not our calculation. Also,
    our results are good enough for analysis purposes.
"""
import pandas as pd
import numpy as np

from district_research.data.elections import get_general_election_results
from district_research.data.pvi import clean_cook_pvi

def calculate_pvi(pvi_df, pres_share_df):
    """Calculates Partisan Voter Index as Cook Political Report defines it."""

    # take df and go from a wide df (e.g. district, D_2018, R_2018, D_2016, R_2016 ...)
    # to long df (district, party_year, share). We do this for easy filtering to find
    # winner of district and their shares, an input to PVI.
    pvi_unpivot = pvi_df.melt(id_vars = 'CD', var_name='party_year', value_name='cur_share').reset_index(drop=True)
    pvi_unpivot[['party', 'year']] = pvi_unpivot['party_year'].str.split('_', expand=True)
    pvi_unpivot = pvi_unpivot.drop('party_year', axis=1)
    pvi_unpivot['year'] = pvi_unpivot['year'].astype(int)

    # calculate rank to identify winner. We do this as opposed to finding the
    # candidate with the majority share because its possible that no candidate
    # got higher than 50% of the vote in that district.
    pvi_unpivot['rank'] = (
        pvi_unpivot
        .sort_values('cur_share', ascending = False)
        .groupby(['CD', 'year'])
        .cumcount() + 1
    )

    pvi_winner = pvi_unpivot[pvi_unpivot['rank'] == 1].drop('rank', axis=1)

    pvi_winner['last'] = pvi_winner['year'] - 4
    
    # merge dataframes to get current and historical results for current year 
    # winning party and the accompanying national average. 
    pvi_winner = pvi_winner.merge(
        pvi_unpivot
        .rename(columns={'year': 'last', 'cur_share': 'prev_share'})
        .drop('rank', axis = 1),
        how='inner', on=['CD', 'last', 'party']
    ).merge(
        pres_share_df[['year', 'party', 'nat_party_share']], 
        how='inner', on=['year', 'party']
    ).merge(
        pres_share_df[['year', 'party', 'nat_party_share']]
        .rename(columns={'nat_party_share': 'prev_nat_party_share', 'year': 'last'}), 
        how='inner', on=['last', 'party']
    )

    pvi_winner[['nat_party_share', 'prev_nat_party_share']] = pvi_winner[['nat_party_share', 'prev_nat_party_share']] * 100

    # calculation for PVI is below
    pvi_winner['district_avg'] = pvi_winner[['cur_share', 'prev_share']].mean(axis=1)
    pvi_winner['national_avg'] = pvi_winner[['nat_party_share', 'prev_nat_party_share']].mean(axis=1)
    pvi_winner['pvi_raw'] = pvi_winner['district_avg'] - pvi_winner['national_avg']

    pvi_winner['pvi'] = np.around(np.where(pvi_winner['party'] == 'D', pvi_winner['pvi_raw'] * -1, pvi_winner['pvi_raw']))

    return pvi_winner[['CD', 'year', 'pvi']]

def score_validation(calculated_pvi, cook_pvi, year):
    """Calculate the correlation between the pvi we calculate and the cook pvi.
        While our scores may not line up with cook's all the time, getting the
        validation can give us some confidence in using the scores from here
        on out.

        Validation includes:
            * Correlation of scores
            * Summary stats for difference of scores
    """

    calculated_pvi_sub = calculated_pvi[calculated_pvi['year'] == year]
    
    pvi = calculated_pvi_sub.merge(cook_pvi, how='left', on='CD')

    # difference in PVI
    print((pvi['pvi'] - pvi['Cook_PVI']).describe([0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]))
    print(pvi[['pvi', 'Cook_PVI']].corr())


def main():

    # step 1: read in presidential election results by congressional district from
    # daily kos. Clean and combine datasets. This is used to calculate each
    # congressional districts results for president
    pvi_df1 = pd.read_csv(
        'data/Daily Kos Elections 2012, 2016 & 2020 presidential election results for congressional districts used in 2020 elections - Results.csv',
        header=1    
    )
    pvi_df1 = pvi_df1.drop([*pvi_df1.columns[1:3], *pvi_df1.columns[-2:]], axis=1)
    print(pvi_df1.columns)
    pvi_df1.columns = ['CD', 'D_2020', 'R_2020', 'D_2016', 'R_2016', 'D_2012', 'R_2012']

    pvi_df2 = pd.read_csv('data/Daily Kos Elections 2008 & 2012 presidential election results for congressional districts used in 2012 & 2014 elections - Results.csv')
    pvi_df2.columns = ['CD', 'Incumbent', 'Party', 'D_2012', 'R_2012', 'D_2008', 'R_2008']
    pvi_df2 = pvi_df2.drop(['Incumbent', 'Party', 'D_2012', 'R_2012'], axis=1)

    pvi_df = pvi_df1.merge(pvi_df2, how='left', on='CD')
    pvi_df['CD'] = pvi_df['CD'].str.replace('-AL', '-01')

    # step 2: read in historical presidential results. This is used to calculate
    # national results. This is used for normalizing PVI and helping us to understand
    # how one district's results relate to national calculus. 
    pres = (
        pd.read_csv('data/1976-2020-president.csv')
        .rename(columns={'party_detailed': 'party'})
    )
    pres_sub = get_general_election_results(pres, 2008, 2020, '*', False)
    pres_sub_vote_ct = pres_sub.groupby(['year', 'party']).sum()['candidatevotes'].reset_index()
    pres_sub_vote_ct = pres_sub_vote_ct[pres_sub_vote_ct['party'].isin(['DEMOCRAT', 'REPUBLICAN'])]
    pres_sub_vote_ct['totalvotes'] = pres_sub_vote_ct.groupby('year').transform('sum')['candidatevotes']
    pres_sub_vote_ct['nat_party_share'] = pres_sub_vote_ct['candidatevotes']/pres_sub_vote_ct['totalvotes']
    pres_sub_vote_ct['party'] = pres_sub_vote_ct['party'].str.slice(stop=1)

    # step 3: calculate PVI
    # TODO(itaher): rectify small differences between cook and our calculation
    historical_pvi = calculate_pvi(pvi_df, pres_sub_vote_ct)

    # step 4: validation
    cook_pvi_df = pd.read_csv('data/pvi.csv')
    cook_pvi_df['Dist'] = cook_pvi_df['Dist'].str.replace('-AL', '-01')
    cook_pvi_df['Cook_PVI'] = clean_cook_pvi(cook_pvi_df['PVI'], False)
    cook_pvi_df = cook_pvi_df.rename(columns={'Dist':'CD'})

    print(score_validation(historical_pvi, cook_pvi_df[['CD', 'Cook_PVI']], 2016))

if __name__ == '__main__':
    main()