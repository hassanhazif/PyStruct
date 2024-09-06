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

#print(BarCentroidY(BarArray))