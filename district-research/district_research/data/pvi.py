"""Code to clean/work with 2017 PVI Data downloaded from the Cook Political Report"""

import numpy as np
import pandas as pd

def clean_pvi_2020(pvi_df, state_codes):
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
    
    df['pvi_pct'] = clean_pvi(df['PVI'], True)
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
