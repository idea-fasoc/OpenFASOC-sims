#!/bin/bash

# run build_csv.py to generate the csv data
python3 build_csv.py

# copy generated csv data to the github repo
FILE_prePEX=data_prePEX.csv
if [ -f "$FILE_prePEX" ]; then
    mkdir -p $GITHUB_WORKSPACE/prePEX_data_results
    mkdir -p $GITHUB_WORKSPACE/latest
    cp $FILE_prePEX $GITHUB_WORKSPACE/prePEX_data/data_prePEX_$(date +%m-%d-%Y-%T).csv
    cp $FILE_prePEX $GITHUB_WORKSPACE/latest/data_prePEX.csv
fi

FILE_postPEX=data_postPEX.csv
if [ -f "$FILE_postPEX" ]; then
    mkdir -p $GITHUB_WORKSPACE/PEX_data
    mkdir -p $GITHUB_WORKSPACE/latest
    cp $FILE_postPEX $GITHUB_WORKSPACE/PEX_data/data_postPEX_$(date +%m-%d-%Y-%T).csv
    cp $FILE_postPEX $GITHUB_WORKSPACE/latest/data_postPEX.csv
fi


# archive the results folder, store it in /home/$USER/runner_results/. and clean the runner_results folder
mkdir -p /home/$USER/runner_archives/
tar cvfz /home/$USER/runner_archives/$(date +%m-%d-%Y-%T)_regression_result.tar.gz .
sudo rm -rf /home/$USER/runner_results/*