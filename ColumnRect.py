from Equations import *

BarArray = {"TOP":["T",20,[[2,16]]], 
            "BTM":["T",20,[[3,16],[2,16]]],
            "LNK":["R",100,[[2,8]]]}

## Moment Array

class RCC_ColumnRect:
    def __init__ (self, name:str, M_EDArray:float, N_ED:float, x:float, y:float, BarArray, Concrete_Material:str, Moment_redist:float = 10, ConcreteCover = 25):
        """Define a Rectangular column
        :param name: Name of the element
        :param M_ED: End Moments array
        :param N_ED: Axial Load Array
        :param x: major axis length
        :param y: minor axis length
        :param BarArray: Reinforcement
        :param Concrete_Material: Material class of concrete
        :param Moment_redist: percentage moment redistribution
        :param ConcreteCover: cover to reinforcement
        """
        self.name = name
        self.concreteData = LoadData('data/Materials.json')["Concrete"][Concrete_Material]
        self.Ac = x * y
        self.bars = BarArray
        self.f_ck = self.concreteData["f_ck"]
        self.f_yk_TOP = self.rftopData["f_yk"]
        self.f_yk_BTM = self.rfbtmData["f_yk"]
        self.f_yk_LNK = self.rflnkData["f_yk"]
        self.linkDia = self.bars["LNK"][2][0][1]
        self.linkSpacing = self.bars["LNK"][1]
        self.As_w = BarArrayDet("LNK",self.bars)["As_Prov"]
        self.d = EffectiveDepth(self.h,ConcreteCover,self.linkDia,SteelCentroid("BTM",BarArray))
        self.d2 = self.h - EffectiveDepth(self.h,ConcreteCover,self.linkDia,SteelCentroid("TOP",BarArray))

    def As_Prov(self, location):
        As_Prov = BarArrayDet(location.upper(),self.bars)["As_Prov"]
        return(As_Prov)
    
    ## Axial force check
    ## Bending check
    ## Biaxial Bending
