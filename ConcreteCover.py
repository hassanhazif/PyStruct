from Prelims import LoadData

def ConcreteCover(file = 'data/EC2.json', S_class="S4", X_class="XC2",Bar_size=16, Nominal_max_aggregate_size=20, DeltaC_dur_add=0, DeltaC_dur_gemma=0, DeltaC_dur_st = 0, Bar_arrangement="Seperated", Numberof_BundledBars=4):

    data = LoadData(file)

    if Bar_arrangement == "Seperated":
        C_min_b = Bar_size
    elif Bar_arrangement == "Bundled":
        Bar_eqsize = Bar_size * Numberof_BundledBars ** (1/2)
        C_min_b = Bar_eqsize
    
    C_min_dur = data["Table 4.4N"][S_class][X_class] # minimum cover due to environmental conditions
    C_min = max(C_min_b, (C_min_dur + DeltaC_dur_gemma - DeltaC_dur_st - DeltaC_dur_add), 10) # minimum cover, c_min
    return(C_min)

print(ConcreteCover(S_class="S4",X_class="XC2"))