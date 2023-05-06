# idea is to use this file to run checks for the particular generator. Basically it should include prePEX simulations, postPEX simulations,
# DRC/LVS checks.

# each check will be a python module. Before the check, another module should be present to run the generator. The concept behind having these
# modules is to import them into the main run_regression script. There is also another config file which has the input parameters range. It can also contain additional info but for now nothing other than the range is read.

import os, sys, fileinput, datetime, math, glob
import subprocess as sp

import pandas as pd
import numpy as np


class regression_ldo():
    
    '''
    Regression class will have the following methods -
    1. run_generator() -> to run the generator with the given arguments (not the input range directly) and generate all files
    2. checkDRC() -> to check and display the count of DRC errors - extracted from the report generated in the end
    3. checkLVS() -> to check and display the LVS errors if any - extracted from the report generated in the end
    4. copyData() -> to copy data from the generated location to the temporary result location.
    5. runSimulations() -> to run the simulations and generate logfiles
    6. processSims() -> to process the simulations log data and generate final data
    '''

    def __init__(self) -> None:
        self.image = "openfasoc_ci_image:latest"
        # self.home_dir = "/home/"+os.getenv("USER")+"/ldo/OpenFASOC/"
        self.home_dir = "/home/"+os.getenv("USER")+"/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims/openfasoc/OpenFASOC/"
        self.results_work_dir = self.home_dir+"openfasoc/generators/ldo-gen/work"
        self.runner_results_dir = "/home/"+os.getenv("USER")+"/runner_results"


    def run_generator(self, imax, vin):
        '''
        Run the generator using subprocess for the given configuration vins and imaxs.
        Returns the path where the work folder is present along with simulations/run folder which contains the spice netlists
        '''

        cmd = "pip3 install -r requirements.txt && cd openfasoc/generators/ldo-gen/ && make clean && make sky130hvl_ldo VoltsOut={0} AmpsMax={1}e-03 pex=True | tee -a {0}_vin_{1}mA_imax.log".format(vin, imax)

        os.chdir(self.home_dir)


        try:
            status = os.system("docker run --rm -v {0}:{0} -w {0} {1} bash -c '{2}'".format(os.getcwd(),self.image, cmd))
            logfile = self.results_work_dir+"/../{0}_vin_{1}mA_imax.log".format(vin, imax)
            with open(logfile) as log:

                if "[Err" in log.read() or "[Err" in log.read() or status:
                    return 1
                else:
                    return 0
        except:
            return 1
            

    def checkDRC(self):
        '''
        Reads 6_final_drc.rpt inside work directory of the generator and returns 1, if errors are found. Else 0.
        '''
        drc_rpt = self.results_work_dir+"/6_final_drc.rpt"
        with open(drc_rpt) as report:
            drc_errors = len(report.readlines()) - 3

            if drc_errors:
                return 1
            else:
                return 0


    def checkLVS(self):
        '''
        Read 6_final_lvs.rpt inside work directory of the generator and grep for the word 'Failed'. If found, return 1. Else return 0.
        '''
        lvs_rpt = self.results_work_dir+"/6_final_lvs.rpt"
        with open(lvs_rpt) as report:

            if "failed" in report.read():
                return 1
            else:
                return 0
            

    def copyData(self, imax, vin):
        '''
        Copy work directory and simulation/run directory to temporary run location where simulations and processing of data are done.
        '''
        os.system("mkdir -p "+self.runner_results_dir+"/ldo/{0}_vin_{1}mA_imax".format(vin, imax))
        os.system("cp -rf "+ self.results_work_dir + "/../simulations/run/* "+ self.runner_results_dir+"/ldo/{0}_vin_{1}mA_imax/.".format(vin, imax))
        os.system("cp -rf "+ self.results_work_dir + " " + self.runner_results_dir+"/ldo/{0}_vin_{1}mA_imax/.".format(vin, imax))
        os.system("cp -rf "+ self.results_work_dir + "/../tools/* " + self.runner_results_dir+"/ldo/{0}_vin_{1}mA_imax/.".format(vin, imax))
        os.system("mv "+self.results_work_dir+"/../{0}_vin_{1}mA_imax.log ".format(vin, imax) + self.runner_results_dir+"/ldo/{0}_vin_{1}mA_imax/.".format(vin, imax))
        # os.system("sudo rm -rf "+self.results_work_dir + "/../simulations/run")


    def runSimulations(self, vin, imax):
        '''
        Run through all above copied directories, go into each prePEX folder and replace tempInstance_error.spice netlist path. 
        Then run simulations using subprocess python library. Returns the list of subprocess which 
        we loop through and run wait command.

        ref: https://github.com/idea-fasoc/OpenFASOC-sims/blob/main/utils/run_sim.py 
        '''


        # get the list of all folders inside /home/runner_results/

        designName = "ldo"
        freqs_list = [0.1,1.0,10.0]
        caps_list = [1,5]
        processes=[]

        rootDir = self.runner_results_dir+"/ldo/{0}_vin_{1}mA_imax".format(vin, imax)
        i = rootDir

        if os.path.isdir(i):

            config=i.split("/")[-1].split("_")
            vin=config[0]
            imax=config[2]

            # "['ngspice -b -o ldo_0.1MHz_1p_out.txt -i ldo_tran_1.0mA_0.1MHz_1p.sp', 'ngspice -b -o ldo_0.1MHz_5p_out.txt -i ldo_tran_1.0mA_0.1MHz_5p.sp', 'ngspice -b -o ldo_1.0MHz_1p_out.txt -i ldo_tran_1.0mA_1.0MHz_1p.sp', 'ngspice -b -o ldo_1.0MHz_5p_out.txt -i ldo_tran_1.0mA_1.0MHz_5p.sp', 'ngspice -b -o ldo_10.0MHz_1p_out.txt -i ldo_tran_1.0mA_10.0MHz_1p.sp', 'ngspice -b -o ldo_10.0MHz_5p_out.txt -i ldo_tran_1.0mA_10.0MHz_5p.sp', 'ngspice -b -o pwrout.txt -i pwrarr.sp', 'ngspice -b -o ldo_load_change.txt -i ldo_load_change.sp']"

            for root, dirs, names in os.walk(i):
                dirs.remove("work")
                break
            
            
            # look for directory name starting with PEX and prePEX and build path to ammend to the filename.
            for j in dirs:

                path = i+"/"+j
                runDir = path

                for freq in freqs_list:
                    for cap in caps_list:

                        p = sp.Popen(
                            [
                                "ngspice",
                                "-b",
                                "-o",
                                "{0}/{1}_{2}MHz_{3}p_out.txt".format(path, designName, freq, cap),
                                "-i",
                                "{0}/{1}_tran_{2}_{3}MHz_{4}p.sp".format(path, designName, imax, freq, cap),
                            ],
                            cwd=runDir,
                        )
                        processes.append(p)

        return processes
    
        
    def processSims(self, vin, imax):

        runDir = self.runner_results_dir+"/ldo/{0}_vin_{1}mA_imax/".format(vin, imax)

        for root, dirs, names in os.walk(runDir):
            dirs.remove("work")
            break
        
        # look for directory name starting with PEX and prePEX and build path to ammend to the filename.
        for j in dirs:

            sim_dir = runDir+"/"+j+"/"

            sim_type = j.split("_")[0]

            p = sp.Popen(["python3","processing.py","--file_path", sim_dir,"--vref",str(vin),"--iload",str(imax),"--odir",runDir, "--figs", "False", "--simType", sim_type],cwd=runDir)
            p.wait()



