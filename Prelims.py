import json

def LoadData(file):
    with open(file) as file:
        data = json.load(file)
    return data