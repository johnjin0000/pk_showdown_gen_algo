import asyncio

from parse import usage_data, pokemon_data
from fitness import calc_fitness
from teams_helper import create_teams, get_new_generation, mutate


async def main():
    pokemon, usage_dist = usage_data()
    poke_dict = pokemon_data()

    n_teams = 30
    n_gens = 5
    mutation_rate = .01
    crossover_rate = .8
    teams, packed_teams = create_teams(pokemon, usage_dist, poke_dict, n_teams)
    fitness_scores = None
    for i in range(n_gens):
        print("gen", i)
        fitness_scores = await calc_fitness(packed_teams, i)
        teams = get_new_generation(teams, fitness_scores, crossover_rate)
        teams, packed_teams = mutate(teams, mutation_rate, poke_dict)

    combined = [(fitness_scores[i], teams[i]) for i in range(len(teams))]
    combined.sort(reverse=True)
    print(combined[0])
    print(combined[1])
    print(combined[2])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
