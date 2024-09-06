from Prelims import LoadData

# Layered Bar Centroids

BarArray = [[4,16],[4,16]]

def BarCentroid(BarArray:list,y_spacing=12): 
    # Units are in mm
    # From centroid of bar, bar arrangement should be symmetric
    weightages = []
    lengths = []
    y = 0
    for layer in range(len(BarArray)):
        ThisLayer = (BarArray[layer][0]*BarArray[layer][1])
        weightages.append(ThisLayer)
        lengths.append(layer*y_spacing)
    
    for length in range(len(lengths)):
        y = y + lengths[length]*(weightages[length]/sum(weightages))

    return(y)

def LeverArmZ(breadth:float,depth:float,moment:float,f_ck:float):
    """ Get Lever arm of the beam, This function is incomplete
    :param depth: mm
    :param breadth: mm
    :param moment: KNm
    :param f_ck: MPa
    """
    M = moment
    b = breadth
    d = depth
    
    K_i = M/(b*(d**2)*f_ck)
    z = (0.5+(0.25-0.881*K_i)**(0.5))*d
    return ({
        "K_i": K_i,
        "z": z
    })


print(LeverArmZ(250,420,80,25))