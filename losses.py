import math as mt



def losses(a1d,a2d,y,h1,h2,bladetype,stagger,asp,rm1,rm2,M1,M2,tmax_c,htr,p1,p2,rho,temp,v2,delta_r,KmodSelection,zweifel):
    
    #? tmax_c hesaplanması gerekiyor 
    
    #Constants
    y1y = (y-1)/(y)
    yy1 = (y/(y-1))
    y12 = (y-1)/(2)

    #Calculations
    alfa1d = 90-a1d 
    alfa2d = 90-mt.fabs(a2d)
    
    a1d_rad = mt.radians(a1d)
    a2d_rad = mt.radians(a2d)

    #? Optimum Pitch-to-Chord Ainley-Mathieson
    sc0 = 0.427 + (alfa2d/58)-(alfa2d/93)**2
    sc1 = 0.224 + (1.575-(alfa2d/90))*(alfa2d/90)
    zn = (90-alfa1d)/(90-alfa2d)
    scopt = sc0+(sc1-sc0)*abs(zn)*zn  #! Optimum pitch-to-chord ratio
    hn = 0.5*(h1+h2)

    #? 
    chn = hn / asp
    ax_cn = chn * mt.cos((abs(a1d_rad)+abs(a2d_rad))/2)
    sn = zweifel* ax_cn/(2*mt.cos(abs(a2d_rad))**2*(mt.tan(abs(a1d_rad))+mt.tan(abs(a2d_rad))))
    te_thick = sn*0.02
    blade_count = round((2*mt.pi*((rm1+rm2)/2))/(sn))

    if(alfa2d<=30):
        scmin = 0.46 + alfa2d/77
    elif(alfa2d>30):
        scmin = 0.614 + alfa2d/130
    X = scopt - scmin
    n = 1+alfa2d/30

    if(alfa2d<=27):
        A = 0.025+(27-alfa2d)/530
    elif(alfa2d>27):
        A = 0.025+(27-alfa2d)/3085

    B = 0.1583 - alfa2d/1640
    C = 0.08*((alfa2d/30)**2-1)

    #! YP1 Hesabı
    if(alfa2d<=30):
        yp1 = A+B*X**2+C*X**3
    elif(alfa2d>30):
        yp1 = A+B*(mt.fabs(X))**n
        
    #! YP2 Hesabı
    scmin_2 = 0.224 + 1.575*(alfa2d/90)-(alfa2d/90)**2
    X = scopt - scmin_2
    A = 0.242 - (alfa2d/151)+(alfa2d/127)**2

    if(alfa2d<=30):
        B = 0.3 + (30-alfa2d)/50
    elif(alfa2d>30):
        B = 0.3+(30-alfa2d)/275
        
    C = 0.88 - (alfa2d/42.4)+(alfa2d/72.8)**2

    yp2 = A+B*X**2-C*X**3

    if(M2<=0.2):
        K1=1.0
    elif(M2>0.2):
        K1 = 1-1.25*(M2-0.2)

    K2 = (M1/M2)**2
    Kaccel = 1-K2*(1-K1)
    Kps = (yp1+zn*abs(zn)*(yp2-yp1))*(5*tmax_c)**(zn)

    if(bladetype == "rotor"):
        K = 5.2
    elif(bladetype == "stator"):
        K=1.8

    Minhub = M1*(1+K*(abs(htr-1))**2.2)

    if(Minhub < 0.4):
        Ksh = 0

    elif(Minhub>0.4):
        Ksh = 0.75*((Minhub-0.4)**1.75)*(htr)*(p1/p2)*((1-(1+(y12)*M1**2)**yy1)/((1-(1+(y12)*M2**2)**yy1)))
        
    dummy = (2/3)*(Kps)*(Kaccel)+Ksh

    #! Supersonic Drag Rise
    if(M2>=0.9):
        CFM = 1+60*(M2-0.9)**2

    else:
        CFM = 1
        
    #! Reynolds Number Correction
    tref = 273.15
    mref = 1.716*10**(-5)
    sref = 110.4
    c1 = (mref/(tref**(1.5)))*(tref+sref)
    mü = (c1*temp**1.5)/(temp+sref)
    Re = (rho*v2*chn)/(mü)

    Kre = 1.0

    if(Re<=2*10**5):
        Kre = (Re/(2*10**5))**(-0.4)
    elif(2*10**5<Re<10**6):
        Kre = 1
    elif(Re>10**6):
        Kre = (Re/(10**6))

    #! Kmodified

    if(KmodSelection == "modern"):
        Kmod  = (2/3)
    elif(KmodSelection == "standart"):
        Kmod = 1
        
    Yp = 0.914 *((Kmod)*CFM*dummy*Kre)

    ##- SECONDARY LOSSES -##

    alpha_mean_rad = mt.atan((mt.tan(a1d_rad)+(mt.tan(a2d_rad)))/2)
    cl_s_c = 2*(mt.tan(a1d_rad)-mt.tan(a2d_rad))*mt.cos(alpha_mean_rad)

    if(asp<=2):
        fas = (1-0.25*mt.sqrt(2-asp))/(asp) 
    else:
        fas = 1/(asp)

    Ks = 0.0334 * fas * (mt.cos(a2d_rad)/(mt.cos(a1d_rad)))*(cl_s_c**2)*((mt.cos(a2d_rad)**2)/(mt.cos(alpha_mean_rad))**3)
    Kcs = 1-(1/asp)**2*(1-Kaccel)
    Ys = 1.2 * Ks * Kcs 

    ##- TRAILING EDGE LOSS -##
    beta_g = mt.radians(alfa2d)
    deltapt = 0.5 * rho * v2 ** 2 *((sn*mt.sin(beta_g))/(sn*mt.sin(beta_g)-te_thick)-1)**2
    Yte = 2*deltapt/(rho*v2**2)

    ##- SUPERSONIC EXPANSION LOSS -##
    if(M2<=1):
        Ysup_exp_loss = 0
    else:
        Ysup_exp_loss = ((M2-1)/(M2))**2

    ##- CLEARANCE LOSS -##

    if(bladetype == "rotor"):
        tc2 = delta_r*hn*2**(-0.42)
        Yc = 0.47* (chn/hn)*((tc2/chn)**0.78)*cl_s_c
    else:
        Yc = 0
        
        
    #! OUTPUT
    losses = {
        "profile_loss" : Yp,
        "secondary_loss" : Ys,
        "trailing_edge_loss" : Yte,
        "supersonic_exp_loss": Ysup_exp_loss,
        "clearance_loss" : Yc
    }       
    
    return {
        "total_loss" : (Yp+Ys+Yte+Ysup_exp_loss+Yc),
        "blade_count" : blade_count,
        "axial_chord" : ax_cn,
        "losses" : losses,
    }
    