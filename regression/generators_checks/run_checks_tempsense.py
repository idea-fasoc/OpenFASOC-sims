# idea is to use this file to run checks for the particular generator. Basically it should include prePEX simulations, postPEX simulations,
# DRC/LVS checks.

# each check will be a python module. Before the check, another module should be present to run the generator. The concept behind having these
# modules is to import them into the main run_regression script. There is also another config file which has the input parameters range. It can also contain additional info but for now nothing other than the range is read.

import os, sys, fileinput, datetime, math
import subprocess as sp


class regression_tempsense():
    
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
        # self.home_dir = "/home/"+os.getenv("USER")+"/OpenFASOC/"
        self.home_dir = "/home/"+os.getenv("USER")+"/actions-runner/_work/OpenFASOC-sims/OpenFASOC-sims/openfasoc/OpenFASOC"
        self.results_work_dir = self.home_dir+"/openfasoc/generators/temp-sense-gen/work"
        self.runner_results_dir = "/home/"+os.getenv("USER")+"/runner_results"


    def run_generator(self, ninv, nhead):
        '''
        Run the generator using subprocess for the given configuration nheads and ninvs.
        Returns the path where the work folder is present along with simulations/run folder which contains the spice netlists
        '''
        cmd = "pip3 install -r requirements.txt && cd openfasoc/generators/temp-sense-gen/ && make clean && make sky130hd_temp sim=pex nhead={0} ninv={1} | tee -a {0}_head_{1}_inv.log".format(nhead, ninv)

        os.chdir(self.home_dir)

        status = os.system("docker run --rm -v {0}:{0} -w {0} {1} bash -c '{2}'".format(os.getcwd(),self.image, cmd))

        return status


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
            

    def copyData(self, ninv, nhead):
        '''
        Copy work directory and simulation/run directory to temporary run location where simulations and processing of data are done.
        '''

        os.system("mkdir -p "+self.runner_results_dir+"/{0}_head_{1}_inv".format(nhead, ninv))
        os.system("cp -rf "+ self.results_work_dir + "/../simulations/run/* "+ self.runner_results_dir+"/{0}_head_{1}_inv".format(nhead, ninv))
        os.system("cp -rf "+ self.results_work_dir + " " + self.runner_results_dir+"/{0}_head_{1}_inv".format(nhead, ninv))
        os.system("mv "+self.results_work_dir+"/../{0}_head_{1}_inv.log ".format(nhead, ninv) + self.runner_results_dir+"/{0}_head_{1}_inv".format(nhead, ninv))


    def runSimulations(self, nhead, ninv):
        '''
        Run through all above copied directories, go into each prePEX folder and replace tempInstance_error.spice netlist path. 
        Then run simulations using subprocess python library. Returns the list of subprocess which 
        we loop through and run wait command.
        ref: https://github.com/idea-fasoc/OpenFASOC-sims/blob/main/utils/run_sim.py 
        '''


        # get the list of all folders inside /home/runner_results/


        designName = "tempsenseInst_error"
        temp_list=[-20, 0, 20, 40, 60, 80, 100]
        processes=[]

        rootDir = self.runner_results_dir+"/{0}_head_{1}_inv".format(nhead, ninv)
        i = rootDir

        # i is the path of the directory - eg: /home/alex/runner_results/5_head_10_inv
        if os.path.isdir(i):

            config=i.split("/")[-1].split("_")
            header=config[0]
            inverter=config[2]

            # look for directory name starting with PEX and prePEX and build path to ammend to the filename.
            for j in ["prePEX", "PEX"]:
                path = i+"/"+j+"_inv"+inverter+"_header"+header
                runDir = path

                for temp in temp_list:

                    # modify the path of the base spice file in .include line - https://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
                    with fileinput.input(path+"/{0}_sim_{1}.sp".format(designName, temp), inplace=True) as file:
                        for line in file:
                            if ".include" in line:
                                text = line.split(".include")
                                new_line = line.replace(text[1].strip(),"'{0}/{1}.spice'".format(path, designName))
                            else:
                                new_line = line

                            print(new_line, end='')


                    p = sp.Popen(
                        [
                            "ngspice",
                            "-b",
                            "-o",
                            "%s/%s_sim_%d.log" % (path, designName, temp),
                            "%s/%s_sim_%d.sp" % (path, designName, temp),
                        ],
                        cwd=runDir,
                    )
                    processes.append(p)

        return processes


    def processSims(self, nhead, ninv):

        designName = "tempsenseInst_error"
        temp_list=[-20, 0, 20, 40, 60, 80, 100]
        processes=[]

        rootDir = self.runner_results_dir+"/{0}_head_{1}_inv".format(nhead, ninv)
        i = rootDir

        # TODO this part needs to be changed from processing simulation log files inside all folders all simulations to just the folder with the given config

        # for i in os.listdir(rootDir):

        # i is the path of the directory - eg: /home/alex/runner_archives/5-head-10-inv
        if os.path.isdir(rootDir+"/"+i):
            

            config=i.split("-")
            header=config[0]
            inverter=config[2]
    
            # look for directory name starting with PEX and prePEX and build path to ammend to the filename.
            for j in ["prePEX", "PEX"]:
                path = i+"/"+j+"_inv"+inverter+"_header"+header
                runDir = path
                os.chdir(path)
                timediff = []

                for temp in temp_list:
                    
                    # get the time diff between the last modifications of .sp file and .log file
                    if os.path.exists("%s/%s_sim_%d.log" % (path, designName, temp)):

                        value = datetime.datetime.fromtimestamp(os.path.getmtime("%s/%s_sim_%d.log" % (path, designName, temp))) - datetime.datetime.fromtimestamp(os.path.getmtime("%s/%s_sim_%d.sp" % (path, designName, temp)))
                        timediff.append("{0} {1}".format(temp, round((value.seconds)/60,4)))
                    
                    else:
                        timediff.append("{0} {1}".format(temp, "timeout"))

                    p = sp.Popen(
                        [
                            "python",
                            "result.py",
                            "--tool",
                            "ngspice",
                            "--inputFile",
                            "%s/%s_sim_%d.log" % (path, designName, temp),
                        ],
                        cwd=runDir,
                    )
                    p.wait()


                p = sp.Popen(["python", "result_error.py", "--mode", "partial"], cwd=runDir)
                p.wait()

                if os.path.isfile(runDir+"/all_result"):
                    
                    os.system("cp all_result ../{0}_sim_result".format(j))

                    # add calculated time differences to a file
                    with open("../{0}_timeStamps".format(j), "w+") as times:
                        for k in timediff:
                            print(k, file=times)

                else:
                    print(runDir+"/all_result not generated for "+j+"_inv"+inverter+"_header"+header)

