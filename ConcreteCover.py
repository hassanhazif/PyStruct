import json

with open ('data/Params.json', 'r') as file:
    data = json.load(file)
print(data)