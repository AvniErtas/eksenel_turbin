import pygad
import numpy as np
import solver
import json
import flowpath as fp

# Sabit inputlar
cycle_inputs = json.load(open(r"Axial_Turbine/data/cycle_inputs.json", "r", encoding="utf-8"))
designer_inputs = json.load(open(r"Axial_Turbine/data/designer_inputs.json", "r", encoding="utf-8"))

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

def calculate_for_sample(sample_inputs):
    # Burada mevcut fonksiyonunuzu doğrudan kullanabilirsiniz, nozl ve rotl iterasyonlarını da yapar
    # Basitleştirmek için aynı kodu burada tekrarladım, gerektiğinde fonksiyonlaştırabilirsiniz
    t01 = cycle_inputs["t01"]
    p01 = cycle_inputs["p01"]
    mfr = cycle_inputs["mfr"]
    power = cycle_inputs["power"]
    rmean = designer_inputs["rmean"]
    swirl = designer_inputs["swirl"]
    rpm = designer_inputs["rpm"]
    choking = designer_inputs["choking"]
    clearance = designer_inputs["clearance"]

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
            vax_12=sample_inputs["vax_12"],
            vax_23=sample_inputs["vax_23"],
            vax_34=sample_inputs["vax_34"],
            rm12=sample_inputs["rm12"],
            rm23=sample_inputs["rm23"],
            rm34=sample_inputs["rm34"],
            M1=sample_inputs["M1"],
            ngv_exit_angle=sample_inputs["ngv_exit_angle"],
            rmean=rmean,
            swirl=swirl,
            rpm=rpm,
            choking=choking,
            clearance=clearance,
            asp_2=sample_inputs["asp_2"],
            asp_4=sample_inputs["asp_4"],
            nozl=nozl_init,
            rotl=rotl_init,
            ngv_stagger=sample_inputs["ngv_stagger"],
            rotor_stagger=sample_inputs["rotor_stagger"],
            ngv_1_zweifel=sample_inputs["ngv_1_zweifel"],
            rotor_1_zweifel = sample_inputs["rotor_1_zweifel"]
        )

        new_nozl = outputs["nozl"]
        new_rotl = outputs["rotl"]
        nozl_err = abs((new_nozl - nozl_init) / new_nozl) * 100
        rotl_err = abs((new_rotl - rotl_init) / new_rotl) * 100
        nozl_init = new_nozl
        rotl_init = new_rotl
        iteration += 1

    return outputs

# Parametre aralıkları
param_bounds = {
    "vax_12": (0.9, 2.5),
    "vax_23": (0.9, 2.5),
    "vax_34": (0.9, 2.5),
    "rm12": (0.9, 1.1),
    "rm23": (0.9, 1.1),
    "rm34": (0.9, 1.1),
    "ngv_exit_angle": (60, 80),
}

# Popülasyondaki kromozom uzunluğu
num_genes = len(param_bounds)

# Bounds dizisini kromozoma göre ayarlayalım
gene_space = [{"low": bounds[0], "high": bounds[1]} for bounds in param_bounds.values()]

def fitness_func(ga_instance, solution, solution_idx):
    sample_inputs = {
        "vax_12": solution[0],
        "vax_23": solution[1],
        "vax_34": solution[2],
        "rm12": solution[3],
        "rm23": solution[4],
        "rm34": solution[5],
        "ngv_exit_angle": solution[6],
    }
    sample_inputs.update(fixed_params)

    outputs = calculate_for_sample(sample_inputs)

    # Kısıtlar: ceza yöntemiyle fitness'ı düşürelim
    penalty = 0
    if not (0.6 <= outputs["flow_coef"] <= 0.9):
        penalty += 100 * abs(outputs["flow_coef"] - 0.75)
    if not (1.1 <= outputs["work_coef"] <= 1.9):
        penalty += 100 * abs(outputs["work_coef"] - 1.5)
    if not (0.3 <= outputs["reaction"] <= 0.5):
        penalty += 100 * abs(outputs["reaction"] - 0.4)
    if outputs["exit_swirl"] >= 20:
        penalty += 100 * (outputs["exit_swirl"] - 20)
    if not (2.7 <= outputs["pratio"] <= 3):
        penalty += 100 * abs(outputs["pratio"] - 2.85)
    if outputs["noz_fang_hub"] >= 20:
        penalty += 100 * (outputs["noz_fang_hub"] - 20)
    if outputs["rot_fang_hub"] >= 20:
        penalty += 100 * (outputs["rot_fang_hub"] - 20)
    if outputs["noz_fang_tip"] >= 20:
        penalty += 100 * (outputs["noz_fang_tip"] - 20)
    if outputs["rot_fang_tip"] > 0:
        penalty += 100 * outputs["rot_fang_tip"]
    if outputs["duct_fang_hub"] >= 20:
        penalty += 100 * (outputs["duct_fang_hub"] - 20)
    if outputs["duct_fang_tip"] >= 20:
        penalty += 100 * (outputs["duct_fang_tip"] - 20)
    if outputs["rotor_turning"] >= 120:
        penalty += 100 * (outputs["rotor_turning"] - 120)
    if outputs["an2_max"] >= 5:
        penalty += 100 * (outputs["an2_max"] - 5)

    fitness = outputs["efficiency"] - penalty

        
    return fitness

ga_instance = pygad.GA(
    num_generations=1000,
    num_parents_mating=10,
    fitness_func=fitness_func,
    sol_per_pop=50,
    num_genes=num_genes,
    gene_space=gene_space,
    parent_selection_type="sss",
    crossover_type="single_point",
    mutation_type="random",
    mutation_percent_genes=10,
    save_solutions=False
)

ga_instance.run()

solution, solution_fitness, _ = ga_instance.best_solution()

print("En iyi çözüm parametreleri:", solution)



# En iyi çözüme ait sample_inputs oluştur
best_inputs = {
    "vax_12": solution[0],
    "vax_23": solution[1],
    "vax_34": solution[2],
    "rm12": solution[3],
    "rm23": solution[4],
    "rm34": solution[5],
    "ngv_exit_angle": solution[6],
}
best_inputs.update(fixed_params)

# Bu noktada outputs artık global tanımlı olur
outputs = calculate_for_sample(best_inputs)

print(outputs["efficiency"])

print("sonuçlar:")
for key, value in outputs.items():
    print(f"{key}: {value:.4f}")

# Şimdi çizim fonksiyonunu çağır
fp.draw_flowpath_with_x_blades_1stg(outputs)