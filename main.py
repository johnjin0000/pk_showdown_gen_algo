import asyncio

from parse import usage_data, pokemon_data
from fitness import calc_fitness
from teams_helper import create_teams, get_new_generation, mutate
from genalgo import gen_algo


async def main():
    pokemon, usage_dist = usage_data()
    poke_dict = pokemon_data()

    crossevals = 5
    n_teams = 50
    n_gens = 10
    mutation_rate = .01
    crossover_rate = .8

    teams, packed_teams = create_teams(pokemon, usage_dist, poke_dict, n_teams)
    fitness_scores = None
    agentteam = teams[0]
    for i in range(n_gens):
        # Initialize DQN model using agentteam
        # Train DQN
        teams, packed_teams = gen_algo(teams, packed_teams, poke_dict, mutation_rate, crossover_rate, i, crossevals)
        


    
def best_teams(fitness_scores, teams):
    combined = [(fitness_scores[i], teams[i]) for i in range(len(teams))]
    combined.sort(reverse=True)
    print([x[0] for x in combined])
    print(combined[0])
    print(combined[1])
    print(combined[2])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
