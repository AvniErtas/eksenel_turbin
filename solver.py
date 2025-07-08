import math as mt
import losses

def meanline_calculator(
    rpm,power,mfr,p01,t01,swirl,M1,rmean,vax_12,vax_23,vax_34,rm12,rm23,rm34,ngv_exit_angle,choking,clearance,asp_2,asp_4,nozl,rotl,ngv_stagger,rotor_stagger,ngv_1_zweifel,rotor_1_zweifel):
    
    y = 1.33
    cp = 1148
    R = 287.1
    y = cp/(cp-R)
    y1y = (y-1)/(y)
    yy1 = y/(y-1)
    y12 = (y-1)/2
    pi = mt.pi
    ctr = 0.5 * (y+1)
    cp_other = 1 / (2*cp)

    p01 = p01 * 1000

    #! Calculations

    shaft_speed = rpm * pi / 30
    spower = power / mfr 

    #? Ngv-1 Inlet
    alfa1 = swirl * pi / 180
    t1 = t01 /((1+y12*M1**2))
    ss1 = (y*R*t1)**0.5
    p1 = p01 /(t01/t1)**yy1
    rho1 = p1 / (R*t1)
    v1 = M1* ss1
    va1 = v1 * mt.cos(alfa1)
    rm1 = rmean /1000
    A1 = mfr /(rho1*va1)
    h = A1 / (2*pi*rm1)
    rt1 = rm1 + 0.5*h
    rh1 = rm1 - 0.5*h
    htr = rh1 / rt1 

    #? Ngv-1 Outlet
    t02 = t01 
    va2 = vax_12*va1
    T2choke = t02 / ctr
    v2choke = mt.sqrt(y*R*T2choke)
    v2unchoke = va2 / mt.cos(mt.radians(ngv_exit_angle))

    if choking == "True":
        v2 = v2choke
    else:
        v2 = v2unchoke

    t2 = t02 - cp_other * v2**2
    rm2 = rm1 * rm12
    U2 = 0

    if nozl > 0 and nozl <0.5:
        P02 = p01 /(1+nozl*(1-(t2/t02)**yy1))
    else:
        P02 = p01 /(1+0.08*(1-(t2/t02)**yy1))
        
    p2 = P02 * ((t2/t02)**yy1)
    M2 = v2 / mt.sqrt(y*R*t2)
    rho2 = p2 /(R*t2)
    A2 = mfr / (rho2*va2)
    h2 = A2 /(2*pi*rm2)
    rt2 = rm2 + 0.5 * h2
    rh2 = rm2 - 0.5 * h2
    htr2 = rh2 / rt2

    a2 = mt.acos(va2 / v2)
    a2d = mt.degrees(a2)
    vt2 = v2 * mt.sin(a2)
    wt2 = vt2 - U2
    beta2 = mt.atan(wt2/va2)
    beta2d = mt.degrees(beta2)
    w2 = mt.sqrt(wt2**2+va2**2)
    M2r = w2 / mt.sqrt(y*R*t2)

    #? Rotor-1 Inlet
    va3 = va2 * vax_23
    rm3 = rm2 * rm23 
    t03 = t02 
    p03 = P02
    a3d = a2d
    vt3 = rm2 * vt2 / rm3
    a3 = mt.atan(vt3/va3)
    v3 = va3 / mt.cos(a3)
    t3 = t03 - cp_other * v3**2
    u3 = shaft_speed*rm3
    wt3 = vt3 - u3
    w3 = mt.sqrt(wt3**2+va3**2)
    p3 = p03 * ((t3/t03)**yy1)
    bet3d = mt.degrees(mt.atan(wt3/va3))
    b3 = mt.radians(bet3d)
    rho3 = p3  /  (R*t3)
    A3 = mfr / (rho3*va3)
    h3 = A3 / (2* pi * rm3)
    rt3 = rm3 + 0.5 * h3
    rh3 = rm3 - 0.5 * h3
    htr3 = rh3 / rt3 
    M3 = M2
    M3r = w3 / mt.sqrt(y * R * t3)
    t03rel = t3 + cp_other * w3**2
    p03rel = p3 * ((t03rel/t3)**yy1)

    #? Rotor-1 Outlet
    t04 = t01 - spower / cp
    va4 = va3 * vax_34
    rm4 = rm3 * rm34
    u4 = shaft_speed*rm4
    vt4 = (-spower+u3*vt3)/(u4)
    v4 = mt.sqrt(vt4**2+va4**2)
    a4 = mt.atan(vt4/va4)
    a4d = mt.degrees(a4)
    t4 = t04 - cp_other* v4**2
    wt4 = vt4-u4
    w4 = mt.sqrt(va4**2+wt4**2)
    t04rel = t4 + cp_other*w4**2

    if rotl>0 and rotl < 0.5:
        P04rel = p03rel / (1+rotl*(1-(t4/t04rel)**yy1))
    else:
        P04rel = p03rel / (1+0.12*(1-(t4/t04rel)**yy1))

    p4 = P04rel * ((t4/t04rel)**yy1)
    p04 = p4*((t04/t4)**yy1)
    bet4 = mt.atan(wt4/va4)
    bet4d = mt.degrees(bet4)
    M4r = w4 / mt.sqrt(y*R*t4)
    M4 = v4 / mt.sqrt(y*R*t4)
    rho4 = p4 / (R*t4)
    A4 = mfr / (va4 * rho4)
    h4 = A4 / (2*pi*rm4)
    rh4 = rm4 - 0.5*h4
    rt4 = rm4 + 0.5*h4
    htr4 = rh4 / rt4
    t04p = t01* (p04/p01)**(1/(yy1))

    ngv_loss_calculation = losses.losses(
        a1d = swirl,
        a2d = a2d,
        M1=M1,
        M2 = M2,
        rm1 = rm1,
        rm2 = rm2,
        stagger = ngv_stagger,
        h1 = h,
        h2 = h2,
        asp = asp_2,
        tmax_c = 0.2,
        bladetype="stator",
        htr = htr,
        v2 = v2,
        p1 = p1,
        p2 = p2,
        y = y,
        temp = t2,
        rho = rho2,
        KmodSelection="standart",
        delta_r = 0,
        zweifel= ngv_1_zweifel
    )
    
    #print("ngv_loss:",ngv_loss_calculation)

    rotor_loss_calculation = losses.losses(
        a1d = bet3d,
        a2d = bet4d,
        M1=M3r,
        M2 = M4r,
        rm1 = rm3,
        rm2 = rm4,
        stagger = rotor_stagger,
        h1 = h3,
        h2 = h4,
        asp = asp_4,
        tmax_c = 0.2,
        bladetype="rotor",
        htr = htr3,
        v2 = v4,
        p1 = p3,
        p2 = p4,
        y = y,
        temp = t4,
        rho = rho2,
        KmodSelection="standart",
        delta_r = clearance,
        zweifel= rotor_1_zweifel
    )

    #print("rotor_loss:",rotor_loss_calculation)
    #! Important Parameters

    flow_coef = va4 / u4 
    work_coef = spower / (0.5*(u3+u4))**2
    reaction = (t3-t4)/(t1-t4)
    ngv_mexit = M2
    rotor_mexit = M4r
    stage_mexit = M4
    exit_swirl = mt.fabs(a4d)
    pratio = p01 / p04
    efficiency = (t01-t04)/(t01-t04p)
    critical_pr = P02 / p2

    nozl = ngv_loss_calculation["total_loss"]
    rotl = rotor_loss_calculation["total_loss"]
    
    ngv_ax_chord = ngv_loss_calculation['axial_chord']
    rotor_ax_chord = rotor_loss_calculation['axial_chord']

    ngv_count = ngv_loss_calculation['blade_count']
    rotor_count = rotor_loss_calculation['blade_count']

    noz_fang_hub = mt.degrees(mt.fabs(mt.atan((rh1-rh2)/(ngv_ax_chord))))
    noz_fang_tip = mt.degrees(mt.fabs(mt.atan((rt1-rt2)/(ngv_ax_chord))))

    rot_fang_hub = mt.degrees(mt.fabs(mt.atan((rh3-rh4)/(rotor_ax_chord))))
    rot_fang_tip = mt.degrees(mt.fabs(mt.atan((rt3-rt4)/(rotor_ax_chord))))

    duct_fang_hub = mt.degrees(mt.fabs(mt.atan((rh2-rh3)/(rotor_ax_chord*0.25))))
    duct_fang_tip = mt.degrees(mt.fabs(mt.atan((rt2-rt3)/(rotor_ax_chord*0.25))))

    rotor_turning = bet3d - bet4d

    #an2rlsmax = ((pi*((rt4/1000)**2-(rh4/1000)**2)*rpm*1.12**2/(10**6)*0.1550031))*1e10
    an2rlsmax = ((A4* 10**6 *(rpm*1.12)**2)/(10**13))/645 * 1000
    
    output = {
        "nozl" : nozl,
        "rotl" : rotl,
        "ngv_count" : ngv_count,
        "rotor_count" : rotor_count,
        "flow_coef" : flow_coef,
        "work_coef" : work_coef,
        "reaction" : reaction,
        "ngv_mexit" : ngv_mexit,
        "rotor_mexit" : rotor_mexit,
        "stage_mexit" : stage_mexit,
        "exit_swirl" : exit_swirl,
        "pratio" : pratio,
        "efficiency" : efficiency,
        "critical_pr" : critical_pr,
        "noz_fang_hub" : noz_fang_hub,
        "rot_fang_hub" : rot_fang_hub,
        "noz_fang_tip" : noz_fang_tip,
        "rot_fang_tip" : rot_fang_tip,
        "duct_fang_hub" : duct_fang_hub,
        "duct_fang_tip" : duct_fang_tip,
        "rotor_turning" : rotor_turning,
        "an2_max" : an2rlsmax,
        "rhub1" : rh1,
        "rhub2" : rh2,
        "rhub3" : rh3,
        "rhub4" : rh4,
        "rtip1" : rt1,
        "rtip2" : rt2,
        "rtip3" : rt3,
        "rtip4" : rt4,
        "ngv_ax_chord" : ngv_ax_chord,
        "rotor_ax_chord" : rotor_ax_chord
    }
    
    
    return {
        "nozl" : nozl,
        "rotl" : rotl,
        "ngv_count" : ngv_count,
        "rotor_count" : rotor_count,
        "flow_coef" : flow_coef,
        "work_coef" : work_coef,
        "reaction" : reaction,
        "ngv_mexit" : ngv_mexit,
        "rotor_mexit" : rotor_mexit,
        "stage_mexit" : stage_mexit,
        "exit_swirl" : exit_swirl,
        "pratio" : pratio,
        "efficiency" : efficiency,
        "critical_pr" : critical_pr,
        "noz_fang_hub" : noz_fang_hub,
        "rot_fang_hub" : rot_fang_hub,
        "noz_fang_tip" : noz_fang_tip,
        "rot_fang_tip" : rot_fang_tip,
        "duct_fang_hub" : duct_fang_hub,
        "duct_fang_tip" : duct_fang_tip,
        "rotor_turning" : rotor_turning,
        "an2_max" : an2rlsmax,
        "rhub1" : rh1,
        "rhub2" : rh2,
        "rhub3" : rh3,
        "rhub4" : rh4,
        "rtip1" : rt1,
        "rtip2" : rt2,
        "rtip3" : rt3,
        "rtip4" : rt4,
        "ngv_ax_chord" : ngv_ax_chord,
        "rotor_ax_chord" : rotor_ax_chord
    }
    