from Equations import *

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

        self.name = name #Name of the element
        self.concreteMaterial = Concrete_Material #Concrete material
        self.concreteData = LoadData('data/Materials.json')["Concrete"][Concrete_Material] #Concrete Data
        self.Ac = breadth * height #Area
        self.bars = BarArray #Bar Array
        self.rftopData = LoadData('data/Materials.json')["Rebar"][self.bars["TOP"][0]]
        self.rfbtmData = LoadData('data/Materials.json')["Rebar"][self.bars["BTM"][0]]
        self.rflnkData = LoadData('data/Materials.json')["Rebar"][self.bars["LNK"][0]]
        self.b = breadth #Breadth
        self.h = height #Height 
        self.f_ck = self.concreteData["f_ck"]["value"]
        self.f_yk_TOP = self.rftopData["f_yk"]["value"]
        self.f_yk_BTM = self.rfbtmData["f_yk"]["value"]
        self.f_yk_LNK = self.rflnkData["f_yk"]["value"]
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

main()