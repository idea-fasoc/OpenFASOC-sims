import yaml, sys, subprocess, os, csv
import numpy as np
from generators_checks import *



def read_config(config_file):
    '''
    Read configuration file for input sweep range
    '''
    
    from yaml.loader import SafeLoader

    with open(config_file) as f:
        data = yaml.load(f, Loader=SafeLoader)
        return data



def tempSense(data, stage):
    '''
    Run the regression for temp-sense generator. The flow is divided into 4 stages - 
    1. generate - to run the generator for the entire input sweep range given in the config file and generate gds, verilog, reports and spice netlists for further processing
    2. simulate - to run the simulations using the existing testbenches and generate logfiles for further processing.
    3. process - to process the earlier generated logfiles and extract required parameter results from it.
    4. build - to build the dataset using the earlier extracted results
    '''

    designName = data["designName"]
    ninv = data["ninv"]
    nhead = data["nhead"]

    reg = run_checks_tempsense.regression_tempsense()

    # generate spice netlists for simulations
    if stage == "generate":
        for i in range(ninv[0], ninv[1], ninv[2]):
            for j in range(nhead[0], nhead[1], nhead[2]):

                if reg.run_generator(ninv=i, nhead=j):
                    print("Generator run failed")
                    sys.exit(1)
                else:
                    print("generator run successeded. processing further...")


                if reg.checkLVS():
                    print("Found LVS errors")
                    sys.exit(1)
                else:
                    print("LVS is clean. processing further...")


                if reg.checkDRC():
                    print("Found DRC errors")
                    sys.exit(1)
                else:
                    print("DRC is clean. processing further...")


                if reg.copyData(ninv=i, nhead=j):
                    print("Failed to copy data to runner_results directory")
                    sys.exit(1)
                else:
                    print("Copied successfully to runner_results directory. processing further...")


    # idea is to build the total combinations list and split them by 2. Run simulations on each half.
    # TODO: Create new runner machines, share the above built data with them and run each half of the simulation on each machine. After ending, get back the data to the master machine and do the postprocess
    if stage == "simulate":

        combs = []
        for i in range(ninv[0], ninv[1], ninv[2]):
            for j in range(nhead[0], nhead[1], nhead[2]):
                combs.append([i,j])
        
        # TODO: Compare the len of combos with the number of threads on the runner machine. If exceeds, then split the list of combos by 2, create a new runner machine and launch the other half of simulations on other machine.

        # processes = reg.runSimulations(nhead=7, ninv=8)
        # for p in processes:
        #     p.wait()


    # process simulation logfiles and generate final data
    if stage == "process":    
        reg.processSims(nhead=7, ninv=8)


    # build the final csv file (or push everthing to the database hosted on GCP?)
    if stage == "build":

        # Direc=os.getcwd()+"/"
        Direc = "/home/"+os.getenv("USER")+"/runner_results/"
        items = os.listdir(Direc)
        folders = [f for f in items if not os.path.isfile(Direc+f)]
        values = []
        result_pre = []
        result_post = []

        for i in folders:
            config = i.split("-")
            header = config[0]
            inverter = config[2]

            # open drc report and look whether the count is blank or not - apparently the first line of the drc report should end with " " for the drc errors to be 0
            if os.path.exists(Direc+i+"/6_final_drc.rpt"):
                with open(Direc+i+"/6_final_drc.rpt") as lines:
                    for line in lines:
                        if "count: " in line:
                            drc="clean"
                        else:
                            drc="not clean"
                        break
            else:
                print("Error - found no drc rpt for "+i+" config")

            # open lvs report and look for the line "Final result: Circuits match uniquely.". If found, lvs is clean, else it is failed
            if os.path.exists(Direc+i+"/6_final_drc.rpt"):
                with open(Direc+i+"/6_final_lvs.rpt") as lines:
                    data = lines.read()
                    if "Final result: Circuits match uniquely." in data:
                        lvs = "clean"
                    else:
                        lvs = "not clean"
            else:
                print("Error - found not lvs rpt for "+i+" config")
            
            # open prePEX_sim_output and extract temp-freq-power-error. 
            if os.path.exists(Direc+i+"/prePEX_sim_result") and os.path.exists(Direc+i+"/prePEX_timeStamps"): 
                lines = open(Direc+i+"/prePEX_sim_result")
                times = open(Direc+i+"/prePEX_timeStamps")
                for line1 in lines:
                    data = line1.split()
                    if not "/" in data[0] and (data[0].isdigit() or data[0].startswith("-") or "." in data[0]):
                        values.append([header,inverter]+data)

                a = 0
                for line2 in times.readlines():
                    time_value = line2.split(" ")
                    values[a].append(time_value[len(time_value)-1].strip())
                    a += 1

            else:
                print("Error - found not sim rpt for "+i+" config")
            
            # combine all results in single dictionary
            result_pre.append(values)
            values=[]


            if os.path.exists(Direc+i+"/PEX_sim_result") and os.path.exists(Direc+i+"/PEX_timeStamps"): 
                lines = open(Direc+i+"/PEX_sim_result")
                times = open(Direc+i+"/PEX_timeStamps")
                for line1 in lines:
                    data = line1.split()
                    if not "/" in data[0] and (data[0].isdigit() or data[0].startswith("-") or "." in data[0]):
                        values.append([header,inverter]+data)

                a = 0
                for line2 in times.readlines():
                    time_value = line2.split(" ")
                    values[a].append(time_value[len(time_value)-1].strip())
                    a += 1
            else:
                print("Error - found not sim rpt for "+i+" config")

            # combine all results in single dictionary
            result_post.append(values)
            values=[]



        # dump results in a csv file
        fields=["header","inverter","temp","freq","power","error","run_time"]
        with open("data_prePEX.csv","w") as f:
            write = csv.writer(f)

            write.writerow(fields)
            for i in result_pre:
                write.writerows(i)

        with open("data_postPEX.csv","w") as f:
            write = csv.writer(f)

            write.writerow(fields)
            for i in result_post:
                write.writerows(i)



