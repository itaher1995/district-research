# District Research

## Overview

District Research is a project aimed to understand the socioeconomic and partisan characteristics of a district. We will use American Community Survey Five Year Estimates, as well as congressional district returns.

## Data

American Community Survey data contains demographic information for a variety of different geographies. For example, we can get the median income of a given zip code. We will use the ACS five year estimates in order to capture information at more granular levels, e.g. zip code, county. By using more granular estimates, we not only increase the size of our population (50 states is less than 3000 zip codes), but we can also target specific areas (e.g. counties and zip codes rather than congressional districts and states.) This may help with GOTV campaigns and canvassing. 

We will also grab partisanship data to see how the socioeconomic variables correlate with partisanship. The reason we chose partisanship is because, we found in a previous analysis that measures like PVI correlate with ideology. In other words, highly partisan districts are where the most progressive candidates are coming from. 

### American Community Survey

The best way to gather ACS data is by using an API. The Census is a terrible website. We interact with the API through the `district-research` library. At the moment we pull data tables for zip codes.

### Getting the Elections Return Datasets

Please save these datasets in the `data` folder.

**House**: To get the house data go [here](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/IG0UN2). After which you should see the dataset, 
1976-2018-house3.tab, click the download button all the way to the right. The 2020 data is downloaded from POLITICO and USA Today. See `jobs/scrape_2020_house_results.py` for more information.

**Senate**: 



**President**:

### ZCTA Shapefiles

Download from [here](https://www2.census.gov/geo/tiger/TIGER2019/ZCTA5/). Please unzip and save in the `data` folder.

### ZCTAto Congressional District Crosswalk

ZCTA to Congressional District data is gathered from two sources. The first source is a list of ztcas to congressional districts in states with 

## Goals

1. To provide quick analysis regarding the socioeconomic state of affairs in a congressional district
2. To measure, over time, how a district has changed based on ACS data. This can be used to target future districts.
3. To relate district socioeconomic changes to the district's partisanship.
4. Create a dashboard that will allow leadership to be proactive in understanding districts.

## Project Structure

`conf` will house the list of districts we'll parse as well as the census api key
`data` is the location that the immutable datasets should be stored.
`views` is the location that views generated either from ACS API or immutable datasets will be stored.
`outputs` where the outputs will be stored
`zips` where the zipped outputs will be stored
`district-research` the library used for most of the data munging and analysis
`streamlit` scripts used to launch streamlit dashboard for visualizing district data
`venv` is where the virtual environment will live
`jobs` stores scripts used for project
`notebooks` location to store jupyter notebooks
`Makefile` contains some shortcuts (kind of a duplicate of jobs.sh honestly)

## A Note on Notebooks

While version controlling jupyter notebooks can be kind of pointless, we do need to host these notebooks because we use them for visualizing data for the district research portion. Volunteers will access these notebooks while they are hosted as Google Colab Notebooks.

## Requirements

Python (preferably >= Python 3.7)
Bash