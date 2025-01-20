from Prelims import LoadData
from math import ceil
from math import pi
from math import tan
from math import cos
from math import sin
from math import radians
from Prelims import cot

BarArray = {"TOP":["T",0,[[4,16]]], 
            "BTM":["T",20,[[5,16]]],
            "LNK":["R",100,[[2,8]]]}

def main():
    B1 = RCC_BeamRect("B1",150,0,0,250,450,BarArray,"C30/37")
    print(f"A st req: {B1.As_Req['A_st']}")
    print(f"A st prov: {B1.As_Prov('btm')}\n")
    print(B1.flexuralCheck())
    # #print(BarArrayDet("BTM",BarArray2))
    # print(BarArrayDet("BTM",BarArray))

class RCC_BeamRect:
    def __init__(self, name:str, M_ED:float, V_ED:float, T_ED:float, breadth:float, height:float, BarArray, Concrete_Material:str, Moment_redist:float = 10, ConcreteCover = 25):
        """ Define a Rectangular Reinforced Concrete Beam
        :param name:
        :param M_ED: Design moment in kNm
        :param V_ED: Design Shear in kN
        :param T_ED: Design torsion in kPa
        :param breadth: mm
        :param height: mm
        :param BarArray: in the form {"Location":["class",spacing,[Layers]],"Location2":...}
        :param Concrete_Material: Check material list in /data/Materials.json and select material
        :param BarYSpacing: c/c spacing between layers in mm
        :param Moment_redist: % of redistribution of moments
        :param ConcreteCover: mm
        :param LinkDia: mm
        """

        self.name = name
        self.concreteMaterial = Concrete_Material
        self.concreteData = LoadData('data/Materials.json')["Concrete"][Concrete_Material]
        self.Ac = breadth * height
        self.bars = BarArray
        self.rftopData = LoadData('data/Materials.json')["Rebar"][self.bars["TOP"][0]]
        self.rfbtmData = LoadData('data/Materials.json')["Rebar"][self.bars["BTM"][0]]
        self.rflnkData = LoadData('data/Materials.json')["Rebar"][self.bars["LNK"][0]]
        self.b = breadth
        self.h = height
        self.f_ck = self.concreteData["f_ck"]
        self.f_yk_TOP = self.rftopData["f_yk"]
        self.f_yk_BTM = self.rfbtmData["f_yk"]
        self.f_yk_LNK = self.rflnkData["f_yk"]
        self.linkDia = self.bars["LNK"][2][0][1]
        self.linkSpacing = self.bars["LNK"][1]
        self.As_w = BarArrayDet("LNK",self.bars)["As_Prov"]
        self.d = EffectiveDepth(self.h,ConcreteCover,self.linkDia,SteelCentroid("BTM",BarArray))
        self.d2 = self.h - EffectiveDepth(self.h,ConcreteCover,self.linkDia,SteelCentroid("TOP",BarArray))
        self.z = LeverArmZ(M_ED,breadth,self.d,self.f_ck,redistribution=Moment_redist)["z"]
        self.rf_type = LeverArmZ(M_ED,breadth,self.d,self.f_ck,redistribution=Moment_redist)["rf"]
        self.K = LeverArmZ(M_ED,breadth,self.d,self.f_ck,redistribution=Moment_redist)["K"]
        self.K_prime = LeverArmZ(M_ED,breadth,self.d,self.f_ck,redistribution=Moment_redist)["K_prime"]
        self.As_Req = AsReq(M_ED,self.b,self.d,self.d2,self.z,self.f_yk_TOP,self.f_ck,self.K,self.K_prime)
        self.V_ED = V_ED
        self.ConcShearCapacity = ConcShearCapacity(self.b,self.d,self.As_Prov("TOP"),self.Ac,self.f_ck)
        self.RfShearCapacity = RfShearCapacity(self.As_w,self.linkSpacing,self.f_yk_LNK,self.b,self.z,self.f_ck)
    
    def As_Prov(self, location):
        As_Prov = BarArrayDet(location.upper(),self.bars)["As_Prov"]
        return(As_Prov)
    
    def flexuralCheck(self):
        Out = {}
        if self.As_Prov("BTM") >= self.As_Req["A_st"]:
            Out["A_st"] = "PASS"
        else:
            Out["A_st"] = "FAIL"
        if self.As_Prov("TOP") >= self.As_Req["A_sc"]:
            Out["A_sc"] = "PASS"
        else:
            Out["A_sc"] = "FAIL"
        return Out
    
    def ShearCheck(self):
        Out = {}
        V_Rdc = self.ConcShearCapacity
        b = self.V_ED
        if V_Rdc >= self.V_ED:
            Out["Check 1"] = f"V_Rdc ({V_Rdc}) >= V_ED ({b}), SHEAR RF IS NOT REQUIRED"
        else:
            Out[1] = f"V_Rdc ({V_Rdc}) <= V_ED ({b}), SHEAR RF IS REQUIRED"
            if self.RfShearCapacity >= self.V_ED:
                Out["V_RD"] = "PASS"
            else:
                Out["V_RD"] = "FAIL"
        return(Out)

