import math as mt
import solver_2stg
import json
import time
import flowpath

start_time = time.time()

# Dosyadan JSON oku
def read_inputs_from_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Her örnek için hesaplama fonksiyonu
def calculate_for_sample(sample_inputs, cycle_inputs, designer_inputs):
    t01 = cycle_inputs["t01"]
    p01 = cycle_inputs["p01"]
    mfr = cycle_inputs["mfr"]
    power = cycle_inputs["power"]

    # Sample inputlardan parametreler
    vax_12 = sample_inputs["vax_12"]
    vax_23 = sample_inputs["vax_23"]
    vax_34 = sample_inputs["vax_34"]
    vax_45 = sample_inputs["vax_45"]
    vax_56 = sample_inputs["vax_56"]
    vax_67 = sample_inputs["vax_67"]
    vax_78 = sample_inputs["vax_78"]

    rm12 = sample_inputs["rm12"]
    rm23 = sample_inputs["rm23"]
    rm34 = sample_inputs["rm34"]
    rm45 = sample_inputs["rm45"]
    rm56 = sample_inputs["rm56"]
    rm67 = sample_inputs["rm67"]
    rm78 = sample_inputs["rm78"]

    M1 = sample_inputs["M1"]
    ngv1_exit_angle = sample_inputs["ngv1_exit_angle"]
    ngv2_exit_angle = sample_inputs["ngv2_exit_angle"]

    rmean = designer_inputs["rmean"]
    swirl = designer_inputs["swirl"]
    rpm = designer_inputs["rpm"]

    choking_1 = designer_inputs["choking_1"]
    choking_4 = designer_inputs["choking_4"]
    clearance_1 = designer_inputs["clearance_1"]
    clearance_2 = designer_inputs["clearance_2"]

    asp_2 = sample_inputs["asp_2"]
    asp_4 = sample_inputs["asp_4"]
    asp_6 = sample_inputs["asp_6"]
    asp_8 = sample_inputs["asp_8"]

    ngv_stagger_1 = sample_inputs["ngv_stagger_1"]
    rotor_stagger_1 = sample_inputs["rotor_stagger_1"]
    ngv_stagger_2 = sample_inputs["ngv_stagger_2"]
    rotor_stagger_2 = sample_inputs["rotor_stagger_2"]

    ngv_1_zweifel = sample_inputs["ngv_1_zweifel"]
    ngv_2_zweifel = sample_inputs["ngv_2_zweifel"]
    rotor_1_zweifel = sample_inputs["rotor_1_zweifel"]
    rotor_2_zweifel = sample_inputs["rotor_2_zweifel"]
    
    stg_1_power_ratio = sample_inputs["stg_1_power_ratio"]

    nozl1_init = nozl2_init = 0.05
    rotl1_init = rotl2_init = 0.05

    nozl1_err = rotl1_err = nozl2_err = rotl2_err = 100
    iteration = 0
    outputs = {}

    while (nozl1_err > 0.001 or rotl1_err > 0.001 or nozl2_err > 0.001 or rotl2_err > 0.001) and iteration < 500:
        outputs = solver_2stg.meanline_calculator(
            t01=t01, p01=p01, mfr=mfr, power=power,
            vax_12=vax_12, vax_23=vax_23, vax_34=vax_34,
            vax_45=vax_45, vax_56=vax_56, vax_67=vax_67, vax_78=vax_78,
            rm12=rm12, rm23=rm23, rm34=rm34, rm45=rm45,
            rm56=rm56, rm67=rm67, rm78=rm78,
            M1=M1,
            ngv1_exit_angle=ngv1_exit_angle,
            ngv2_exit_angle=ngv2_exit_angle,
            rmean=rmean, swirl=swirl, rpm=rpm,
            choking_1=choking_1, choking_4=choking_4,
            clearance_1=clearance_1, clearance_2=clearance_2,
            asp_2=asp_2, asp_4=asp_4, asp_6=asp_6, asp_8=asp_8,
            nozl_1=nozl1_init, rotl_1=rotl1_init,
            nozl_2=nozl2_init, rotl_2=rotl2_init,
            ngv_stagger_1=ngv_stagger_1, rotor_stagger_1=rotor_stagger_1,
            ngv_stagger_2=ngv_stagger_2, rotor_stagger_2=rotor_stagger_2,
            stg_1_power_ratio=stg_1_power_ratio,
            ngv_1_zweifel=ngv_1_zweifel, ngv_2_zweifel=ngv_2_zweifel,
            rotor_1_zweifel=rotor_1_zweifel, rotor_2_zweifel=rotor_2_zweifel
        )

        new_nozl1, new_rotl1 = outputs["nozl_1"], outputs["rotl_1"]
        new_nozl2, new_rotl2 = outputs["nozl_2"], outputs["rotl_2"]

        nozl1_err = mt.fabs((new_nozl1 - nozl1_init) / new_nozl1) * 100
        rotl1_err = mt.fabs((new_rotl1 - rotl1_init) / new_rotl1) * 100
        nozl2_err = mt.fabs((new_nozl2 - nozl2_init) / new_nozl2) * 100
        rotl2_err = mt.fabs((new_rotl2 - rotl2_init) / new_rotl2) * 100

        nozl1_init, rotl1_init = new_nozl1, new_rotl1
        nozl2_init, rotl2_init = new_nozl2, new_rotl2

        iteration += 1

    return outputs

# --- Ana çalışma bloğu ---
cycle_inputs = read_inputs_from_json("Axial_Turbine/data/cycle_inputs_2stg.json")
designer_inputs = read_inputs_from_json("Axial_Turbine/data/designer_inputs_2stg.json")
samplings = read_inputs_from_json("Axial_Turbine/data/latin_hypercube_samples_2_stg.json")

all_outputs = []
failed_samples = []

for i, sample_inputs in enumerate(samplings):
    print(f"\n{i+1}. örnek çalıştırılıyor...")
    try:
        outputs = calculate_for_sample(sample_inputs, cycle_inputs, designer_inputs)
        all_outputs.append(outputs)
    except Exception as e:
        print(f"❌ {i+1}. örnek hata verdi: {str(e)}")
        failed_samples.append({
            "index": i + 1,
            "inputs": sample_inputs,
            "error": str(e)
        })

# Başarılı sonuçları yaz
with open("Axial_Turbine/data/all_outputs_2stg.json", "w", encoding="utf-8") as file:
    json.dump(all_outputs, file, indent=2)

# Hatalı örnekleri yaz
with open("Axial_Turbine/data/failed_samples_log.json", "w", encoding="utf-8") as file:
    json.dump(failed_samples, file, indent=2)

end_time = time.time()
print("\n✅ Tüm örnekler işlendi.")
print("Toplam Çalışma Süresi:", round(end_time - start_time, 2), "saniye")

# Son örnek için akış yolu çizimi (başarılıysa)
if all_outputs:
    flowpath.draw_flowpath_with_x_blades_2stg(all_outputs[-1], save_path="flowpath_last_2stg.png")
