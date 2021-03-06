# District Research

Primary Developer: [Ibrahim Taher](https://github.com/itaher1995)

## Overview

District Research is a project aimed to understand the socioeconomic and partisan characteristics of a district. We will use American Community Survey One/Five Year Estimates, as well as congressional district returns.

## Data

American Community Survey data contains demographic information for a variety of different geographies. For example, we can get the median income of a given zip code. We will use the ACS five year estimates in order to capture information at more granular levels, e.g. zip code, county. By using more granular estimates, we not only increase the size of our population (50 states is less than 3000 zip codes), but we can also target specific areas (e.g. counties and zip codes rather than congressional districts and states.) This may help with GOTV campaigns and canvassing. 

We will also grab partisanship data to provide added context to demographic and electoral information. The reason we chose partisanship is because, we found in a previous analysis that measures like PVI correlate with ideology. In other words, highly partisan districts are where the most progressive candidates are coming from. PVI is a metric created by The Cook Political Report.

### American Community Survey

The best way to gather ACS data is by using an API. The Census is a terrible website. We interact with the API through the `district-research` library. At the moment we pull data tables for zip codes. To learn more about the ACS API, please go [here](https://www.census.gov/data/developers/data-sets/acs-1year.html) for information on the ACS 1-year estimates and [here](https://www.census.gov/data/developers/data-sets/acs-5year.html) for 5-year esimates. We're interested in the data profiles. The codes are largely the same for both estimates so please visit [here](https://api.census.gov/data/2019/acs/acs5/variables.html) to identify other codes of interest.

### Getting the Elections Return Datasets

Please save these datasets in the `data` folder.

**House**: To get the house data go [here](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/IG0UN2). After which you should see the dataset, 1976-2018-house3.tab, click the download button all the way to the right. Download it in the original format (csv). The 2020 data is downloaded from POLITICO and USA Today. See `jobs/scrape_2020_house_results.py` for more information.

**Senate**: To get the senate data go [here](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PEJ5QU). After which you should see the dataset, 1976-2020-senate.tab, click the download button all the way to the right. Download it in the original format (csv). 

**President**: To get the presidential data by state go [here](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX). After which you should see the dataset, 1976-2020-president.tab, click the download button all the way to the right. Download it in the original format (csv).

### ZCTA Shapefiles

Download from [here](https://www2.census.gov/geo/tiger/TIGER2019/ZCTA5/). Please unzip and save in the `data` folder.

### ZCTA to Congressional District Crosswalk

ZCTA to Congressional District data is gathered from the [Geographic Correspondence Engine](https://mcdc.missouri.edu/applications/geocorr2018.html). Please download and save in `data` folder.

### PVI

PVI is the partisan voter index from the Cook Political Report. Please click **Get the data** [here](https://cookpolitical.com/pvi-map-and-district-list) to get 2017 data. Rename to pvi.csv and move to `data` folder. For 2021 data, please contact Ibrahim Taher for the dataset.

For calculating PVI we'll need two datasets. Both are from Daily Kos. The [first](https://docs.google.com/spreadsheets/d/1XbUXnI9OyfAuhP5P3vWtMuGc5UJlrhXbzZo3AwMuHtk/edit#gid=0) will have historical results (2012-2020) for districts in 2020. The [second](https://docs.google.com/spreadsheets/d/1whYBonfwlgTGnYl7U_IH31G0JNYQ9QBIjDfqkZHkW-0/edit#gid=0) will have historical results (2008-2016) for districts in 2020. We combine to get a full view of districts from 2008-2020. Download and save in `data` folder.

## Goals

1. To provide quick analysis regarding the socioeconomic state of affairs in a congressional district
2. To measure, over time, how a district has changed based on ACS data. This can be used to target future districts.
3. To relate district socioeconomic changes to the district's partisanship.
4. Create a dashboard that will allow leadership to be proactive in understanding districts.

## Project Structure

`conf` will house the list of districts we'll parse as well as the census api key
`data` is the location that the immutable datasets should be stored.
`outputs` where the outputs will be stored
`zips` where the zipped outputs will be stored
`district-research` the library used for most of the data munging and analysis
`streamlit` scripts used to launch streamlit dashboard for visualizing district data
`venv` is where the virtual environment will live
`jobs` stores scripts used for project
`notebooks` location to store jupyter notebook used to launch district dashboard.
`Makefile` contains some shortcuts (kind of a duplicate of jobs.sh honestly)

## Requirements

Python (preferably >= Python 3.7)
Bash

## Major TODOs:

1. Change saving directory for some datasets from `data` to `views`. We need to do this to segregate immutable data from data that's transformed. 