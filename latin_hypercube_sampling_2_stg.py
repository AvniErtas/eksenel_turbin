
import numpy as np
from scipy.stats import qmc
import json

# Parametrelerin Aralıklarının Belirlenmesi

param_bounds = {
    "vax_12" : (1.0,1.8),
    "vax_23" : (1.0,1.5),
    "vax_34" : (1.0,1.5),
    "vax_45" : (1.0,1.5),
    "vax_56" : (1.0,1.4),
    "vax_67" : (1.0,1.4),
    "vax_78" : (1.0,1.4),
    "rm12" : (0.9,1.1),
    "rm23" : (0.9,1.1),
    "rm34" : (0.9,1.1),
    "rm45" : (0.9,1.1),
    "rm56" : (0.9,1.1),
    "rm67" : (0.9,1.1),
    "rm78" : (0.9,1.1),
    "ngv1_exit_angle" : (60,70),
    "ngv2_exit_angle" : (60,70)
}

# Sabit parametreler
fixed_params = {
    "M1": 0.246,
        "ngv_stagger_1": 49.3,
        "rotor_stagger_1": 41.7,
        "ngv_stagger_2": 41.3,
        "rotor_stagger_2": 34.5,
        "asp_2": 1.5,
        "asp_4": 2.0,
        "asp_6": 1.5,
        "asp_8": 2.0,
        "stg_1_power_ratio": 0.5,
        "ngv_1_zweifel": 0.8,
        "ngv_2_zweifel": 0.8,
        "rotor_1_zweifel": 0.8,
        "rotor_2_zweifel": 0.8,
}

# Üretilmek istenen veri sayısı
n_samples = 10000

# Latin HyperCube Örnekleyicisi oluşturma
sampler = qmc.LatinHypercube(d=len(param_bounds))

# Rastgele Örnekler Üret
lhs_samples = sampler.random(n=n_samples)

# Parametreleri Belirlediğimiz aralıklara göre ölçeklendir
scaled_samples = np.zeros_like(lhs_samples)

for i,(param,(low,high)) in enumerate(param_bounds.items()):
    scaled_samples[:,i] = qmc.scale(lhs_samples[:,i:i+1],low,high).flatten()

# Json formatında çıktı oluştur
json_output = []

for sample in scaled_samples:
    sample_dict = {}
    for i,(param,_) in enumerate(param_bounds.items()):
        sample_dict[param] = sample[i]
    # Sabit parametreleri ekle
    sample_dict.update(fixed_params)
    json_output.append(sample_dict)

# Json çıktısını dosyaya yazalım
file_path = 'Axial_Turbine/data/latin_hypercube_samples_2_stg.json'

with open(file_path,"w") as f:
    json.dump(json_output,f,indent=4)

print(f"JSON dosyası başarıyla '{file_path} olarak kaydedildi.")
