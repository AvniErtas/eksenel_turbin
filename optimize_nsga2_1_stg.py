import json
import numpy as np
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.termination import get_termination
from pymoo.optimize import minimize
from pymoo.core.callback import Callback
import solver

# --- Girdileri Yükle ---
cycle_inputs = json.load(open("Axial_Turbine/data/cycle_inputs.json", "r", encoding="utf-8"))
designer_inputs = json.load(open("Axial_Turbine/data/designer_inputs.json", "r", encoding="utf-8"))

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

# Optimize edilecek parametre aralıkları
param_bounds = {
    "vax_12": (0.9, 2.5),
    "vax_23": (0.9, 2.5),
    "vax_34": (0.9, 2.5),
    "rm12": (0.9, 1.1),
    "rm23": (0.9, 1.1),
    "rm34": (0.9, 1.1),
    "ngv_exit_angle": (60, 80),
}
param_names = list(param_bounds.keys())
lower_bounds = [param_bounds[k][0] for k in param_names]
upper_bounds = [param_bounds[k][1] for k in param_names]

# --- Hesaplama Fonksiyonu ---
def calculate_for_sample(sample_inputs):
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
            rotor_1_zweifel=sample_inputs["rotor_1_zweifel"],
        )

        new_nozl = outputs["nozl"]
        new_rotl = outputs["rotl"]
        nozl_err = abs((new_nozl - nozl_init) / new_nozl) * 100
        rotl_err = abs((new_rotl - rotl_init) / new_rotl) * 100
        nozl_init = new_nozl
        rotl_init = new_rotl
        iteration += 1

    return outputs

# --- Problem Tanımı ---
class TurbineOptimizationProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=len(param_bounds),
            n_obj=1,  # Tek amaç
            n_constr=17,
            xl=np.array(lower_bounds),
            xu=np.array(upper_bounds)
        )

    def _evaluate(self, X, out, *args, **kwargs):
        F1 = []
        G = []

        for row in X:
            sample = dict(zip(param_names, row))
            # Sabit parametreleri de ekle
            sample.update(fixed_params)

            try:
                r = calculate_for_sample(sample)

                # Amaç fonksiyonu (verimliliği maksimize etmek için negatif alıyoruz)
                F1.append(-r["efficiency"])

                # Kısıtlar (her biri ≤ 0 olmalı)
                g = [
                    r["flow_coef"] - 0.9,
                    0.6 - r["flow_coef"],
                    r["work_coef"] - 1.9,
                    1.1 - r["work_coef"],
                    r["reaction"] - 0.5,
                    0.3 - r["reaction"],
                    r["exit_swirl"] - 20,
                    r["pratio"] - 3.0,
                    2.7 - r["pratio"],
                    r["noz_fang_hub"] - 20,
                    r["rot_fang_hub"] - 20,
                    r["noz_fang_tip"] - 20,
                    r["rot_fang_tip"] - 0, #? 0 çözmüyor
                    r["duct_fang_hub"] - 20,
                    r["duct_fang_tip"] - 20,
                    r["rotor_turning"] - 120,
                    r["an2_max"] - 5,
                ]
                G.append(g)

            except Exception as e:
                print("Hata örneği:", e)
                F1.append(1e6)       # Büyük ceza değeri
                G.append([1e3] * 17) # Kısıt ceza değerleri

        out["F"] = np.column_stack([F1])
        out["G"] = np.array(G)

# --- Callback ---
class PrintCallback(Callback):
    def __init__(self):
        super().__init__()
        self.gen = 0

    def notify(self, algorithm):
        self.gen += 1
        print(f"Generation: {self.gen}")

# --- Algoritmayı Çalıştır ---
algorithm = NSGA2(pop_size=50)
termination = get_termination("n_gen", 50)

res = minimize(
    TurbineOptimizationProblem(),
    algorithm,
    termination,
    seed=1,
    callback=PrintCallback(),
    save_history=True,
    verbose=True,
)

print("\nOptimum çözümler:")
sol = res.X          # Tek bir çözüm (7 parametre)
f = res.F[0]         # Tek fitness değeri (1 obje)
print(f"Girdi: {dict(zip(param_names, sol))} → Efficiency: {-f:.4f}")


import flowpath

sample = dict(zip(param_names, sol))
sample.update(fixed_params)
output = calculate_for_sample(sample)
print("\nÇıktılar:")
for key, value in output.items():
    print(f"{key}: {value:.4f}")
flowpath.draw_flowpath_with_x_blades_1stg(output)
