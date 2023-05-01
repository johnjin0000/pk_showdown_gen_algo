import asyncio
from fitness import calc_fitness
from teams_helper import  get_new_generation, mutate

async def gen_algo(teams, packed_teams, poke_dict, mutrate, crossrate, current_gen, num_crossevals):
    fitness_scores = await calc_fitness(packed_teams, current_gen, num_crossevals)
    teams = get_new_generation(teams, fitness_scores, crossrate)
    teams, packed_teams = mutate(teams, mutrate, poke_dict)
    team1, team2 = best_teams(fitness_scores, teams)
    return teams, packed_teams, team1, team2
    

def best_teams(fitness_scores, teams):
    combined = [(fitness_scores[i], teams[i]) for i in range(len(teams))]
    combined.sort(reverse=True)
    return combined[0] # Best team