import asyncio
from fitness import calc_fitness
from teams_helper import  get_new_generation, mutate

async def gen_algo(teams, packed_teams, poke_dict, mutrate, crossrate, current_gen, num_crossevals):
    fitness_scores = await calc_fitness(packed_teams, current_gen, num_crossevals)
    teams = get_new_generation(teams, fitness_scores, crossrate)
    teams, packed_teams = mutate(teams, mutrate, poke_dict)
    return teams, packed_teams