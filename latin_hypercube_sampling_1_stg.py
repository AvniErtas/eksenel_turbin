import numpy as np
from scipy.stats import qmc
import json

# Parametrelerin Aralıklarının Belirlenmesi

param_bounds = {
    "vax_12" : (1.0,2.5),
    "vax_23" : (1.0,2.5),
    "vax_34" : (1.0,2.5),
    "vax_34" : (1.0,2.5),
    "rm12" : (0.9,1.1),
    "rm23" : (0.9,1.1),
    "rm34" : (0.9,1.1),
    "ngv_exit_angle" : (60,80)
}

# Sabit parametreler
fixed_params = {
    "M1": 0.13,
    "ngv_stagger": 40,
    "rotor_stagger": 35,
    "asp_2": 2,
    "asp_4": 2
}

# Üretilmek istenen veri sayısı
n_samples = 10

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
file_path = 'Axial_Turbine/data/latin_hypercube_samples.json'

with open(file_path,"w") as f:
    json.dump(json_output,f,indent=4)

print(f"JSON dosyası başarıyla '{file_path} olarak kaydedildi.")
