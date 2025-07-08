import math as mt
import solver
import json
import time
from scipy.optimize import minimize

start_time = time.time()

def read_inputs_from_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        inputs = json.load(file)
    return inputs

def calculate_for_sample(sample_inputs, cycle_inputs, designer_inputs):
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
    iteration = 0
    outputs = {}

    while (nozl_err > 0.001 or rotl_err > 0.001) and iteration < 500:
        outputs = solver.meanline_calculator(
            t01=t01,
            p01=p01,
            mfr=mfr,
            power=power,
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
            asp_2=asp_2,
            asp_4=asp_4,
            nozl=nozl_init,
            rotl=rotl_init,
            ngv_stagger=ngv_stagger,
            rotor_stagger=rotor_stagger,
            ngv_1_zweifel=ngv_1_zweifel,
            rotor_1_zweifel=rotor_1_zweifel
        )

        new_nozl = outputs["nozl"]
        new_rotl = outputs["rotl"]
        nozl_err = mt.fabs(((new_nozl - nozl_init) / new_nozl) * 100)
        rotl_err = mt.fabs(((new_rotl - rotl_init) / new_rotl) * 100)
        nozl_init = new_nozl
        rotl_init = new_rotl
        iteration += 1

    return outputs


# Sabit parametreler
fixed_params = {
    "ngv_stagger": 40,
    "rotor_stagger": 35,
    "asp_2": 2,
    "asp_4": 2,
    "M1": 0.1,
    "ngv_1_zweifel": 0.8,
    "rotor_1_zweifel": 0.8,
}

# Sabit cycle ve designer inputları oku
cycle_inputs = read_inputs_from_json(r"Axial_Turbine/data/cycle_inputs.json")
designer_inputs = read_inputs_from_json(r"Axial_Turbine/data/designer_inputs.json")

# Optimize edilecek parametreler için sınırlar
bounds = [
    (0.9, 2.5),  # vax_12
    (0.9, 2.5),  # vax_23
    (0.9, 2.5),  # vax_34
    (0.9, 1.1),  # rm12
    (0.9, 1.1),  # rm23
    (0.9, 1.1),  # rm34
    (60, 80),    # ngv_exit_angle
]

# x parametrelerini sample_inputs dict'ine map eden fonksiyon
def map_sample_inputs(x):
    return {
        "vax_12": x[0],
        "vax_23": x[1],
        "vax_34": x[2],
        "rm12": x[3],
        "rm23": x[4],
        "rm34": x[5],
        "ngv_exit_angle": x[6],
        "M1": fixed_params["M1"],
        "ngv_stagger": fixed_params["ngv_stagger"],
        "rotor_stagger": fixed_params["rotor_stagger"],
        "asp_2": fixed_params["asp_2"],
        "asp_4": fixed_params["asp_4"],
        "ngv_1_zweifel": fixed_params["ngv_1_zweifel"],
        "rotor_1_zweifel": fixed_params["rotor_1_zweifel"],
    }

# Objective function (maksimize etmek için negatif efficiency döndür)
def objective(x):
    sample_inputs = map_sample_inputs(x)
    outputs = calculate_for_sample(sample_inputs, cycle_inputs, designer_inputs)
    return -outputs["efficiency"]

# Constraint fonksiyonu üreten yardımcı metod
def make_constraint_function(name, mode, limit):
    def constraint(x):
        sample_inputs = map_sample_inputs(x)
        outputs = calculate_for_sample(sample_inputs, cycle_inputs, designer_inputs)
        value = outputs[name]
        if mode == 'min':
            return value - limit
        elif mode == 'max':
            return limit - value
    return constraint


# Başlangıç noktası
x0 = [1.8, 1.0, 1.45, 1.0, 1.0, 1.0, 75]

constraint_definitions = [
    # name,      mode,   limit
    ("flow_coef",   "min", 0.6),
    ("flow_coef",   "max", 0.9),
    ("work_coef",   "min", 1.1),
    ("work_coef",   "max", 1.9),
    ("reaction",    "min", 0.3),
    ("reaction",    "max", 0.5),
    ("exit_swirl",  "max", 20),
    ("pratio",      "min", 2.7),
    ("pratio",      "max", 3),
    ("noz_fang_hub",    "max", 20),
    ("rot_fang_hub",    "max", 20),
    ("noz_fang_tip",    "max", 20),
    ("rot_fang_tip",    "max", 0),   # dikkat: bu constraint negatif dönmeli
    ("duct_fang_hub",   "max", 20),
    ("duct_fang_tip",   "max", 20),
    ("rotor_turning",   "max", 120),
    ("an2_max",         "max", 5),
]

constraints = [
    {"type": "ineq", "fun": make_constraint_function(name, mode, limit)}
    for name, mode, limit in constraint_definitions
]

result = minimize(objective, x0, bounds=bounds, constraints=constraints, method='SLSQP', options={'disp': True, 'maxiter': 100})

print("Optimum parametreler:", result.x)
print("Maksimum efficiency:", -result.fun)

end_time = time.time()
print("Kodun Çalışma Süresi:", end_time - start_time, "saniye")

import flowpath 
# Optimize edilmiş parametreleri map et
opt_sample_inputs = map_sample_inputs(result.x)
print(opt_sample_inputs)
# Optimize edilmiş sonuçları hesapla
opt_outputs = calculate_for_sample(opt_sample_inputs, cycle_inputs, designer_inputs)
print(opt_outputs)
# Akış yolu grafiğini çiz
flowpath.draw_flowpath_with_x_blades_1stg(opt_outputs, save_path="optimum_flowpath.png")



