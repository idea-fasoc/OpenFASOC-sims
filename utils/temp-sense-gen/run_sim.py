#!/bin/python3

import subprocess as sp
import os
import fileinput

# get the list of all folders inside /home/runner_results/


designName = "tempsenseInst_error"
temp_list=[-20, 0, 20, 40, 60, 80, 100]
processes=[]

rootDir = "/home/"+os.getenv("USER")+"/runner_results"
for i in os.listdir(rootDir):

    # i is the path of the directory - eg: /home/alex/runner_archives/5-head-10-inv
    if os.path.isdir(i):

        config=i.split("-")
        header=config[0]
        inverter=config[2]
 
         # look for directory name starting with PEX and prePEX and build path to ammend to the filename.
        for j in ["prePEX", "PEX"]:
            path = rootDir+"/"+i+"/"+j+"_inv"+inverter+"_header"+header
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

for p in processes:
    p.wait()