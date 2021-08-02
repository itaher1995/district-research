"""Uses election data to create certain views such as voting history of 
    district
"""
import numpy as np
import pandas as pd

def get_general_election_results(df, start, stop, area, is_district):
    """Grabs general election results from a dataset that aheres to the MIT
    Election Lab dataset schemas.

        Args:
            df (Pandas DataFrame): A DataFrame that contains election returns
            data
            start (int): Beginning of the time window that data is collected for
            stop (int): End of the time window that data is collected for.
            area (str): The identifier to filter on. E.g. could be a state
            abbreviation like 'AK' or a district like 'NY-03'
            is_district (bool): Defines whether this is a district query or a
            state query. If its district there is slightly different logic to
            create the final view.
        
        Returns:
            A DataFrame with the required data.
    """

    subset = df[(df['year'] >= start) & (df['year'] <= stop)]

    # Democrats are named different things in two states, ND and MN.
    subset['party'] = (
        subset['party']
        .replace('DEMOCRATIC-FARMER-LABOR', 'DEMOCRAT')
        .replace('DEMOCRATIC-NONPARTISAN LEAGUE', 'DEMOCRAT')
    )
    subset['party'] = np.where(
        ~subset['party'].isin(['DEMOCRAT', 'REPUBLICAN']),
        'OTHER',
        subset['party'])

    # presidential data assumes general election, so stage is not a column in
    # that dataset.
    if 'stage' in subset.columns:
        subset = subset[subset['stage'] == 'gen']
    
    # sort + groupby + cumcount is supposedly the equivalent of a window function
    # that uses row_number() as its ranking function in sql
    partition_cols = ['year', 'state_po', 'party']

    if is_district:
        partition_cols.append('district')

    subset['rank'] = (
        subset
        .sort_values('candidatevotes', ascending = False)
        .groupby(partition_cols)
        .cumcount() + 1
    )

    # adding the rank to  the party name when the rank of that candidate relative
    # to other candidates of the same party is the general election is not 1.
    # This generally is an issue in states like California, where multiple 
    # Democrats appear on the general election ballot.
    subset['party'] = np.where(
        (subset['rank'] != 1) & (subset['party'].isin(['DEMOCRAT', 'REPUBLICAN'])), 
        subset['party'] + ' (' + subset['rank'].astype(str) + ')', 
        subset['party']
    )

    # Any named party candidate that isn't the top 2 for that party will be
    # considered OTHER. This is for simplicity purposes. 
    subset['party'] = np.where(
        subset['party'].isin(['DEMOCRAT', 'REPUBLICAN', 'DEMOCRAT (2)', 'REPUBLICAN (2)']),
        subset['party'],
        'OTHER'
    )

    if is_district:
        filter_col = 'CD'
        subset[filter_col] = (
            subset['state_po']
            + '-'
            + subset['district'].astype(str)
                .str.pad(2, 'left', '0')
        )
    else:
        filter_col = 'state_po'

        # don't include any secondary democrats or republicans in non-house races
        # these may be write ins. 
        subset = subset[~subset['party'].str.match('(?:DEMOCRAT|REPUBLICAN) \(\d\)')]
    
    return (
        subset[['year', filter_col, 'party', 'candidatevotes']]
        [subset[filter_col] == area]
    )


def clean_daily_kos2020(df):
    """Code to clean the daily kos general election results by congressional
        district.

        Args:
            df (Pandas DataFrame): A DataFrame containing election results from
            2012 to 2020
        
        Returns:
            A cleaned pandas dataframe with election results.
    """
    df_copy = df.iloc[:, :9]
    df_copy.columns = ["district", "incumbent", "party", "dem_2020", "rep_2020", 
                    "dem_2016", "rep_2016", "dem_2012", "rep_2012"]
    df_copy = df_copy.drop(['incumbent', 'party'], axis=1)

    df_copy = df_copy.melt(
        id_vars='district', 
        value_vars = ['dem_2020', 'rep_2020', 'dem_2016', 'rep_2016', 'dem_2012', 'rep_2012']
    )

    df_copy[["party", "year"]] = pd.DataFrame(df_copy["variable"].str.split("_").values.tolist())
    df_copy = df_copy.pivot_table(index = ["year", 'district'], columns = "party", values = "value").reset_index()
    df_copy["other"] = 100 - df_copy["dem"] - df_copy["rep"]
    df_copy.columns = ['YEAR', 'CD', 'DEMOCRAT', 'REPUBLICAN', 'OTHER']
    df_copy['CD'] = df_copy['CD'].str.replace('-AL', '-01')
    df_copy = df_copy.melt(id_vars = ['YEAR', 'CD'], var_name='PARTY', value_name='PCT')

    return df_copy
