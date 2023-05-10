import json

with open("rules.json","r") as f:
    rules = json.load(f)

print(rules['rules'])