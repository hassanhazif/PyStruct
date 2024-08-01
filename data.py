import json

with open('data/Params.json') as file:
    data = json.load(file)

a = "As_prov"
b = "phi_abc"


# display(Markdown('*some markdown* $\phi$'))
# If you particularly want to display maths, this is more direct:
# display(Latex('\phi'))

Params = data["Params"]
