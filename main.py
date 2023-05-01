import asyncio
import pickle

from parse import usage_data, pokemon_data
from teams_helper import create_teams
from genalgo import gen_algo
from dqn_player import *
from poke_env import LocalhostServerConfiguration, PlayerConfiguration
from gym.utils.env_checker import check_env


async def main():
    pokemon, usage_dist = usage_data()
    poke_dict = pokemon_data()
    teams = []

    crossevals = 5
    n_teams = 50
    n_gens = 10
    mutation_rate = .01
    crossover_rate = .8
    num_different_teams = 10
    train_steps = 1000

    teams, packed_teams = create_teams(pokemon, usage_dist, poke_dict, n_teams)
    agentteam = teams[0]
    teams.append(agentteam)
    agent = None
    for i in range(n_gens):
        # Train agent
        agent = DQNPlayer(
            battle_format="gen8ou",
            player_configuration=PlayerConfiguration("gen" + str(i) + "user" + str(i), None),
            server_configuration=LocalhostServerConfiguration,
            max_concurrent_battles=n_teams,
            team=agentteam
        )
        if i == 0:
            agent.create_model()
            check_env(agent)

        # We want some variety in the teams the opponent uses
        for j in range(num_different_teams):
            opponent = DQNPlayer(battle_format="gen8ou",
                                 player_configuration=PlayerConfiguration("gen" + str(i) + "opponent" + str(j), None),
                                 server_configuration=LocalhostServerConfiguration,
                                 max_concurrent_battles=n_teams,
                                 team=random.choice(teams)  # Pick a random team
                                 )
            agent.train(opponent, train_steps)
        # Search for team via GA
        teams, packed_teams, bestteam = gen_algo(teams, packed_teams, poke_dict, mutation_rate, crossover_rate, i,
                                                 crossevals)
        agentteam = bestteam
        teams.append(agentteam)
    # Give results to user
    agent.save_model()
    print(agentteam)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
