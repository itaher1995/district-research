import os

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .data.acs import get_acs_data_table
from .data.elections import get_general_election_results

def plot_district_characteristic(map_cd_df, district, characteristic, 
    title=None, save_dir=None):
    """Plots and saves the map for a given congressional district and
        characteristic.

        Args:
            map_cd_df (Geopandas DataFrame): Dataframe with shape info,
            congressional district info and zip code
            district (str): The district to plot
            characteristic (str): The code to plot from the data table from
            ACS data.
        Returns
            Nothing, but plots a map.
    """

    if district[-2:] != 'SN':
        district_df = map_cd_df[(map_cd_df['CD'] == district)]
    else:
        district_df = map_cd_df[(map_cd_df['CD'].str.startswith(district[:2]))]

    # The annotation variable indicates something is off for an estimate when it
    # is filled in. Therefore we only want when these annotation variable is not
    # filled in.
    district_df = district_df[pd.isnull(district_df[f'{characteristic}A'])]

    # always convert to float to ensure that percent estimates and estimates can
    # be read in
    district_df[characteristic] = district_df[characteristic].astype(float)

    fig, ax = plt.subplots()
    (
        district_df
        [pd.notnull(district_df['geometry'])]
        .plot(column=characteristic, legend=True, cmap='Blues', edgecolor="black", ax=ax)
    )

    plt.xlabel('Latitude')
    plt.ylabel('Longitude')

    if title:
        plt.title(title)
    else:
        plt.title(characteristic)

    if save_dir and title:
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        plt.savefig(f'{save_dir}/{title}.png')
    elif save_dir:
        plt.savefig(f'{save_dir}/{characteristic}.png')
    return fig


def plot_house_general_election_results(df, district, save_dir, start, stop):
    """Plots general election results in a given district for Democrats and
        Republicans.
    """

    # TODO(any): extend this to senate and presidential races if needed
    sns.set_style('whitegrid')
    res = get_general_election_results(df, start, stop, district, True)
    
    plt.figure(figsize=(15, 4))
    sns.lineplot(data=res, x='year', y='candidatevotes', hue='party')
    plt.xlabel('Year')
    plt.ylabel('Number of Votes')
    plt.title(f'Number of Voters from {start} to {stop} ({district})')
    plt.ylim(bottom=0)

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    
    plt.savefig(f'{save_dir}/{district}-candidate-votes-{start}-{stop}.png')
