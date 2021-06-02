SHELL := /bin/bash

venv: requirements.txt
	rm -rf venv
	. jobs/funs.sh && make_venv

deps: $(SHELL find district-research -type f)
	. jobs/funs.sh && install_libs

maps: venv deps
	. jobs/funs.sh && create_zip_acs_views --PLOT_MAPS

acs_zip: venv deps
	. jobs/funs.sh && create_zip_acs_views --SAVE_VIEW

acs_cd: venv deps
	. jobs/funs.sh && create_acs_view congressional_district

acs_state: venv deps
	. jobs/funs.sh && create_acs_view state

acs: venv deps
	. jobs/funs.sh && create_zip_acs_views --SAVE_VIEW
	. jobs/funs.sh && create_acs_view congressional_district
	. jobs/funs.sh && create_acs_view state

voteplots: venv deps
	. jobs/funs.sh && plot_vote_history

housedata2020: venv deps
	. jobs/funs.sh && scrape_house_results_2020