def BarArrayDet(Location:str,BarArray):
    ''' Enter Bar array to give details
    :param Location: str
    :param BarArray: in the form {"Location":["class",spacing,[Layers]],"Location2":...}
    '''
    Material_Data = LoadData('data/Materials.json')["Rebar"][BarArray[Location][0]]
    f_yk = Material_Data["f_yk"]
    S = BarArray[Location][1] #spacing
    layers = BarArray[Location][2]
    Area = 0
    for layer in range(len(layers)):
        n = layers[layer][0]
        d = layers[layer][1]
        Area = Area + (n * pi * (d/2) **2)

    return({"S":S,"f_yk":f_yk, "As_Prov": round(Area,3), "Layers":layers})

def SteelCentroid(Location:str,BarArray): 
    """ Find the centroid of a layered bar arrangement. Layers should be symmetric accross the x axis. Distance is starting from bottom of bottom layer
    :param BarArray: list in the form [[number of bars,diameter of bars],[number of bars,diameter of bars]], starting from bottom layer
    :param y_spacing: c/c spacing between layers in mm
    :returns SteelCentroid: mm
    """
    weightages = []
    lengths = []
    y_spacing = BarArrayDet(Location,BarArray)["S"]
    BarLayers = BarArrayDet(Location,BarArray)["Layers"]
    a_0 = BarLayers[0][1]/2
    y = 0
    for layer in range(len(BarLayers)):
        ThisLayer = (BarLayers[layer][0]*BarLayers[layer][1])
        weightages.append(ThisLayer)
        lengths.append(layer*y_spacing)
    for length in range(len(lengths)):
        y = y + lengths[length]*(weightages[length]/sum(weightages))
    
    y_1 = y+a_0

    return(round(y_1,3))

def EffectiveDepth(height,ConcreteCover,LinkDia,SteelCentroid):
    """ Effective depth of section
    :param height: mm
    :param ConcreteCover: mm
    :param LinkDia: mm
    :param SteelCentroid: mm
    :returns EffectiveDepth: mm
    """
    a = height-ConcreteCover-LinkDia-SteelCentroid
    return(round(a,3))

def LeverArmKprime(redistribution:float = 10):
    """ Get the constant K' needed for Lever arm calculation, UK NA, McKenzie Table 6.5
    :param redistribution: % (0 to 30)
    """
    r = redistribution/100
    if r > 0.30 or r < 0:
        return ("error, value must be between 0 to 30")
    else:
        a = 1-r
        b = min(0.45, (a-0.4))
        K_prime = min(0.168,0.598*a-0.18*a**2-0.21)
        return ({"delta":round(b,3),"K_prime": round(K_prime,3)})

def LeverArmZ(moment:float,breadth:float,depth:float,f_ck:float,redistribution:float = 10):
    """ Get Lever arm of the beam
    :param moment: KNm
    :param depth: mm
    :param breadth: mm
    :param f_ck: characteristic compressive strength of concrete (MPa)
    :param redistribution: % of redistribution of moments (0 to 30)
    :returns K_prime:
    :returns K:
    :returns rf: reinforcement type
    :returns z/d:
    :returns z: mm
    """
    M = moment *1e6
    b = breadth
    d = depth
    r = redistribution

    K_prime = LeverArmKprime(r)["K_prime"]

    K_0 = M/(b*(d**2)*f_ck)

    if K_0 <= K_prime:
        rf = "singly"
        K = K_0
    else:
        rf = "doubly"
        K = K_prime
    
    
    try:
        z_per_d = min(0.5+(0.25-0.881*K)**(0.5),0.95)
    except:
        return ({"error":f"This section size is inadequate for a moment of {moment} KNm"})

    z = z_per_d * d

    return ({
        "K_prime": round(K_prime,3),
        "rf": rf,
        "K": round(K_0,3),
        "z/d": round(z_per_d,3),
        "z" : round(z,3)
    }) 