def ldo(data, stage):
    '''
    Run the regression for ldo generator. The flow is divided into 4 stages - 
    1. generate - to run the generator for the entire input sweep range given in the config file and generate gds, verilog, reports and spice netlists for further processing
    2. simulate - to run the simulations using the existing testbenches and generate logfiles for further processing.
    3. process - to process the earlier generated logfiles and extract required parameter results from it.
    4. build - to build the dataset using the earlier extracted results
    '''

    designName = data["designName"]
    vin = data["vin"]
    imax = data["imax"]

    reg = run_checks_ldo.regression_ldo()

    # generate spice netlists for simulations
    if stage == "generate":
        for i in np.arange(vin[0], vin[1], vin[2]):
            for j in np.arange(imax[0], imax[1], imax[2]):

                if reg.run_generator(vin=i, imax=j):
                    print("Generator run failed")
                    sys.exit(1)
                else:
                    print("generator run successeded. processing further...")


                if reg.checkLVS():
                    print("Found LVS errors")
                    sys.exit(1)
                else:
                    print("LVS is clean. processing further...")


                if reg.checkDRC():
                    print("Found DRC errors")
                    print("Exception for LDO generator found. processing further...")
                else:
                    print("DRC is clean. processing further...")


                if reg.copyData(vin=i, imax=j):
                    print("Failed to copy data to runner_results directory")
                    sys.exit(1)
                else:
                    print("Copied successfully to runner_results directory. processing further...")



    # idea is to build the total combinations list and split them by 2. Run simulations on each half.
    # TODO: Create new runner machines, share the above built data with them and run each half of the simulation on each machine. After ending, get back the data to the master machine and do the postprocess
    if stage == "simulate":
        processes = reg.runSimulations(vin=1.8, imax=1.0)
        for p in processes:
            p.wait()



    # process simulation logfiles and generate final data
    if stage == "process":    
        reg.processSims(vin=1.8, imax=1)




#--------------
# Main section
#--------------

configuration="configs/config_"+sys.argv[1]+".yml"

if os.path.exists(configuration):
    data = read_config(config_file=configuration)

else:
    print("Given configuration file doesn't exists.")
    print(read_config.__doc__)
    sys.exit(1)

if len(sys.argv) > 1:

    if sys.argv[1] == "tempsense":
        tempSense(data, sys.argv[2])

    elif sys.argv[1] == "ldo":
        ldo(data, sys.argv[2])

else:
    print("Missing generator name and stage name")
    sys.exit(1)
        








