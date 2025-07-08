import pygad
import numpy as np
import solver_2stg
import json

# Sabit inputlar
cycle_inputs = json.load(open("Axial_Turbine/data/cycle_inputs_2stg.json", "r", encoding="utf-8"))
designer_inputs = json.load(open("Axial_Turbine/data/designer_inputs_2stg.json", "r", encoding="utf-8"))

# Sabit parametreler
fixed_params = {
    "ngv_stagger_1": 40,
    "rotor_stagger_1": 35,
    "ngv_stagger_2": 40,
    "rotor_stagger_2": 35,
    "asp_2": 1.5,
    "asp_4": 2.2,
    "asp_6": 1.5,
    "asp_8": 2.5,
    "M1": 0.25,
    "stg_1_power_ratio": 0.5,
    "ngv_1_zweifel": 0.85,
    "rotor_1_zweifel": 0.9,
    "ngv_2_zweifel": 0.85,
    "rotor_2_zweifel": 0.9,
}

# Parametre aralıkları
param_bounds = {
    "vax_12": (1.0, 2.3), "vax_23": (0.9, 1.05), "vax_34": (0.9, 1.5),
    "vax_45": (0.9, 1.05), "vax_56": (0.9, 1.5), "vax_67": (0.9, 1.05), "vax_78": (0.9, 1.5),
    "rm12": (0.97, 1.03), "rm23": (0.97, 1.03), "rm34": (0.97, 1.03),
    "rm45": (0.97, 1.03), "rm56": (0.97, 1.03), "rm67": (0.97, 1.03), "rm78": (0.97, 1.03),
    "ngv1_exit_angle": (60, 80), "ngv2_exit_angle": (60, 80)
}
gene_space = [{"low": bounds[0], "high": bounds[1]} for bounds in param_bounds.values()]
param_keys = list(param_bounds.keys())

def calculate_for_sample(sample_inputs):
    try:
        t01 = cycle_inputs["t01"]
        p01 = cycle_inputs["p01"]
        mfr = cycle_inputs["mfr"]
        power = cycle_inputs["power"]
        rmean = designer_inputs["rmean"]
        swirl = designer_inputs["swirl"]
        rpm = designer_inputs["rpm"]
        choking_1 = designer_inputs["choking_1"]
        choking_4 = designer_inputs["choking_4"]
        clearance_1 = designer_inputs["clearance_1"]
        clearance_2 = designer_inputs["clearance_2"]

        nozl1 = nozl2 = rotl1 = rotl2 = 0.05
        iteration = 0

        while iteration < 500:
            outputs = solver_2stg.meanline_calculator(
                t01=t01, p01=p01, mfr=mfr, power=power,
                **sample_inputs,
                rmean=rmean, swirl=swirl, rpm=rpm,
                choking_1=choking_1, choking_4=choking_4,
                clearance_1=clearance_1, clearance_2=clearance_2,
                nozl_1=nozl1, rotl_1=rotl1, nozl_2=nozl2, rotl_2=rotl2
            )

            # 🔍 Beklenen minimum anahtarlar var mı kontrol et
            required_keys = ["nozl_1", "rotl_1", "nozl_2", "rotl_2", "efficiency"]
            if not all(k in outputs for k in required_keys):
                return {"efficiency": -9999}  # Eksik çıktı varsa ceza ver

            new_nozl1 = outputs["nozl_1"]
            new_rotl1 = outputs["rotl_1"]
            new_nozl2 = outputs["nozl_2"]
            new_rotl2 = outputs["rotl_2"]

            err = max(
                abs((new_nozl1 - nozl1) / new_nozl1),
                abs((new_rotl1 - rotl1) / new_rotl1),
                abs((new_nozl2 - nozl2) / new_nozl2),
                abs((new_rotl2 - rotl2) / new_rotl2),
            )
            if err < 0.001:
                break

            nozl1, rotl1, nozl2, rotl2 = new_nozl1, new_rotl1, new_nozl2, new_rotl2
            iteration += 1

        return outputs

    except Exception as e:
        return {"efficiency": -9999}  # Hata oluştuysa sadece efficiency dön


def fitness_func(ga_instance, solution, solution_idx):
    sample_inputs = {k: v for k, v in zip(param_keys, solution)}
    sample_inputs.update(fixed_params)

    try:
        outputs = calculate_for_sample(sample_inputs)
        if "error" in outputs:
            return -9999
    except Exception:
        return -9999

    # -------------------------------
    # 🔒 Limitleri açıkça tanımla
    # -------------------------------
    limits = {
        "flow_coef_1": (0.4, 0.9),
        "flow_coef_2": (0.4, 0.9),
        "work_coef_1": (1.1, 1.9),
        "work_coef_2": (1.1, 1.9),
        "reaction_1": (0.3, 0.5),
        "reaction_2": (0.3, 0.5),
        "exit_swirl_2": (None, 20),
        "pratio": (3.0, 3.5),

        # Fan angle ve turning sınırları
        "noz1_fang_hub": (None, 20),
        "rot1_fang_hub": (None, 20),
        "noz2_fang_hub": (None, 20),
        "rot2_fang_hub": (None, 20),
        "noz1_fang_tip": (None, 20),
        "rot1_fang_tip": (None, 20),
        "noz2_fang_tip": (None, 20),
        "rot2_fang_tip": (None, 20),
        "duct1_fang_hub": (None, 5),
        "duct1_fang_tip": (None, 5),
        "duct2_fang_hub": (None, 5),
        "duct2_fang_tip": (None, 5),
        "duct3_fang_hub": (None, 5),
        "duct3_fang_tip": (None, 5),
        "rotor1_turning": (None, 120),
        "rotor2_turning": (None, 120),
        "an2_rls1": (None, 5),
        "an2_rls2": (None, 5)
    }

    # -------------------------------
    # 📉 Ceza Hesabı
    # -------------------------------
    penalty = 0
    for key, (lower, upper) in limits.items():
        val = outputs.get(key, None)
        if val is None:
            penalty += 1000  # bilinmeyen hata/eksik çıktı için sabit ceza
            continue
        if lower is not None and val < lower:
            penalty += 100 * abs(val - lower)
        if upper is not None and val > upper:
            penalty += 100 * abs(val - upper)

    # -------------------------------
    # 🎯 Amaç Fonksiyonu
    # -------------------------------
    efficiency = outputs.get("efficiency", 0)
    fitness = efficiency - penalty
    return fitness


ga_instance = pygad.GA(
    num_generations=2000,
    num_parents_mating=10,
    fitness_func=fitness_func,
    sol_per_pop=20,
    num_genes=len(param_bounds),
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

best_inputs = {k: v for k, v in zip(param_keys, solution)}
best_inputs.update(fixed_params)

best_outputs = calculate_for_sample(best_inputs)

print("En iyi çözüm çıktıları:", best_outputs)

from flowpath import draw_flowpath_with_x_blades_2stg
draw_flowpath_with_x_blades_2stg(best_outputs)
