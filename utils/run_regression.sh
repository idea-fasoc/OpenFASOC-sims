#!/bin/bash

# for h in {5..9..2}
# do
#         for i in {2..10..2}
#         do
#                 echo "[regression] Starting for $h-head-$i-inv config"
#                 cd /home/alex/OpenFASOC/openfasoc/generators/temp-sense-gen
#                 make clean && make sky130hd_temp_full sim=pex nhead=$h ninv=$i | tee -a $h-head-$i-inv.log
#                 mkdir -p /home/alex/results/$h-head-$i-inv
#                 cp -rf simulations/run/* /home/alex/results/$h-head-$i-inv/.
#                 cp -rf work/* /home/alex/results/$h-head-$i-inv/.
#                 cp $h-head-$i-inv.log /home/alex/results/$h-head-$i-inv/.
#                 echo "[regression] Completed for $h-head-$i-inv config"
#         done
# done

# /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims - /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims
# /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims - /home/alex/git_runner/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims
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

# copy this script from utils to openfasoc/OpenFASOC/. and then run it.

# this will generate the data and copy them to /home/$USER/runner_results directory

h=3
i=6
IMAGE_NAME="ghcr.io/idea-fasoc/openfasoc_ci:alpha"

docker run --rm -v $PWD:$PWD -w $PWD --user $(id -u):$(id -g) $IMAGE_NAME bash -c "pip3 install -r requirements.txt && cd openfasoc/generators/temp-sense-gen/ && make clean && make sky130hd_temp_full sim=pex nhead=$h ninv=$i | tee -a $h-head-$i-inv.log"

cd openfasoc/generators/temp-sense-gen/

mkdir -p /home/$USER/runner_results/$h-head-$i-inv
sudo cp -rf simulations/run/* /home/$USER/runner_results/$h-head-$i-inv/.
sudo cp -rf work/* /home/$USER/runner_results/$h-head-$i-inv/.
sudo cp $h-head-$i-inv.log /home/$USER/runner_results/$h-head-$i-inv/.

sudo make clean

