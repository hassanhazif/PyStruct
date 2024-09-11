from Prelims import LoadData
from math import ceil
from math import pi

BarArray = {"TOP":["T",0,[[4,12]]], "BTM":["T",20,[[1,10]]],"LNK":["R",100,[[2,8]]]}

def main():
    B1 = RCC_BeamRect("B1",150,0,0,250,250,BarArray,"C30/37")
    print(f"A req st: {B1.As_Req['A_st']}")
    print(f"A prov st: {B1.As_Prov('btm')}\n")
    print(f"A req sc: {B1.As_Req['A_sc']}")
    print(f"A prov sc: {B1.As_Prov('top')}")
    #print(BarArrayDet("BTM",BarArray2))
    #print(BarArray2["BTM"])
    #print(SteelCentroid("BTM",BarArray2))

class RCC_BeamRect:
    def __init__(self, name:str, M_ED:float, V_ED:float, T_ED:float, breadth:float, height:float, BarArray, Concrete_Material:str, Moment_redist:float = 10, ConcreteCover = 0):
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
        self.b = breadth
        self.h = height
        self.bars = BarArray
        self.f_ck = self.concreteData["f_ck"]
        self.linkDia = self.bars["LNK"][2][0][1]
        self.d = EffectiveDepth(self.h,ConcreteCover,self.linkDia,SteelCentroid("BTM",BarArray))
        self.d2 = self.h - EffectiveDepth(self.h,ConcreteCover,self.linkDia,SteelCentroid("TOP",BarArray))
        self.z = LeverArmZ(M_ED,breadth,self.d,self.f_ck,redistribution=Moment_redist)["z"]
        self.rf_type = LeverArmZ(M_ED,breadth,self.d,self.f_ck,redistribution=Moment_redist)["rf"]
        self.K = LeverArmZ(M_ED,breadth,self.d,self.f_ck,redistribution=Moment_redist)["K"]
        self.K_prime = LeverArmZ(M_ED,breadth,self.d,self.f_ck,redistribution=Moment_redist)["K_prime"]
        self.As_Req = AsReq(M_ED,self.b,self.d,self.d2,self.z,460,self.f_ck,self.K,self.K_prime)

    def As_Prov(self, location):
        As_Prov = BarArrayDet(location.upper(),self.bars)["As_Prov"]
        return(As_Prov)

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
    """ Area of tension reinforcment required
    :param Moment: KNm
    :param LeverArmZ: mm
    :param f_yd: Design yield strength of reinforcement (MPa)
    :param x: d - neutral axis
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
    A_sc = ((K-K_prime)*b*d**2*f_ck)/(f_sc*(d-d_2))
    return ({"A_st": ceil(A_st),"A_sc": ceil(A_sc)})

# def BarNotation(BarArray):
#     T = []
#     B = []
#     L = []
#     for i in range(len(BarArray["T"])):
#         for j in range(len(BarArray["T"][i])):
#             T.append[BarArray[i]]

main()