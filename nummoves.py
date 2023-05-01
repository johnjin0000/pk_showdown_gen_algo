
moves = set()
with open("data/gen8ou-1760-pokedata.txt", "r") as f:
    lines = f.readlines()
    for i in range(len(lines)):
        line = lines[i].split()
        if not(line and line[0] == "Moves"):
            continue
        j = i+1 # Moves line found, start on line after
        moveline = lines[j].split()
        while moveline:
            moves.add(" ".join(moveline[:-1]))
            j += 1
            moveline = lines[j].split()
print(len(moves))
            
