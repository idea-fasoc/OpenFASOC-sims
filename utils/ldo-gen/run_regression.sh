#!/bin/bash

# $GITHUB_WORKSPACE = /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims - /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims
# $PWD = /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims - /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims
# tree -L 2
# .
# ├── LICENSE
# ├── README.md
# ├── docker_image
# │   ├── Dockerfile
# │   └── xyce_install.sh
# ├── openfasoc
# │   └── OpenFASOC
# └── utils
#     └── build_csv.py

# copy this script from utils to openfasoc/OpenFASOC/. . navigate to that location and then run it.
# this will generate the spice decks in the end and copy them to /home/$USER/runner_results

IMAGE_NAME="ghcr.io/idea-fasoc/openfasoc_ci:alpha"

for b in $(seq 1.8 0.5 3.3)
do
    for c in $(seq 0.5 0.5 25)
    do

        docker run --rm -v $PWD:$PWD -w $PWD $IMAGE_NAME bash -c "pip3 install -r requirements.txt && cd openfasoc/generators/ldo-gen/ && make clean && make sky130hvl_ldo_full VoltsOut=$b AmpsMax=$c\e-03 | tee -a $bv-$c\mA.log"

        cd openfasoc/generators/ldo-gen/

        mkdir -p /home/$USER/runner_results/ldo-gen/$bv-$c\mA
        sudo cp -rf simulations/run/* /home/$USER/runner_results/ldo-gen/$bv-$c\mA/.
        sudo cp -rf work/* /home/$USER/runner_results/ldo-gen/$bv-$c\mA/.
        sudo cp $bv-$c\i.log /home/$USER/runner_results/ldo-gen/$bv-$c\mA/.

        cd ../../../
    done

done