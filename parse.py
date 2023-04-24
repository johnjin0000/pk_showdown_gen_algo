def get_usage_data(line):
    data = line.split("|")
    pokemon = data[2].strip()
    usage = float(data[3].strip()[:-1])
    return pokemon, usage


def create_dist(poke_usage):
    # get softmax
    total_percent = 0
    poke_usage_filt = dict()
    for pokemon in poke_usage:
        if poke_usage[pokemon] >= 1:
            poke_usage_filt[pokemon] = poke_usage[pokemon]

    for pokemon in poke_usage_filt:
        total_percent += poke_usage_filt[pokemon]
    for pokemon in poke_usage_filt:
        poke_usage_filt[pokemon] = poke_usage_filt[pokemon] / total_percent

    softmax = [(pokemon, poke_usage_filt[pokemon]) for pokemon in poke_usage_filt]

    pokemon = [data[0] for data in softmax]
    usage = [data[1] for data in softmax]

    return pokemon, usage


def usage_data():
    poke_usage = dict()
    with open("data/gen8ou-1760-usage.txt", "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i < 5 or i == len(lines) - 1:
                continue
            pokemon, usage = get_usage_data(line.strip())
            poke_usage[pokemon] = usage

    pokemon, usage_dist = create_dist(poke_usage)

    return pokemon, usage_dist


def pokedata_get_inputs(header, lines, poke_dict):
    poke_dict[header] = dict()
    idxs_skipped = 0

    for line in lines:
        line = line.strip()
        if line == "":
            return idxs_skipped
        entry, usage = " ".join(line.split()[:-1]), line.split()[-1]
        usage = float(usage[:-1]) / 100
        poke_dict[header][entry] = usage
        idxs_skipped += 1
    return idxs_skipped


def parse_poke_data(poke_data, lines):
    # already pre-edited the document (removed pokemon with usage below 1%),
    # cleaned up formatting, etc.
    pokemon = ""
    for i in range(len(lines)):
        line = lines[i].strip()
        if line == "Pokemon":
            pokemon = lines[i + 1].strip()
            poke_data[pokemon] = dict()
            # skip random data and empty spaces
            i += 6
        elif line in ["Abilities", "Items", "Spreads", "Moves", "Teammates"]:
            idxs_skipped = pokedata_get_inputs(line, lines[i + 1:], poke_data[pokemon])
            i += idxs_skipped
        elif line == "Checks and Counters":
            while line != "":
                i += 1
                line = lines[i].strip()


def pokemon_data():
    poke_data = dict()
    with open("data/gen8ou-1760-pokedata.txt", "r") as f:
        lines = f.readlines()
        parse_poke_data(poke_data, lines)
    return poke_data
