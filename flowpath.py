import matplotlib.pyplot as plt

def draw_flowpath_with_x_blades_1stg(result, save_path="flowpath.png"):
    """
    Rotor ve stator parametrelerinden akış yolu grafiğini oluşturur.
    NGV ve Rotor kanatları X şeklinde gösterilir.
    X ve Y eksenleri mm cinsindendir.
    """

    # Radyal noktalar (mm cinsine çevrildiğini varsayıyoruz)
    rhubs = [
        result["rhub1"],  # rh0
        result["rhub1"],
        result["rhub2"],
        result["rhub3"],
        result["rhub4"],
        result["rhub4"],  # rh5
    ]

    rtips = [
        result["rtip1"],  # rt0
        result["rtip1"],
        result["rtip2"],
        result["rtip3"],
        result["rtip4"],
        result["rtip4"],  # rt5
    ]

    # Aksiyel konumlar (mm cinsine dönüştürüldü)
    x0 = 0
    x1 = x0 + result["ngv_ax_chord"] * 1000 * 0.5
    x2 = x1 + result["ngv_ax_chord"] * 1000
    x3 = x2 + result["rotor_ax_chord"] * 1000 * 0.25
    x4 = x3 + result["rotor_ax_chord"] * 1000
    x5 = x4 + result["rotor_ax_chord"] * 1000 * 0.5


    x_vals = [x0, x1, x2, x3, x4, x5]
    y_tip = rtips
    y_hub = rhubs

    # Grafik başlat
    plt.figure(figsize=(12, 5))
    plt.plot(x_vals, y_tip, label="Tip Radius", color="red", linewidth=2)
    plt.plot(x_vals, y_hub, label="Hub Radius", color="blue", linewidth=2)
    plt.fill_between(x_vals, y_hub, y_tip, color="lightgray", alpha=0.5)

    # NGV X şekli (x1 - x2)
    plt.plot([x1, x2], [rhubs[1], rtips[2]], color="black", linewidth=1.5)
    plt.plot([x1, x2], [rtips[1], rhubs[2]], color="black", linewidth=1.5)

    # ROTOR X şekli (x3 - x4)
    plt.plot([x3, x4], [rhubs[3], rtips[4]], color="black", linewidth=1.5)
    plt.plot([x3, x4], [rtips[3], rhubs[4]], color="black", linewidth=1.5)

    # Dikey çizgiler (kanat yüksekliği)
    for i in range(1, 5):
        plt.plot([x_vals[i], x_vals[i]], [rhubs[i], rtips[i]], color="black", linewidth=1.0, linestyle='--')

    # Stil ayarları
    plt.title("Axial Turbine Flowpath with Blade X Representation")
    plt.xlabel("Axial Position (mm)")
    plt.ylabel("Radius (mm)")

    # Grid ve aralıklar
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(
        ticks=[round(val, 2) for val in x_vals],
        labels=[f"{round(val,1)}" for val in x_vals]
    )
    plt.yticks(
        ticks=[round(r, 2) for r in sorted(set(rhubs + rtips))],
        labels=[f"{round(r,2)}" for r in sorted(set(rhubs + rtips))]
    )
    
    plt.ylim((0.1))

    plt.legend(loc="lower right")
    plt.tight_layout()

    # Kaydet ve göster
    plt.savefig(save_path, dpi=300)
    plt.show()


def draw_flowpath_with_x_blades_2stg(result, save_path="flowpath.png"):
    """
    Rotor ve stator parametrelerinden akış yolu grafiğini oluşturur.
    NGV ve Rotor kanatları X şeklinde gösterilir.
    X ve Y eksenleri mm cinsindendir.
    """

    # Radyal noktalar (mm cinsine çevrildiğini varsayıyoruz)
    rhubs = [
        result["rhub1"],  # rh0
        result["rhub1"],
        result["rhub2"],
        result["rhub3"],
        result["rhub4"],
        result["rhub5"], 
        result["rhub6"],
        result["rhub7"],  
        result["rhub8"],
        result["rhub8"],
    ]

    rtips = [
        result["rtip1"],  # rt0
        result["rtip1"],
        result["rtip2"],
        result["rtip3"],
        result["rtip4"],
        result["rtip5"],
        result["rtip6"],
        result["rtip7"],
        result["rtip8"],
        result["rtip8"]
        
    ]

    # Aksiyel konumlar (mm cinsine dönüştürüldü)
    x0 = 0
    x1 = x0 + result["ngv_ax_chord_1"] * 1000 * 0.5
    x2 = x1 + result["ngv_ax_chord_1"] * 1000
    x3 = x2 + result["rotor_ax_chord_1"] * 1000 * 0.5
    x4 = x3 + result["rotor_ax_chord_1"] * 1000
    x5 = x4 + result["rotor_ax_chord_1"] * 1000 * 0.5
    x6 = x5 + result["ngv_ax_chord_2"] * 1000 
    x7 = x6 + result["rotor_ax_chord_2"]* 1000 * 0.5
    x8 = x7 + result["rotor_ax_chord_2"]* 1000
    x9 = x8 + result["rotor_ax_chord_2"]*1000 * 0.5


    x_vals = [x0, x1, x2, x3, x4, x5,x6,x7,x8,x9]
    y_tip = rtips
    y_hub = rhubs

    # Grafik başlat
    plt.figure(figsize=(12, 5))
    plt.plot(x_vals, y_tip, label="Tip Radius", color="red", linewidth=2)
    plt.plot(x_vals, y_hub, label="Hub Radius", color="blue", linewidth=2)
    plt.fill_between(x_vals, y_hub, y_tip, color="lightgray", alpha=0.5)

    # NGV-1 X şekli (x1 - x2)
    plt.plot([x1, x2], [rhubs[1], rtips[2]], color="black", linewidth=1.5)
    plt.plot([x1, x2], [rtips[1], rhubs[2]], color="black", linewidth=1.5)

    # ROTOR-1 X şekli (x3 - x4)
    plt.plot([x3, x4], [rhubs[3], rtips[4]], color="black", linewidth=1.5)
    plt.plot([x3, x4], [rtips[3], rhubs[4]], color="black", linewidth=1.5)
    
    # NGV-2 X şekli (x5-x6)
    plt.plot([x5, x6], [rhubs[5], rtips[6]], color="black", linewidth=1.5)
    plt.plot([x5, x6], [rtips[5], rhubs[6]], color="black", linewidth=1.5)
    
    # ROTOR-2 X şekli (x5-x6)
    plt.plot([x7, x8], [rhubs[7], rtips[8]], color="black", linewidth=1.5)
    plt.plot([x7, x8], [rtips[7], rhubs[8]], color="black", linewidth=1.5)

    # Dikey çizgiler (kanat yüksekliği)
    for i in range(1, 9):
        plt.plot([x_vals[i], x_vals[i]], [rhubs[i], rtips[i]], color="black", linewidth=1.0, linestyle='--')

    # Stil ayarları
    plt.title("Axial Turbine Flowpath with Blade X Representation")
    plt.xlabel("Axial Position (mm)")
    plt.ylabel("Radius (mm)")

    # Grid ve aralıklar
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(
        ticks=[round(val, 2) for val in x_vals],
        labels=[f"{round(val,1)}" for val in x_vals]
    )
    plt.yticks(
        ticks=[round(r, 2) for r in sorted(set(rhubs + rtips))],
        labels=[f"{round(r,2)}" for r in sorted(set(rhubs + rtips))]
    )
    
    plt.ylim((0))

    plt.legend(loc="lower right")
    plt.tight_layout()

    # Kaydet ve göster
    plt.savefig(save_path, dpi=300)
    plt.show()
