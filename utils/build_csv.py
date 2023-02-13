#!/bin/python3

import os, csv

Direc=os.getcwd()+"/"
items=os.listdir(Direc)
folders = [f for f in items if not os.path.isfile(Direc+f)]
values=[]
result_pre=[]
result_post=[]

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
        print("Error - found no drc rpt for "+i+" config")

    # open lvs report and look for the line "Final result: Circuits match uniquely.". If found, lvs is clean, else it is failed
    if os.path.exists(Direc+i+"/6_final_drc.rpt"):
        with open(Direc+i+"/6_final_lvs.rpt") as lines:
            data=lines.read()
            if "Final result: Circuits match uniquely." in data:
                lvs="clean"
            else:
                lvs="not clean"
    else:
        print("Error - found not lvs rpt for "+i+" config")
    
    # open prePEX_sim_output and extract temp-freq-power-error. 
    if os.path.exists(Direc+i+"/prePEX_sim_result") and os.path.exists(Direc+i+"/prePEX_timeStamps"): 
        lines = open(Direc+i+"/prePEX_sim_result")
        times = open(Direc+i+"/prePEX_timeStamps")
        for line1 in lines:
            data=line1.split()
            if not "/" in data[0] and (data[0].isdigit() or data[0].startswith("-") or "." in data[0]):
                values.append([header,inverter]+data)

        a = 0
        for line2 in times.readlines():
            time_value = line2.split(" ")
            print(values[a])
            print(time_value[len(time_value)-1])
            values[a].append(time_value[len(time_value)-1].strip())
            print(values[a])
            a += 1

    else:
        print("Error - found not sim rpt for "+i+" config")
    
    # combine all results in single dictionary
    print(values)
    result_pre.append(values)
    values=[]

    # open postPEX_sim_output and extract temp-freq-power-error. 
    # if os.path.exists(Direc+i+"/PEX_sim_result") and os.path.exists(Direc+i+"/PEX_timeStamps"):
    #     with open(Direc+i+"/PEX_sim_result") as lines:
    #         for line in lines:
    #             data=line.split()
    #             if not "/" in data[0] and (data[0].isdigit() or data[0].startswith("-") or "." in data[0]):
    #                 values.append([header,inverter]+data)

    if os.path.exists(Direc+i+"/PEX_sim_result") and os.path.exists(Direc+i+"/PEX_timeStamps"): 
        lines = open(Direc+i+"/PEX_sim_result")
        times = open(Direc+i+"/PEX_timeStamps")
        for line1 in lines:
            data=line1.split()
            if not "/" in data[0] and (data[0].isdigit() or data[0].startswith("-") or "." in data[0]):
                values.append([header,inverter]+data)

        a = 0
        for line2 in times.readlines():
            time_value = line2.split(" ")
            print(values[a])
            print(time_value[len(time_value)-1])
            values[a].append(time_value[len(time_value)-1].strip())
            print(values[a])
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
