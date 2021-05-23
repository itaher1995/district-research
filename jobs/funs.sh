#!/bin/bash

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

# Create full dataset 
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

# Code to create the dashboard on google colab. May break if testing in local.
launch_colab_dash() {
    . venv/bin/activate
    npm install localtunnel
    streamlit cache clear
    streamlit run streamlit/app.py &>/dev/null&
    lt --port 8501
    deactivate
}

launch_dash() {
    . venv/bin/activate
    streamlit run streamlit/app.py
    lt --port 8501
}
