"""Uses election data to create certain views such as voting history of 
    district
"""
import numpy as np

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
    
    # star is used to calculate PVI. We will capture all votes across states.
    if area != '*':
        return (
            subset[['year', filter_col, 'party', 'candidatevotes']]
            [subset[filter_col] == area]
        )
    else:
        return subset[['year', filter_col, 'party', 'candidatevotes']]


def project_voter_turnout():
    """Creates a dataframe for a given district that projects the final voter
        turnout.
    """
    pass
