import json

def ConcreteCover(S_class="S4",
X_class="XC2",Bar_size=16,Nominal_max_aggregate_size=20, DeltaC_dur_add=0,DeltaC_dur_gemma=0,DeltaC_dur_st = 0,Bar_arrangement="Seperated",Numberof_BundledBars=4):

    with open('data/Params.json') as file:
        data = json.load(file)

    #S_class = "S4"
    #X_class = "XC2"
    #Bar_arrangement = "Seperated" # "Seperated" or "Bundled"
    #Bar_size = 16 # in mm
    #Nominal_max_aggregate_size = 20 # in mm

    #DeltaC_dur_gemma = 0 #additive safety element, see 4.4.1.2 (6)
    #DeltaC_dur_st = 0 # reduction of minimum cover for use of stainless steel, see 4.4.1.2 (7)
    #DeltaC_dur_add = 0 # reduction of minimum cover for use of additional protection, see 4.4.1.2 (8)

    ## Bundled bars
    #Numberof_BundledBars = 4 # for bundled bars

    if Bar_arrangement == "Seperated":
        C_min_b = Bar_size
    elif Bar_arrangement == "Bundled":
        Bar_eqsize = Bar_size * Numberof_BundledBars ** (1/2)
        C_min_b = Bar_eqsize
    
    C_min_dur = data["Table 4.4N"]["Data"][S_class][X_class] # minimum cover due to environmental conditions
    C_min = max(C_min_b, (C_min_dur + DeltaC_dur_gemma - DeltaC_dur_st - DeltaC_dur_add), 10) # minimum cover, c_min
    return(C_min)

print(ConcreteCover(S_class="S4",X_class="XC2"))