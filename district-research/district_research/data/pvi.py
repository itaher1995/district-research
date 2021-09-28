"""Code to clean/work with 2017 PVI Data downloaded from the Cook Political Report"""

import numpy as np
import pandas as pd

def calculate_pvi(general_election_df, level_col):
    """Takes a dataframe of general election results from MIT and calculates
    PVI."""
    
    # step 1: clean data, make sure we have total counts for each county.
    # some results are broken up into early voting, election day, etc.
    count_df = (
        general_election_df
        [general_election_df['party'].isin(['DEMOCRAT', 'REPUBLICAN'])]
        .groupby(['year', level_col, 'candidate', 'party'])
        .sum()['candidatevotes']
        .reset_index()
    )

    # step 2: make number of votes into percentage
    count_df['total'] = (
        count_df
        .groupby(['year', level_col])
        .transform('sum')['candidatevotes']
    )
    count_df['candidatepct'] = count_df['candidatevotes']/count_df['total']

    # step 3: get percent at election-wide level per party
    count_df['total_election_per_party'] = (
        count_df
        .groupby(['year', 'party'])
        .transform('sum')['candidatevotes']
    )

    count_df['total_election'] = (
        count_df
        .groupby(['year'])
        .transform('sum')['candidatevotes']
    )

    count_df['electionpct'] = count_df['total_election_per_party']/count_df['total_election']
    
    # step 4: get the results for the party in question from the previous
    # election
    count_df['previous_year'] = count_df['year'] - 4
    count_df2 = (
        count_df
        .merge(count_df[
            ['year', 'party', level_col, 'candidatepct', 'electionpct']
        ].rename(
            columns={
                'year': 'previous_year',
                'candidatepct': 'previous_candidatepct',
                'electionpct': 'previous_electionpct'
            }),
        how='left', left_on=['previous_year', 'party', level_col],
        right_on=['previous_year', 'party', level_col])
    )

    # can't calcuate pvi for min year because we have no data from before then
    count_df2 = count_df2[count_df2['year'] > count_df['year'].min()]

    # step 5: choose winner for each county. Do this through pandas syntax
    # for window function.

    count_df2['rank'] = (
        count_df2
        .sort_values('candidatevotes', ascending = False)
        .groupby(['year', level_col])
        .cumcount() + 1
    )
    
    winners = count_df2[count_df2['rank'] == 1]
    
    # step 6: calculate pvi by getting average results of candidate from county
    # vs. average results from candidate from entire election.
    winners['county_avg'] = winners[['candidatepct', 'previous_candidatepct']].mean(axis=1)
    winners['national_avg'] = winners[['electionpct', 'previous_electionpct']].mean(axis=1)
    winners['diff_in_avgs'] = (winners['county_avg'] - winners['national_avg']) * 100
    winners['diff_in_avgs'] = winners['diff_in_avgs'].fillna(0)

    
    # When val is positive assign party as is. When val is negative flip party 
    # and make positive
    winners['party_initial'] = winners['party'].str.slice(stop=1)
    winners['other_party_initial'] = np.where(winners['party_initial'] == 'D', 'R', 'D')
    winners['pvi'] = np.where(
        winners['diff_in_avgs'] > 0,
        winners['party_initial'] + '+' + winners['diff_in_avgs'].astype(str),
        winners['other_party_initial'] + '+' + winners['diff_in_avgs'].abs().astype(str)
    )
    winners['pvi'] = winners['pvi'].str.split('.').str.slice(stop=1).str.join('')

    return winners[['year', level_col, 'candidate', 'party', 'pvi']]


def clean_cook_pvi_2020(pvi_df, state_codes):
    df = pvi_df.iloc[2:, :5]
    df = df[pd.notnull(df[0])]
    df.columns = ['STATE_NAME', 'DISTRICT', 'INCUMBENT', 'PARTY', 'PVI']
    df = df.merge(state_codes, how='left', on='STATE_NAME')
    df['Dist'] = (df['STUSAB'] 
            + '-' 
            + df['DISTRICT']
                .astype(str)
                .str.pad(2, 'left', '0')
                .replace('00','01')
    )
    df['Dist'] = df['Dist'].str.replace('-AL', '-01')
    
    df['pvi_pct'] = clean_cook_pvi(df['PVI'], True)
    return df[['Dist', 'PVI', 'pvi_pct']]


def clean_cook_pvi(pvi_column, do_rank=False):
    """Take the series, pvi_column and convert it to a continuous integer, where
        more negative means more democratic and more positive means more 
        republican.

        Args:
            pvi_column (Pandas Series): A Series of PVI values
            do_rank (bool): Convert to percentile or not
        Returns:
            A series of +/- integers
    """
    
    pvi_cleaned = (
        np.sum(
            pvi_column
            .str.replace('EVEN','R+0')
            .str.extract('([A-Z])\+(\d+)'),
            axis = 1
        )
    .str.replace('R','')
    .str.replace('D','-')
    .astype(int)
    )

    if do_rank:
        pvi_cleaned = pvi_cleaned.rank(pct = True)
    
    return pvi_cleaned
