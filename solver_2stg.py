import math as mt
import losses

def meanline_calculator(
    rpm,
    power,
    mfr,
    p01,
    t01,
    swirl,
    M1,
    rmean,
    vax_12,
    vax_23,
    vax_34,
    vax_45,
    vax_56,
    vax_67,
    vax_78,
    rm12,
    rm23,
    rm34,
    rm45,
    rm56,
    rm67,
    rm78,
    ngv1_exit_angle,
    ngv2_exit_angle,
    choking_1,
    choking_4,
    clearance_1,
    clearance_2,
    asp_2,
    asp_4,
    asp_6,
    asp_8,
    nozl_1,
    rotl_1,
    nozl_2,
    rotl_2,
    ngv_stagger_1,
    rotor_stagger_1,
    ngv_stagger_2,
    rotor_stagger_2,
    ngv_1_zweifel,
    ngv_2_zweifel,
    rotor_1_zweifel,
    rotor_2_zweifel,
    stg_1_power_ratio
    ):
    
    try:
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

        #? Ngv-1 Inlet(Station-1)
        a1 = swirl * pi / 180
        a1d = mt.degrees(a1)
        t1 = t01 /((1+y12*M1**2))
        ss1 = (y*R*t1)**0.5
        p1 = p01 /(t01/t1)**yy1
        rho1 = p1 / (R*t1)
        v1 = M1* ss1
        va1 = v1 * mt.cos(a1)
        rm1 = rmean /1000
        A1 = mfr /(rho1*va1)
        h1 = A1 / (2*pi*rm1)
        rt1 = rm1 + 0.5*h1
        rh1 = rm1 - 0.5*h1
        htr1 = rh1 / rt1 

        #? Ngv-1 Outlet(Station-2)
        t02 = t01 
        va2 = vax_12*va1
        T2choke = t02 / ctr
        v2choke = mt.sqrt(y*R*T2choke)
        v2unchoke = va2 / mt.cos(mt.radians(ngv1_exit_angle))

        if choking_1 == "True":
            v2 = v2choke
        else:
            v2 = v2unchoke

        t2 = t02 - cp_other * v2**2
        rm2 = rm1 * rm12
        U2 = 0

        if nozl_1 > 0 and nozl_1 <0.5:
            P02 = p01 /(1+nozl_1*(1-(t2/t02)**yy1))
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

        #? Rotor-1 Inlet(Duct Exit Station-3)
        va3 = va2 * vax_23
        rm3 = rm2 * rm23 
        t03 = t02 
        p03 = P02
        vt3 = rm2 * vt2 / rm3
        a3 = mt.atan(vt3/va3)
        a3d = a2d
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

        #? Rotor-1 Outlet(Station-4)
        t04 = t01 - (spower*stg_1_power_ratio) / cp
        va4 = va3 * vax_34
        rm4 = rm3 * rm34
        u4 = shaft_speed*rm4
        vt4 = (-spower*stg_1_power_ratio+u3*vt3)/(u4)
        v4 = mt.sqrt(vt4**2+va4**2)
        a4 = mt.atan(vt4/va4)
        a4d = mt.degrees(a4)
        t4 = t04 - cp_other* v4**2
        wt4 = vt4-u4
        w4 = mt.sqrt(va4**2+wt4**2)
        t04rel = t4 + cp_other*w4**2

        if rotl_1>0 and rotl_1 < 0.5:
            P04rel = p03rel / (1+rotl_1*(1-(t4/t04rel)**yy1))
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
        
        #? NGV2- Inlet (Duct-2 Exit Station-5)
        a5d = a4d
        a5 = a4
        t05 = t04
        p05 = p04
        va5 = va4 * vax_45
        rm5 = rm4 * rm45
        U5 = 0
        v5 = va5 / mt.cos(a5)
        M5 = M4 
        t5 = t05 /((1+y12*M5**2))
        p5 = p05 * ((t5/t05)**yy1)
        rho5 = p5 / (R*t5)
        A5 = mfr / (va5*rho5)
        h5 = A5 / (2*pi*rm5)
        rh5 = rm5 - 0.5 * h5
        rt5 = rm5 + 0.5 * h5
        htr5 = rh5 / rt5
        
        #? NGV2- Outlet(Station-6)
        t06 = t05 
        va6 = vax_56*va5
        T6choke = t06 / ctr
        v6choke = mt.sqrt(y*R*T6choke)
        v6unchoke = va6 / (mt.cos(mt.radians(ngv2_exit_angle)))
        
        if choking_4 == "True":
            v6 = v6choke
        else:
            v6 = v6unchoke
        
        t6 = t06 - cp_other * v6**2
        rm6 = rm5 * rm56
        U6 = 0
        
        if nozl_2 > 0 and nozl_2 <0.5:
            P06 = p05 /(1+nozl_2*(1-(t6/t06)**yy1))
        else:
            P06 = p05 /(1+0.08*(1-(t6/t06)**yy1))
        
        p6 = P06 * ((t6/t06)**yy1)
        M6 = v6 / mt.sqrt(y*R*t6)
        
        rho6 = p6 /(R*t6)
        A6 = mfr / (rho6*va6)
        h6 = A6 /(2*pi*rm6)
        rt6 = rm6 + 0.5 * h6
        rh6 = rm6 - 0.5 * h6
        htr6 = rh6 / rt6
        
        a6 = mt.acos(va6 / v6)
        a6d = mt.degrees(a6)
        vt6 = v6 * mt.sin(a6)
        wt6 = vt6 - U6
        beta6 = mt.atan(wt6/va6)
        beta6d = mt.degrees(beta6)
        w6 = mt.sqrt(wt6**2+va6**2)
        M6r = w6 / mt.sqrt(y*R*t6)

        #? Rotor-2 Inlet(Duct Exit Station-7)
        va7 = va6 * vax_67
        rm7 = rm6 * rm67
        t07 = t06
        p07 = P06
        vt7 = rm6 * vt6 / rm7
        a7 = mt.atan(vt7/va7)
        a7d = a6d
        v7 = va7 / mt.cos(a7)
        t7 = t07 - cp_other * v7**2
        u7 = shaft_speed*rm7
        wt7 = vt7 - u7
        w7 = mt.sqrt(wt7**2+va7**2)
        p7 = p07 * ((t7/t07)**yy1)
        bet7d = mt.degrees(mt.atan(wt7/va7))
        b7 = mt.radians(bet7d)
        rho7 = p7  /  (R*t7)
        A7 = mfr / (rho7*va7)
        h7 = A7 / (2* pi * rm7)
        rt7 = rm7 + 0.5 * h7
        rh7 = rm7 - 0.5 * h7
        htr7 = rh7 / rt7 
        M7 = M6
        M7r = w7 / mt.sqrt(y * R * t7)
        t07rel = t7 + cp_other * w7**2
        p07rel = p7 * ((t07rel/t7)**yy1)
        
        #? Rotor-2 Exit (Station-8)
        
        t08 = t05 - (spower*(1-stg_1_power_ratio)) / cp
        va8 = va7 * vax_78
        rm8 = rm7 * rm78
        u8 = shaft_speed*rm8
        vt8 = (-spower*(1-stg_1_power_ratio)+u7*vt7)/(u8)
        v8 = mt.sqrt(vt8**2+va8**2)
        a8 = mt.atan(vt8/va8)
        a8d = mt.degrees(a8)
        t8 = t08 - cp_other* v8**2
        wt8 = vt8-u8
        w8 = mt.sqrt(va8**2+wt8**2)
        t08rel = t8 + cp_other*w8**2

        if rotl_2>0 and rotl_2 < 0.5:
            P08rel = p07rel / (1+rotl_2*(1-(t8/t08rel)**yy1))
        else:
            P08rel = p07rel / (1+0.12*(1-(t8/t08rel)**yy1))

        p8 = P08rel * ((t8/t08rel)**yy1)
        p08 = p8*((t08/t8)**yy1)
        bet8 = mt.atan(wt8/va8)
        bet8d = mt.degrees(bet8)
        M8r = w8 / mt.sqrt(y*R*t8)
        M8 = v8 / mt.sqrt(y*R*t8)
        rho8 = p8 / (R*t8)
        A8 = mfr / (va8 * rho8)
        h8 = A8 / (2*pi*rm8)
        rh8 = rm8 - 0.5*h8
        rt8 = rm8 + 0.5*h8
        htr8 = rh8 / rt8
        t08p = t01* (p08/p01)**(1/(yy1))

        ngv_1_loss_calculation = losses.losses(
            a1d = swirl,
            a2d = a2d,
            M1=M1,
            M2 = M2,
            rm1 = rm1,
            rm2 = rm2,
            stagger = ngv_stagger_1,
            h1 = h1,
            h2 = h2,
            asp = asp_2,
            tmax_c = 0.2,
            bladetype="stator",
            htr = htr1,
            v2 = v2,
            p1 = p1,
            p2 = p2,
            y = y,
            temp = t2,
            rho = rho2,
            KmodSelection="standart",
            delta_r = 0,
            zweifel=ngv_1_zweifel,
        )
        
        #print("ngv_loss:",ngv_loss_calculation)

        rotor_1_loss_calculation = losses.losses(
            a1d = bet3d,
            a2d = bet4d,
            M1=M3r,
            M2 = M4r,
            rm1 = rm3,
            rm2 = rm4,
            stagger = rotor_stagger_1,
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
            rho = rho4,
            KmodSelection="standart",
            delta_r = clearance_1,
            zweifel=rotor_1_zweifel
        )
        
        ngv_2_loss_calculation = losses.losses(
            a1d = a5d,
            a2d = a6d,
            M1=M5,
            M2 = M6,
            rm1 = rm5,
            rm2 = rm6,
            stagger = ngv_stagger_2,
            h1 = h5,
            h2 = h6,
            asp = asp_6,
            tmax_c = 0.2,
            bladetype="stator",
            htr = htr6,
            v2 = v6,
            p1 = p5,
            p2 = p6,
            y = y,
            temp = t6,
            rho = rho6,
            KmodSelection="standart",
            delta_r = 0,
            zweifel=ngv_2_zweifel
        )
        # 3-7 , 4-8
        rotor_2_loss_calculation = losses.losses(
            a1d = bet7d,
            a2d = bet8d,
            M1=M7r,
            M2 = M8r,
            rm1 = rm7,
            rm2 = rm8,
            stagger = rotor_stagger_2,
            h1 = h7,
            h2 = h8,
            asp = asp_8,
            tmax_c = 0.2,
            bladetype="rotor",
            htr = htr7,
            v2 = v8,
            p1 = p7,
            p2 = p8,
            y = y,
            temp = t8,
            rho = rho8,
            KmodSelection="standart",
            delta_r = clearance_2,
            zweifel=rotor_2_zweifel
        )

        #print("rotor_loss:",rotor_loss_calculation)
        #! Important Parameters

        flow_coef_1 = va4 / u4 
        flow_coef_2 = va8 / u8
        
        work_coef_1 = spower / (0.5*(u3+u4))**2
        work_coef_2 = spower / (0.5*(u7+u8))**2
        
        reaction_1 = (t3-t4)/(t1-t4)
        reaction_2 = (t7-t8)/(t5-t8)
        
        ngv_mexit_1 = M2
        ngv_mexit_2 = M6
        
        rotor_mexit_1 = M4r
        rotor_mexit_2 = M8r
        
        stage_mexit_1 = M4
        stage_mexit_2 = M8
        
        exit_swirl_1 = mt.fabs(a4d)
        exit_swirl_2 = mt.fabs(a8d)
        
        pratio_1 = p01 / p04
        pratio_2 = p05 / p08
        pratio = pratio_1*pratio_2
        
        efficiency_1 = (t01-t04)/(t01-t04p)
        efficiency_2 = (t05-t08)/(t05-t08p)
        
        efficiency = (efficiency_1+efficiency_2)*0.5
        
        critical_pr_1 = P02 / p2
        critical_pr_2 = P06 / p6

        nozl_1 = ngv_1_loss_calculation["total_loss"]
        nozl_2 = ngv_2_loss_calculation["total_loss"]
        
        rotl_1 = rotor_1_loss_calculation["total_loss"]
        rotl_2 = rotor_2_loss_calculation["total_loss"]
        
        ngv_ax_chord_1 = ngv_1_loss_calculation['axial_chord']
        ngv_ax_chord_2 = ngv_2_loss_calculation['axial_chord']
        
        rotor_ax_chord_1 = rotor_1_loss_calculation['axial_chord']
        rotor_ax_chord_2 = rotor_2_loss_calculation['axial_chord']

        ngv_count_1 = ngv_1_loss_calculation['blade_count']
        ngv_count_2 = ngv_2_loss_calculation['blade_count']
        
        rotor_count_1 = rotor_1_loss_calculation['blade_count']
        rotor_count_2 = rotor_2_loss_calculation['blade_count']

        noz1_fang_hub = mt.degrees(mt.fabs(mt.atan((rh1-rh2)/(ngv_ax_chord_1))))
        noz2_fang_hub = mt.degrees(mt.fabs(mt.atan((rh5-rh6)/(ngv_ax_chord_2))))

        noz1_fang_tip = mt.degrees(mt.fabs(mt.atan((rt1-rt2)/(ngv_ax_chord_1))))
        noz2_fang_tip = mt.degrees(mt.fabs(mt.atan((rt5-rt6)/(ngv_ax_chord_2))))

        rot1_fang_hub = mt.degrees(mt.fabs(mt.atan((rh3-rh4)/(rotor_ax_chord_1))))
        rot2_fang_hub = mt.degrees(mt.fabs(mt.atan((rh7-rh8)/(rotor_ax_chord_2))))

        rot1_fang_tip = mt.degrees(mt.fabs(mt.atan((rt3-rt4)/(rotor_ax_chord_1))))
        rot2_fang_tip = mt.degrees(mt.fabs(mt.atan((rt7-rt8)/(rotor_ax_chord_2))))

        duct1_fang_hub = mt.degrees(mt.fabs(mt.atan((rh2-rh3)/(rotor_ax_chord_1*0.50))))
        duct2_fang_hub = mt.degrees(mt.fabs(mt.atan((rh4-rh5)/(ngv_ax_chord_2*0.50))))
        duct3_fang_hub = mt.degrees(mt.fabs(mt.atan((rh6-rh7)/(rotor_ax_chord_2*0.50))))

        duct1_fang_tip = mt.degrees(mt.fabs(mt.atan((rt2-rt3)/(rotor_ax_chord_1*0.50))))
        duct2_fang_tip = mt.degrees(mt.fabs(mt.atan((rt4-rt5)/(ngv_ax_chord_2*0.50))))
        duct3_fang_tip = mt.degrees(mt.fabs(mt.atan((rt6-rt7)/(rotor_ax_chord_2*0.50))))

        rotor1_turning = bet3d - bet4d
        rotor2_turning = bet7d - bet8d

        #an2rlsmax = ((pi*((rt4/1000)**2-(rh4/1000)**2)*rpm*1.12**2/(10**6)*0.1550031))*1e10
        an2rls1 = ((A4* 10**6 *(rpm*1.12)**2)/(10**13))/645 * 1000
        an2rls2 = ((A8* 10**6 *(rpm*1.12)**2)/(10**13))/645 * 1000
        
        return {
            "nozl_1" : nozl_1,
            "rotl_1" : rotl_1,
            "nozl_2" : nozl_2,
            "rotl_2" : rotl_2,
            "ngv_count_1" : ngv_count_1,
            "ngv_count_2" : ngv_count_2,
            "rotor_count_1" : rotor_count_1,
            "rotor_count_2" : rotor_count_2,
            "flow_coef_1" : flow_coef_1,
            "flow_coef_2" : flow_coef_2,
            "work_coef_1" : work_coef_1,
            "work_coef_2" : work_coef_2,
            "reaction_1" : reaction_1,
            "reaction_2" : reaction_2,
            "ngv_mexit_1" : ngv_mexit_1,
            "ngv_mexit_2" : ngv_mexit_2,
            "rotor_mexit_1" : rotor_mexit_1,
            "rotor_mexit_2" : rotor_mexit_2,
            "stage_mexit_1" : stage_mexit_1,
            "stage_mexit_2" : stage_mexit_2,
            "exit_swirl_1" : exit_swirl_1,
            "exit_swirl_2" : exit_swirl_2,
            "pratio_1" : pratio_1,
            "pratio_2" : pratio_2,
            "pratio" : pratio,
            "efficiency_1" : efficiency_1,
            "efficiency_2" : efficiency_2,
            "efficiency" : efficiency,
            "critical_pr_1" : critical_pr_1,
            "critical_pr_2" : critical_pr_2,
            "noz1_fang_hub" : noz1_fang_hub,
            "noz2_fang_hub" : noz2_fang_hub,
            "rot1_fang_hub" : rot1_fang_hub,
            "rot2_fang_hub" : rot2_fang_hub,
            "noz1_fang_tip" : noz1_fang_tip,
            "noz2_fang_tip" : noz2_fang_tip,
            "rot1_fang_tip" : rot1_fang_tip,
            "rot2_fang_tip" : rot2_fang_tip,
            "duct1_fang_hub" : duct1_fang_hub,
            "duct2_fang_hub" : duct2_fang_hub,
            "duct3_fang_hub" : duct3_fang_hub,
            "duct1_fang_tip" : duct1_fang_tip,
            "duct2_fang_tip" : duct2_fang_tip,
            "duct3_fang_tip" : duct3_fang_tip,
            "rotor1_turning" : rotor1_turning,
            "rotor2_turning" : rotor2_turning,
            "an2_rls1" : an2rls1,
            "an2_rls2" : an2rls2,
            "rhub1" : rh1,
            "rhub2" : rh2,
            "rhub3" : rh3,
            "rhub4" : rh4,
            "rhub5" : rh5,
            "rhub6" : rh6,
            "rhub7" : rh7,
            "rhub8" : rh8,
            "rtip1" : rt1,
            "rtip2" : rt2,
            "rtip3" : rt3,
            "rtip4" : rt4,
            "rtip5" : rt5,
            "rtip6" : rt6,
            "rtip7" : rt7,
            "rtip8" : rt8,
            "ngv_ax_chord_1" : ngv_ax_chord_1,
            "ngv_ax_chord_2" : ngv_ax_chord_2,
            "rotor_ax_chord_1" : rotor_ax_chord_1,
            "rotor_ax_chord_2" : rotor_ax_chord_2,
            "ngv_1_profile_loss" : ngv_1_loss_calculation["losses"]["profile_loss"],
            "ngv_1_secondary_loss" : ngv_1_loss_calculation["losses"]["secondary_loss"],
            "ngv_1_trailing_edge_loss" : ngv_1_loss_calculation["losses"]["trailing_edge_loss"],
            "ngv_1_supersonic_loss" : ngv_1_loss_calculation["losses"]["supersonic_exp_loss"],
            "ngv_1_clearance_loss" : ngv_1_loss_calculation["losses"]["clearance_loss"],
            "rotor_1_profile_loss" : rotor_1_loss_calculation["losses"]["profile_loss"],
            "rotor_1_secondary_loss" : rotor_1_loss_calculation["losses"]["secondary_loss"],
            "rotor_1_trailing_edge_loss" : rotor_1_loss_calculation["losses"]["trailing_edge_loss"],
            "rotor_1_supersonic_loss" : rotor_1_loss_calculation["losses"]["supersonic_exp_loss"],
            "rotor_1_clearance_loss" : rotor_1_loss_calculation["losses"]["clearance_loss"],
            "ngv_2_profile_loss" : ngv_2_loss_calculation["losses"]["profile_loss"],
            "ngv_2_secondary_loss" : ngv_2_loss_calculation["losses"]["secondary_loss"],
            "ngv_2_trailing_edge_loss" : ngv_2_loss_calculation["losses"]["trailing_edge_loss"],
            "ngv_2_supersonic_loss" : ngv_2_loss_calculation["losses"]["supersonic_exp_loss"],
            "ngv_2_clearance_loss" : ngv_2_loss_calculation["losses"]["clearance_loss"],
            "rotor_2_profile_loss" : rotor_2_loss_calculation["losses"]["profile_loss"],
            "rotor_2_secondary_loss" : rotor_2_loss_calculation["losses"]["secondary_loss"],
            "rotor_2_trailing_edge_loss" : rotor_2_loss_calculation["losses"]["trailing_edge_loss"],
            "rotor_2_supersonic_loss" : rotor_2_loss_calculation["losses"]["supersonic_exp_loss"],
            "rotor_2_clearance_loss" : rotor_2_loss_calculation["losses"]["clearance_loss"],
            "ngv_1_total_loss" : ngv_1_loss_calculation["total_loss"],
            "ngv_2_total_loss" : ngv_2_loss_calculation["total_loss"],
            "rotor_1_total_loss" : rotor_1_loss_calculation["total_loss"],
            "rotor_2_total_loss" : rotor_2_loss_calculation["total_loss"],
            
        }

    except Exception as e:
        return {"efficiency": 0, "error": str(e)}