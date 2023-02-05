#!/bin/bash

echo "GITHUB_WORKSPACE - $GITHUB_WORKSPACE"
# run build_csv.py to generate the csv data
python3 build_csv.py
cp data.csv /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims/data_$(date +%m-%d-%Y-%T).csv

# tar the results folder and store it in /home/$USER/runner_results/. along with $(data +%m-%d-%Y) appended in the end 
# clean the runner_results folder
mkdir -p /home/$USER/runner_archives/
tar cvfz /home/$USER/runner_archives/$(date +%m-%d-%Y-%T)_regression_result.tar.gz .
sudo rm -rf /home/$USER/runner_results/*