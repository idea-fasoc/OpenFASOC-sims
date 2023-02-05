#!/bin/python3

import os, csv

Direc=os.getcwd()+"/"
items=os.listdir(Direc)
folders = [f for f in items if not os.path.isfile(Direc+f)]
values=[]
result=[]

for i in folders:
    config=i.split("-")
    header=config[0]
    inverter=config[2]

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
        print("Error - found no drc rpt")

    # open lvs report and look for the line "Final result: Circuits match uniquely.". If found, lvs is clean, else it is failed
    if os.path.exists(Direc+i+"/6_final_drc.rpt"):
        with open(Direc+i+"/6_final_lvs.rpt") as lines:
            data=lines.read()
            if "Final result: Circuits match uniquely." in data:
                lvs="clean"
            else:
                lvs="not clean"
    else:
        print("Error - found not lvs rpt")
    
    # open all folders, get the config, open prePEX_sim_output and extract temp-freq-power-error. 
    if os.path.exists(Direc+i+"/prePEX_sim_result"): 
        with open(Direc+i+"/prePEX_sim_result") as lines:
            for line in lines:
                data=line.split()
                if not "/" in data[0] and (data[0].isdigit() or data[0].startswith("-")):
                    values.append([header,inverter]+data)
    else:
        print("Error - found not sim rpt")
    
    # combine all results in single dictionary
    result.append(values)
    values=[]

# dump results in a csv file
fields=["header","inverter","temp","freq","power","error"]
with open("data.csv","w") as f:
    write = csv.writer(f)

    write.writerow(fields)
    for i in result:
        write.writerows(i)

