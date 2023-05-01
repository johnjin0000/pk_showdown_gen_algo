import numpy as np
import random


def packed_format_str(string):
    return string.lower().replace(" ", "").replace("-", "")


def get_packed_moves(moves):
    packed_moves = []
    for move in moves:
        packed_moves.append(packed_format_str(move))

    return ",".join(packed_moves)


def get_packed_evs(evs):
    evs = evs.split("/")
    packed_evs = ",".join(evs)
    packed_evs = packed_evs.replace("0", "")
    return packed_evs


def select_pokemon(pokemon, usage_dist, n_teams):
    selected_pokemon = []
    for i in range(n_teams):
        indices = np.arange(len(pokemon))
        selected_pokemon_idxs = np.random.choice(indices, size=6, replace=False, p=usage_dist)
        sample = [pokemon[i] for i in selected_pokemon_idxs]
        # check for Zapdos and slowking
        while (("Zapdos" in sample and "Zapdos-Galar" in sample) or
               ("Slowking" in sample and "Slowking-Galar") in sample):
            selected_pokemon_idxs = np.random.choice(indices, size=6, replace=False, p=usage_dist)
            sample = [pokemon[i] for i in selected_pokemon_idxs]
        selected_pokemon.append(sample)
    return selected_pokemon


def sample_pokemon_info(pokemon_info, header, n_choices):
    pk_header_info = pokemon_info[header]
    total_percent = 0
    for data in pk_header_info:
        if data != "Other":
            total_percent += pk_header_info[data]
    choices = []
    weights = []
    for data in pk_header_info:
        if data != "Other":
            choices.append(data)
            weights.append(pk_header_info[data] / total_percent)

    indices = np.arange(len(choices))
    selected_choice_idxs = np.random.choice(indices, size=n_choices, replace=False, p=weights)
    selected = [choices[i] for i in selected_choice_idxs]
    if len(selected) == 1:
        return selected[0]
    return selected


def sample_pokemon_details(selected_teams, poke_dict):
    teams = []
    for team in selected_teams:
        sampled_team = []
        for pokemon in team:
            pokemon_info = poke_dict[pokemon]
            ability = sample_pokemon_info(pokemon_info, "Abilities", 1)
            moves = sample_pokemon_info(pokemon_info, "Moves", 4)
            item = sample_pokemon_info(pokemon_info, "Items", 1)
            nature_spread = sample_pokemon_info(pokemon_info, "Spreads", 1)
            nature, spread = nature_spread.split(":")
            sampled_team.append([pokemon, item, ability, moves, nature, spread])
        teams.append(sampled_team)
    return teams


def create_teams(pokemon, usage_dist, poke_dict, n_teams):
    selected_teams = select_pokemon(pokemon, usage_dist, n_teams)   # Samples 6 pokemon
    teams = sample_pokemon_details(selected_teams, poke_dict)       # Fills in info about their moves, abilities, etc.
    # use pokemon showdown packed team format
    packed_teams = create_packed_teams(teams)                       # Reformats to packed format
    return teams, packed_teams


def create_packed_teams(teams):
    packed_teams = []
    for team in teams:
        pokemon_strs = []
        for pokemon_info in team:
            pokemon, item, ability, moves, nature, evs = pokemon_info
            pokemon = packed_format_str(pokemon)
            item = packed_format_str(item)
            ability = packed_format_str(ability)
            moves = get_packed_moves(moves)
            evs = get_packed_evs(evs)
            pokemon_strs.append(pokemon + "||" + item + "|" + ability + "|" +
                                moves + "|" + nature + "|" + evs + "|||||")
        packed_teams.append("]".join(pokemon_strs))

    return packed_teams


def select_parents(teams, fitness_scores):
    indices = np.arange(len(teams))
    selected_choice_idxs = np.random.choice(indices, size=2, replace=False, p=fitness_scores)
    selected = [teams[i] for i in selected_choice_idxs]
    return selected


# fill in pokemon in teams if there were dupes
def fill_teams(child, parent):
    for i in range(6 - len(child)):
        j = 0
        pokemon = parent[j][0]
        cur_child_team = [child[k][0] for k in range(len(child))]
        while ((pokemon in cur_child_team) or
               (pokemon == "Zapdos" and "Zapdos-Galar" in cur_child_team) or
               (pokemon == "Zapdos-Galar" and "Zapdos" in cur_child_team) or
               (pokemon == "Slowking" and "Slowking-Galar" in cur_child_team) or
               (pokemon == "Slowking-Galar" and "Slowking" in cur_child_team)):
            j += 1
            pokemon = parent[j][0]
        child.append(parent[j])
    return child


def crossover_parents(parents):
    parent_1, parent_2 = parents
    pivot = random.randint(1, 4)
    child_1, child_2 = parent_1[:pivot], parent_2[:pivot]
    for i in range(pivot, 6):
        # child 1
        parent_2_pokemon = parent_2[i][0]
        if parent_2_pokemon not in [child_1[j][0] for j in range(len(child_1))]:
            child_1.append(parent_2[i])
        # child 2
        parent_1_pokemon = parent_1[i][0]
        if parent_1_pokemon not in [child_2[j][0] for j in range(len(child_2))]:
            child_2.append(parent_1[i])

    # now fill in pokemon in teams if there were dupes
    child_1 = fill_teams(child_1, parent_1)
    child_2 = fill_teams(child_2, parent_2)

    return child_1, child_2


def get_new_generation(teams, fitness_scores, crossover_rate):
    n_teams = len(teams)
    next_gen_teams = []
    for i in range(n_teams // 2):
        parents = select_parents(teams, fitness_scores)
        if random.random() < crossover_rate:
            child_1, child_2 = crossover_parents(parents)
            next_gen_teams.append(child_1)
            next_gen_teams.append(child_2)
        else:
            next_gen_teams.append(parents[0])
            next_gen_teams.append(parents[1])
    combined = [(fitness_scores[i], teams[i]) for i in range(len(teams))]
    combined.sort(reverse=True)
    for i in range(n_teams - 2 * (n_teams // 2)):
        next_gen_teams.append(combined[i][1])

    return next_gen_teams



def mutate(teams, mutation_rate, poke_dict):
    next_gen_teams = []
    for team in teams:
        next_gen_teams.append(team)
        if random.random() < mutation_rate:
            mut_stat = random.randint(0, 3)
            mut_pokemon_idx = random.randint(0, 5)
            mut_pokemon = next_gen_teams[-1][mut_pokemon_idx]
            pokemon_info = poke_dict[team[mut_pokemon_idx][0]]
            if mut_stat == 0:
                ability = sample_pokemon_info(pokemon_info, "Abilities", 1)
                mut_pokemon[2] = ability
            elif mut_stat == 1:
                moves = sample_pokemon_info(pokemon_info, "Moves", 4)
                mut_pokemon[3] = moves
            elif mut_stat == 2:
                item = sample_pokemon_info(pokemon_info, "Items", 1)
                mut_pokemon[1] = item
            else:
                nature_spread = sample_pokemon_info(pokemon_info, "Spreads", 1)
                nature, spread = nature_spread.split(":")
                mut_pokemon[4] = nature
                mut_pokemon[5] = spread

    return next_gen_teams, create_packed_teams(next_gen_teams)

