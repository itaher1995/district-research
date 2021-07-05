#!/bin/bash

# A set of functions to use on a UNIX machine (Linux/Mac) that aid with interactive
# development. We still need to decide whether a Windows version is needed. 

# If PYTHON does not point to your python installation, then you'll need to
# change this variable. If you installed anaconda then this should work.
PYTHON=$CONDA_PYTHON_EXE
PROJ_PYTHON='venv/bin/python'
CENSUS_API_KEY=$(cat conf/censuskey.txt)

# TODO(any): Better venv setup. How can i get it such that it only updates
# if there are changes to requirements OR library
make_venv() {
    $PYTHON -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    deactivate
}

# function to install BNC libraries
install_libs() {
    . venv/bin/activate
    cd district-research && python setup.py install && cd -
    deactivate
}

# creates a view of acs data. View is zip code level acs five year estimate data for certain
# indicators. The view can be a dataframe (all data) or maps (from config.)
# $1 = Either --PLOT_MAPS for plotting maps or --SAVE_VIEW to save view
create_zip_acs_views() {
    $PROJ_PYTHON jobs/mk_acs_zip_cd_view.py \
        --API_KEY=${CENSUS_API_KEY} \
        --EST=acs5 \
        --YEAR=2019 \
        $1
}

# Creates a view based on a given level
# $1 = geography. Ideally should be congressional_district or state
create_acs_view() {
    $PROJ_PYTHON jobs/mk_acs_view.py \
        --API_KEY=${CENSUS_API_KEY} \
        --EST=acs1 \
        --YEAR=2019 \
        --GEO=$1
}

# plots vote history for congressional races from 2008 to 2020
plot_vote_history() {
    $PROJ_PYTHON jobs/plt_vote_history.py
}

# Create full 2020 house general election results 
scrape_house_results_2020() {
    $PROJ_PYTHON jobs/mk_election_results_2020.py
}


zip_district_outputs() {
    dirs=$(ls outputs/)
    array=($(echo $dirs | tr " " "\n"))
    echo $array
    for a in "${array[@]}";
    do
        zip "zips/$a.zip" "outputs/$a/*"
    done
}

launch_dash() {
    . venv/bin/activate
    streamlit run streamlit/app.py
    deactivate
}

calculate_pvi() {
    $PROJ_PYTHON jobs/mk_pvi.py
}

# zip everything needed for streamlit
zip_streamlit() {
    zip -r "zips/conf.zip" \
        "conf/censuskey.txt"

    zip -r "zips/data.zip" \
        "data/1976-2018-house3.csv" \
        "data/1976-2020-president.csv" \
        "data/1976-2020-senate.csv" \
        "data/2020-house-full.csv" \
        "data/acs1-congressional-district-indicators-2019.csv" \
        "data/acs1-state-indicators-2019.csv" \
        "data/acs-zcta5-cong-dist-indicators-2019.csv" \
        "data/tl_2019_us_zcta510" \
        "data/pvi.csv"
}
