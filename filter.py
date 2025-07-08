import json

# Sınırlamalar
def is_valid(entry):
    fang_values = [v for k, v in entry.items() if "_fang_" in k]
    if any(f > 15 for f in fang_values):
        return False

    if not (0.3 <= entry.get("flow_coef_1", 0) <= 0.9):
        return False
    if not (0.3 <= entry.get("flow_coef_2", 0) <= 0.9):
        return False

    if not (0.3 <= entry.get("reaction_1", 0) <= 0.5):
        return False
    if not (0.3 <= entry.get("reaction_2", 0) <= 0.5):
        return False

    if not (2.7 <= entry.get("pratio", 0) <= 3.2):
        return False

    if entry.get("an2_rls1", 100) >= 5:
        return False
    if entry.get("an2_rls2", 100) >= 5:
        return False

    if not (1.05 <= entry.get("work_coef_1", 0) <= 1.9):
        return False
    if not (1.05 <= entry.get("work_coef_2", 0) <= 1.9):
        return False

    return True

# Dosyayı oku
with open('Axial_Turbine/data/all_outputs_2stg.json', 'r') as f:
    data = json.load(f)

# Filtrele
filtered = [d for d in data if is_valid(d)]

# Verimi yüksekten düşüğe sırala
filtered_sorted = sorted(filtered, key=lambda x: x.get("efficiency", 0), reverse=True)

# Yeni dosyaya yaz
filtered_filename = "Axial_Turbine/data/filtered_outputs_2stg.json"
with open(filtered_filename, "w") as f:
    json.dump(filtered_sorted, f, indent=4)

filtered_filename
