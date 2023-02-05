# openfasoc-sims

## workflows

**build_docker_image.yml**

* Build the docker container containing all tools (yosys, openroad, magic, netgen, ngspice and Xyce) and latest PDK version using open_pdks PDK installers. This container is built using the Dockerfile present in the `docker_image/` location in the root of this repo.

* This image is stored on GitHub Container Registery (ghcr.io) and is attached to this repository. This contianer is used for the CI purposes under this repo

**tempSense_sky130hd.yml**

* Run the generator (including sims) for all possible header-inverter combinations using the above build container, with the help of the `run_regression.sh` script present in `utils/` directory in the root of this repo.

* The results are stored on the runner machine for building the csv data file using `build_csv.py` script present in `utils/` directory

* Later, the results are archived and stored in `/home/$USER/runner_archives` location on the runner machine with the archive name under the format `$(date +%m-%d-%Y-%T)_regression_result.tar.gz`

* The csv file is pushed back to this repository with the file name in the format `data_$(date +%m-%d-%Y-%T).csv`
