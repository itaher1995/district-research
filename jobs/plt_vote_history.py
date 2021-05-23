import logging

import pandas as pd

from district_research.viz import plot_house_general_election_results

def main():
    logging.basicConfig(level=logging.INFO)

    with open('conf/districts.txt', 'r') as f:
        districts = f.readlines()
        districts = [x.replace('\n','').strip() for x in districts]
    
    df = (
        pd.read_csv('data/1976-2018-house3.csv')
        [['year', 'state_po', 'district', 'party', 'candidatevotes', 'stage']]
    )
    df2020 = (
        pd.read_csv('data/2020-house-full.csv')
        [['year', 'state_po', 'district', 'party', 'candidatevotes', 'stage']]
    )
    df2020['district'] = df2020['district'].astype(str).str.pad(2, 'left', '0')

    final_df = pd.concat([df, df2020], axis=0)

    for d in districts:
        logging.info(f'Plotting voting history for {d}...')
        plot_house_general_election_results(final_df, d, f'outputs/{d}', 2008, 2020)

if __name__ == "__main__":
    main()


