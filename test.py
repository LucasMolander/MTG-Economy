import json

from set_util import SetUtil

from print_util import PrintUtil

header = ['Col A', 'Col B']
rows = [['a1', 'b1'], ['a2', 'b2']]

myTable = PrintUtil.getTable(header, rows)

print(myTable)

# excludeSets = ['Homelands']

# with open('Old Rarities.json', 'r') as f:
#     # Cards include name and rarity fields
#     setNameToCards = json.loads(f.read())


# for setName in setNameToCards:
#     if (setName in excludeSets):
#         continue

#     rarities = setNameToCards[setName]

#     with open(setName, 'r') as f:
#         prices = json.loads(f.read())

#     print('%s: %s, %s' % (setName, len(rarities), len(prices)))
