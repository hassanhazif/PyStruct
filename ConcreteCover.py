import json

with open('data/Params.json') as file:
    data = json.load(file)

S_class = "S4"
X_class = "XS3"
C_min_dur = data["Table 4.4N"]["Data"][S_class][X_class]


print(C_min_dur)