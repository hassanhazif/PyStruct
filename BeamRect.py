from Prelims import LoadData
from math import ceil
from math import pi

BarArray = {"TOP":["T",0,[[2,12]]], "BTM":["T",20,[[2,10],[2,10]]],"LNK":["R",100,[[2,6]]]}

def main():
    B1 = RCC_BeamRect("B1",50,0,0,250,400,BarArray,"C30/37")
    print(B1.As_Prov("lnk"))
    #print(BarArrayDet("BTM",BarArray2))
    #print(BarArray2["BTM"])
    #print(SteelCentroid("BTM",BarArray2))

class RCC_BeamRect:
    def __init__(self, name:str, Moment:float, Shear:float, Torsion:float, breadth:float, height:float, BarArray, Concrete_Material:str, BarYSpacing:float=25, Moment_redist:float = 10, ConcreteCover = 25, LinkDia = 8):
        """ Define a Reinforced Concrete Rectangular Beam
        :param name:
        :param Moment: Design moment in kNm
        :param Shear: Design Shear in kN
        :param Torsion: Design torsion in kPa
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
        self.d = EffectiveDepth(self.h,ConcreteCover,LinkDia,SteelCentroid("BTM",BarArray))
        self.z = LeverArmZ(Moment,breadth,self.d,self.f_ck,redistribution=Moment_redist)["z"]

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
        Area = Area + n * pi * (d/2) **2

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
    """ Get Lever arm of the beam, This function is incomplete
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
    
    K = M/(b*(d**2)*f_ck)
    try:
        z_per_d = min(0.5+(0.25-0.881*K)**(0.5),0.95)
    except:
        return ({"error":f"This section size is inadequate for a moment of {moment} KNm"})

    z = z_per_d * d

    if K <= K_prime:
        rf = "singly"
    else:
        rf = "doubly"

    return ({
        "K_prime": round(K_prime,3),
        "rf": rf,
        "K": round(K,3),
        "z/d": round(z_per_d,3),
        "z" : round(z,3)
    }) 

def AstReq(Moment:float,LeverArmZ:float,f_yd:float):
    """ Area of reinforcing steel required
    :param Moment: KNm
    :param LeverArmZ: mm
    :param f_yd: Design yield strength of reinforcement (MPa)
    """
    M = Moment * 1e6
    z = LeverArmZ

    A_st = M/(f_yd*z)

    return ({"A_st": ceil(A_st)})

# def BarNotation(BarArray):
#     T = []
#     B = []
#     L = []
#     for i in range(len(BarArray["T"])):
#         for j in range(len(BarArray["T"][i])):
#             T.append[BarArray[i]]

main()