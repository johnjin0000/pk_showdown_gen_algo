import asyncio
from parse import usage_data, pokemon_data
from fitness import calc_fitness
from teams_helper import create_teams, get_new_generation, mutate


async def gen_algo(n_gens, mutrate, crossrate, crossevals, poke_dict):
    for i in range(n_gens):
        print("gen", i)
        fitness_scores = await calc_fitness(packed_teams, i, crossevals)
        teams = get_new_generation(teams, fitness_scores, crossrate)
        teams, packed_teams = mutate(teams, mutrate, poke_dict)

    combined = [(fitness_scores[i], teams[i]) for i in range(len(teams))]
    combined.sort(reverse=True)
    print([x[0] for x in combined])
    print(combined[0])
    print(combined[1])
    print(combined[2])