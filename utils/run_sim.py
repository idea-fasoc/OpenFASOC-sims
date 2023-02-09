#!/bin/python

import subprocess as sp
import os

# get the list of all folders inside /home/runner_results/


designName = "tempsenseInst_error"
temp_list=[0,20, 40, 60, 80, 100]
processes=[]

for i in directories:
    # i is the path of the directory - eg: /home/alex/runner_archives/5-head-10-inv
    # look for directory name starting with PEX and prePEX
    # build path to ammend to the filename.
    path = ""
    runDir = path
    for temp in temp_list:
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