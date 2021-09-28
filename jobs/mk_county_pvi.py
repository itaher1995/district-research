import pandas as pd

from district_research.data.pvi import calculate_pvi, clean_cook_pvi

def main():

    df = pd.read_csv('data/countypres_2000-2020.csv')
    pvi_df = calculate_pvi(df, 'county_fips')
    pvi_df['county_pvi_pct'] = pvi_df.groupby('year')['pvi'].transform(clean_cook_pvi, do_rank=True)
    pvi_df.to_csv('data/countypres_pvi.csv', index=False)

if __name__ == '__main__':
    main()