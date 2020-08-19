import plates
allPlates = ["SYDNEY"]

for p in allPlates:
    status, expires = plates.Plates(p)
    print(p, status, expires)



