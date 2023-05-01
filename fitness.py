import asyncio

import re
import math
import numpy as np
import poke_env
from poke_env.player import SimpleHeuristicsPlayer, cross_evaluate
from poke_env import LocalhostServerConfiguration, PlayerConfiguration
from poke_env.teambuilder import Teambuilder


async def calc_fitness(teams, gen, crossevals):
    players = [
        SimpleDQNPlayer(
            battle_format="gen8ou",
            player_configuration=PlayerConfiguration("gen" + str(gen) + "user" + str(i), None),
            server_configuration=LocalhostServerConfiguration,
            max_concurrent_battles=50,
            team=teams[i],
        ) for i in range(len(teams))
    ]

    cross_evaluation = await cross_evaluate(players, n_challenges=crossevals)
    fitness_dict = dict()

    for user in cross_evaluation:
        score = 0
        for matchup in cross_evaluation[user]:
            if user != matchup:
                score += cross_evaluation[user][matchup]
        fitness_dict[int(re.search(r'(\d+)\D*$', user).group())] = score

    fitness_scores = [0 for i in range(len(teams))]
    total_matches = math.comb(len(teams), 2)
    for user in fitness_dict:
        fitness_scores[user] = fitness_dict[user] / total_matches

    return fitness_scores
