import json
from math import tan

def LoadData(file):
    with open(file) as file:
        data = json.load(file)
    return data

def cot(x):
    y = 1/tan(x)
    return y