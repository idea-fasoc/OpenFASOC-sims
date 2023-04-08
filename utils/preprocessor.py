#!/usr/bin/python
import yaml, os, sys, shutil
from yaml.loader import SafeLoader



class Preprocessor():
     
    def __init__(self):
        self.input_file = 'inputs.yml'
        # generators_path = os.getenv("GITHUB_WORKSPACE")+"/openfasoc/OpenFASOC/openfasoc/generators/"

    def temp_sense_regression_script(self, inputs):

        script_temp = open("run_regression_template_temp-sense","r")
        script = open("run_regression_temp-sense.sh", "w")

        for line in script_temp.readlines():

            # inputs[0] is for headers
            # inputs[1] is for inverters
            if "for h" in line:

                # for h in {%start..%stop..%step}
                start, stop, step = list(inputs[0].values())[0].split(", ")
                line = line.replace("start..stop..step", start+".."+stop+".."+step)
                print(line, file=script, end="")

            elif "for i" in line:

                # for i in {%start..%stop..%step}
                start, stop, step = list(inputs[1].values())[0].split(", ")
                line = line.replace("start..stop..step", start+".."+stop+".."+step)
                print(line, file=script, end="")

            else:
                print(line, file=script, end="")
        
    def ldo_regression_script(self, inputs):

        script_temp = open("run_regression_template_ldo","r")
        script = open("run_regression_ldo.sh", "w")

        for line in script_temp.readlines():

            # inputs[0] is for VoltsOut
            # inputs[1] is for AmpsMax
            if "for b" in line:

                # for h in {%start..%stop..%step}
                start, stop, step = list(inputs[0].values())[0].split(", ")
                line = line.replace("start step stop", start+" "+stop+" "+step)
                print(line, file=script, end="")

            elif "for c" in line:

                # for i in {%start..%stop..%step}
                start, stop, step = list(inputs[1].values())[0].split(", ")
                line = line.replace("start step stop", start+" "+stop+" "+step)
                print(line, file=script, end="")

            else:
                print(line, file=script, end="")
        

pp = Preprocessor()

# Open the file and load the file
with open(pp.input_file) as f:
    data = yaml.load(f, Loader=SafeLoader)

    # check for the generator name definition inside the inputs.yml file and its existance under the repository OpenFASOC
    try:
        generator_name = list(data.keys())[0]
        # if os.path.exists(generators_path+generator_name):
        #     print("generator exists")
        # else:
        #     print("generator name is invalid.")
    except:
        print("Generator name not defined. The first item should be the name of the generator.")
        sys.exit(1)

    # check for the technology definition inside the inputs.yml file
    try:
        technology = data[generator_name][0]
    except:
        print("Technology information missing.")
        sys.exit(1)

    # check for the input params definition inside the inputs.yml file
    try:
        inputs_data = data[generator_name][1]["inputs"]
    except:
        print("Inputs information missing.")
        sys.exit(1)

    # build the regression scripts for provided input combinations and their respective ranges.
    if generator_name == "temp-sense-gen":
        pp.temp_sense_regression_script(inputs_data)

    elif generator_name == "ldo-gen":
        pp.ldo_regression_script(inputs_data)
    
