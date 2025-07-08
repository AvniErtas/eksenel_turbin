import math as mt 
import solver
import json 
import time


start_time = time.time()

def read_inputs_from_json(filename):
    with open(filename,"r",encoding="utf-8") as file:
        inputs = json.load(file)
    return inputs

def calculate_for_sample(sample_inputs,cycle_inputs,designer_inputs):
    t01 = cycle_inputs["t01"]
    p01 = cycle_inputs["p01"]
    mfr = cycle_inputs["mfr"]
    power = cycle_inputs["power"]
    vax_12 = sample_inputs["vax_12"]
    vax_23 = sample_inputs["vax_23"]
    vax_34 = sample_inputs["vax_34"]
    rm12 = sample_inputs["rm12"]
    rm23 = sample_inputs["rm23"]
    rm34 = sample_inputs["rm34"]
    M1 = sample_inputs["M1"]
    ngv_exit_angle = sample_inputs["ngv_exit_angle"]
    rmean = designer_inputs["rmean"]
    swirl = designer_inputs["swirl"]
    rpm = designer_inputs["rpm"]
    choking = designer_inputs["choking"]
    clearance = designer_inputs["clearance"]
    asp_2 = sample_inputs["asp_2"]
    asp_4 = sample_inputs["asp_4"]
    ngv_stagger = sample_inputs["ngv_stagger"]
    rotor_stagger = sample_inputs["rotor_stagger"]
    ngv_1_zweifel = sample_inputs["ngv_1_zweifel"]
    rotor_1_zweifel = sample_inputs["rotor_1_zweifel"]
    nozl_init = 0.05
    rotl_init = 0.05
    nozl_err = 100
    rotl_err = 100
    iteration =0
    outputs = {}

    while (nozl_err >0.001 or rotl_err> 0.001) and iteration<500:
        outputs = solver.meanline_calculator(
            t01=t01,
            p01=p01,
            mfr =mfr,
            power =power,
            vax_12=vax_12,
            vax_23=vax_23,
            vax_34=vax_34,
            rm12=rm12,
            rm23=rm23,
            rm34=rm34,
            M1=M1,
            ngv_exit_angle=ngv_exit_angle,
            rmean=rmean,
            swirl=swirl,
            rpm=rpm,
            choking=choking,
            clearance=clearance,
            asp_2 = asp_2,
            asp_4 = asp_4,
            nozl= nozl_init,
            rotl= rotl_init,
            ngv_stagger= ngv_stagger,
            rotor_stagger= rotor_stagger,
            ngv_1_zweifel=ngv_1_zweifel,
            rotor_1_zweifel=rotor_1_zweifel
        )
        
        new_nozl = outputs["nozl"]
        new_rotl = outputs["rotl"]
        nozl_err = mt.fabs(((new_nozl-nozl_init)/(new_nozl))*100)
        rotl_err = mt.fabs(((new_rotl-rotl_init)/(new_rotl))*100)
        nozl_init = new_nozl
        rotl_init = new_rotl
        iteration+=1
        print(iteration)
        print("nozl_err:",nozl_err)
        print("rotl_err:",rotl_err)
        
    return outputs

iteration = 0 #! Çözüm bitti iterasyon sıfırlandı

cycle_inputs = read_inputs_from_json(r"Axial_Turbine/data/cycle_inputs.json")
designer_inputs = read_inputs_from_json(r"Axial_Turbine/data/designer_inputs.json")
samplings = read_inputs_from_json(r"Axial_Turbine/data/samplings.json")

all_outputs = []

for sample_inputs in samplings:
    outputs = calculate_for_sample(sample_inputs,cycle_inputs,designer_inputs)
    all_outputs.append(outputs)
    
with open("Axial_Turbine/data/all_outputs.json","w",encoding="utf-8" ) as file:
    json.dump(all_outputs,file)

print("iteration:",iteration)
if(iteration ==0):
    
    end_time = time.time()

    elapsed_time = end_time-start_time

    print("Kodun Çalışma Süresi:",elapsed_time," saniye")

import flowpath

flowpath.draw_flowpath_with_x_blades_1stg(outputs)