#!/bin/python3

import subprocess as sp
import os, datetime, math

# get the list of all folders inside /home/runner_results/


designName = "tempsenseInst_error"
temp_list=[0, 20, 40, 60, 80, 100]
processes=[]

rootDir = "/home/"+os.getenv("USER")+"/runner_test_results"
for i in os.listdir(rootDir):

    # i is the path of the directory - eg: /home/alex/runner_archives/5-head-10-inv
    if os.path.isdir(rootDir+"/"+i):
        

        config=i.split("-")
        header=config[0]
        inverter=config[2]
 
        # look for directory name starting with PEX and prePEX and build path to ammend to the filename.
        for j in ["prePEX", "PEX"]:
            path = rootDir+"/"+i+"/"+j+"_inv"+inverter+"_header"+header
            runDir = path
            os.chdir(path)
            timediff = []

            for temp in temp_list:
                
                # get the time diff between the last modifications of .sp file and .log file
                value = datetime.datetime.fromtimestamp(os.path.getmtime("%s/%s_sim_%d.log" % (path, designName, temp))) - datetime.datetime.fromtimestamp(os.path.getmtime("%s/%s_sim_%d.sp" % (path, designName, temp)))
                timediff.append("{0} {1}".format(temp, round((value.seconds)/60,4)))

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