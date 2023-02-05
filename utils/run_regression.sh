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
# this will generate the data and copy them to /home/$USER/runner_results directory

IMAGE_NAME="ghcr.io/idea-fasoc/openfasoc_ci:alpha"

for h in {5..9..2}
do
        for i in {2..10..2}
        do

            docker run --rm -v $PWD:$PWD -w $PWD $IMAGE_NAME bash -c "pip3 install -r requirements.txt && cd openfasoc/generators/temp-sense-gen/ && make clean && make sky130hd_temp_full sim=pex nhead=$h ninv=$i | tee -a $h-head-$i-inv.log"

            cd openfasoc/generators/temp-sense-gen/

            mkdir -p /home/$USER/runner_results/$h-head-$i-inv
            sudo cp -rf simulations/run/* /home/$USER/runner_results/$h-head-$i-inv/.
            sudo cp -rf work/* /home/$USER/runner_results/$h-head-$i-inv/.
            sudo cp $h-head-$i-inv.log /home/$USER/runner_results/$h-head-$i-inv/.

            cd ../../../

        done
done