def AsReq(Moment:float, breadth:float, depth:float, depth2:float, LeverArmZ:float,f_yk:float, f_ck:float, K:float, K_prime:float, gamma_st:float = 1.15):
    ## might be erroneous
    """ Area of reinforcment required
    :param Moment: KNm
    :param breadth:
    :param depth:
    :param depth2: depth to top reinforcement centroid from top face
    :param LeverArmZ: mm
    :param f_yd: Design yield strength of reinforcement (MPa)
    """
    M = Moment * 1e6
    z = LeverArmZ
    b = breadth
    d = depth
    d_2 = depth2
    x = 2.5* (d-z)
    f_yd = f_yk/gamma_st
    e_cu3 = 0.0035
    E_s = 200000
    f_sc = E_s*((e_cu3*(x-d_2))/x)
    A_st = M/(f_yd*z)
    A_sc = max(0,((K-K_prime)*b*d**2*f_ck)/(f_sc*(d-d_2)))
    return ({"A_st": ceil(A_st),"A_sc": ceil(A_sc)})

def ConcShearCapacity(b_w, d, A_sl, A_c, f_ck, gamma_c = 1.5, N_Ed = 0):
    # Might need to verify units. might be outputting in N instead of kN
    ''' kN, Concrete shear capacity formula for members not requiring shear reinforcement (empirical) (Equation 6.2a EN 1992-1-1)
    :param b_w: smallest width of the cross-section in the tensile area
    :param d: effective depth
    :param A_sl: fully anchored tension reinforcement
    :param A_c: cross-sectional area of the concrete in mm2
    :param f_cd: design concrete strength
    :param gamma_c: concrete safety factor
    :param N_Ed: axial force in the cross-section due to loading or prestressing (in N)
    '''
    rho_1 = min(A_sl / (b_w * d), 0.02)
    k = min (1 + (200/d)**(1/2),2)
    f_cd = f_ck / gamma_c
    sigma_cp = min (N_Ed/A_c,0.2*f_cd)
    C_Rd_c = 0.18/gamma_c
    v_min = 0.035*k**(3/2)*f_ck**(1/2)
    k_1 = 0.15

    if N_Ed > 0:
        V_Rd_c = max((C_Rd_c*k*(100*rho_1*f_ck)**(1/3)+k_1*sigma_cp) * b_w * d , (v_min + k_1 * sigma_cp)* b_w *d )
    else:
        V_Rd_c = max((0.12*k*(100*rho_1*f_ck)**(1/3)*b_w*d, (0.035*k**(3/2)*f_ck**(1/2))*b_w*d))
    
    return (V_Rd_c/1000) #Convert to kN
                     
def RfShearCapacity(As_w, S, f_ywk, b_w,z,f_ck,alpha_cw = 1,theta = 21.8, alpha = 90, gamma_c = 1.5, gamma_y = 1.15):
    '''kN Shear Capacity of a section requiring shear reinforcement
    :param As_w: cross sectional area of shear reinforcement
    :param S: Spacing of reinforcement
    :param f_ywk: Characteristic yield of shear reinforcement
    :param b_w: smallest width of the cross section in the tensile area
    :param z: lever arm of the section
    :param v_1: empirical factor to take account of the actual stress distribution in the concrete
    :param f_cd: design concrete strength
    :param alpha_cw: a coefficient taking account of any applied compression force (for non-prestressed structures alpha_cw = 1)
    :param theta: between 21.8 and 45 degrees (enter in degrees)
    :param alpha: angle between shear reinforcement and the beam axis, vertical bars are 90 degrees (enter in degrees)
    '''
    # V_RD > V_ED
    theta = radians(theta)
    alpha = radians(alpha)
    f_ywd = f_ywk / gamma_y
    V_Rd_s = (As_w/S)*z*f_ywd*(cot(theta)+cot(alpha))*sin(alpha)

    f_cd = f_ck / gamma_c
    v = 0.6*(1 - (f_ck/250))
    v_1 = v*(1 - cos(alpha))
    V_Rd_max = (alpha_cw*b_w*z*v_1*f_cd)*(cot(theta)+cot(alpha))/(1+cot(theta)**2)

    V_Rd = min(V_Rd_s, V_Rd_max)
    return (V_Rd/1000) # convert to kN

# def BarNotation(BarArray):
#     T = []
#     B = []
#     L = []
#     for i in range(len(BarArray["T"])):
#         for j in range(len(BarArray["T"][i])):
#             T.append[BarArray[i]]

main()