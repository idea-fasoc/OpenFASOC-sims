#!/bin/bash

echo "GITHUB_WORKSPACE - $GITHUB_WORKSPACE"
# run build_csv.py to generate the csv data
python3 build_csv.py

# copy generated csv data to the github repo
FILE_prePEX=data_prePEX.csv
if [ -f "$FILE_prePEX" ]; then
    cp $FILE_prePEX $GITHUB_WORKSPACE/data_prePEX_$(date +%m-%d-%Y-%T).csv
fi

FILE_postPEX=data_postPEX.csv
if [ -f "$FILE_postPEX" ]; then
    cp $FILE_postPEX $GITHUB_WORKSPACE/data_postPEX_$(date +%m-%d-%Y-%T).csv
fi


# archive the results folder, store it in /home/$USER/runner_results/. and clean the runner_results folder
mkdir -p /home/$USER/runner_archives/
tar cvfz /home/$USER/runner_archives/$(date +%m-%d-%Y-%T)_regression_result.tar.gz .
sudo rm -rf /home/$USER/runner_results/*