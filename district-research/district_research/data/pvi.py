"""Code to clean/work with 2017 PVI Data downloaded from the Cook Political Report"""

import numpy as np

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
