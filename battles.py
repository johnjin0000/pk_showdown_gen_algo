import asyncio

import re
import math
import numpy as np
import poke_env
from poke_env.player import SimpleHeuristicsPlayer, cross_evaluate
from poke_env import LocalhostServerConfiguration, PlayerConfiguration
from poke_env.teambuilder import Teambuilder
from teams_helper import create_packed_teams, create_teams
from parse import *


def get_random_team():
    pokemon, usage_dist = usage_data()
    poke_dict = pokemon_data()

    n_teams = 50
    n_gens = 10
    mutation_rate = .02
    crossover_rate = .9
    teams, packed_teams = create_teams(pokemon, usage_dist, poke_dict, n_teams)
    return packed_teams[0]


async def main():
    team = [[['Krookodile', 'Choice Scarf', 'Moxie',
              ['Stone Edge', 'Taunt', 'Knock Off', 'Earthquake'], 'Adamant', '0/252/0/0/0/248'],
             ['Landorus-Therian', 'Leftovers', 'Intimidate',
              ['U-turn', 'Toxic', 'Earthquake', 'Knock Off'], 'Careful', '252/0/4/0/252/0'],
             ['Blaziken', 'Air Balloon', 'Speed Boost',
              ['Flare Blitz', 'Swords Dance', 'Thunder Punch', 'Close Combat'], 'Adamant', '144/252/0/0/0/112'],
             ['Heatran', 'Air Balloon', 'Flame Body',
              ['Taunt', 'Flamethrower', 'Protect', 'Magma Storm'], 'Modest', '0/0/0/252/4/252'],
             ['Tapu Koko', 'Heavy-Duty Boots', 'Electric Surge',
              ['Thunderbolt', 'Dazzling Gleam', 'Roost', 'Defog'], 'Timid', '0/0/0/252/4/252'],
             ['Volcanion', 'Choice Specs', 'Water Absorb',
              ['Flamethrower', 'Steam Eruption', 'Sludge Bomb', 'Earth Power'], 'Modest', '0/0/0/252/4/252']]]

    gen_alg_team = create_packed_teams(team)[0]

    gen_alg_player = SimpleHeuristicsPlayer(
        battle_format="gen8ou",
        player_configuration=PlayerConfiguration("gen algo", None),
        server_configuration=LocalhostServerConfiguration,
        max_concurrent_battles=50,
        team=gen_alg_team
    )

    team_2 = [[['Tapu Lele', 'Choice Scarf', 'Psychic Surge', ['Focus Blast', 'Psychic', 'Thunderbolt', 'Moonblast'],
                'Modest', '0/0/0/252/4/252'],
               ['Ninetales-Alola', 'Light Clay', 'Snow Warning', ['Aurora Veil', 'Freeze-Dry', 'Moonblast', 'Blizzard'],
                'Timid', '4/0/0/252/0/252'], ['Aegislash', 'Choice Specs', 'Stance Change',
                                              ['Flash Cannon', 'Close Combat', 'Shadow Sneak', 'Shadow Ball'], 'Rash',
                                              '0/4/0/252/0/252'],
               ['Blacephalon', 'Choice Specs', 'Beast Boost', ['Shadow Ball', 'Flamethrower', 'Overheat', 'Trick'],
                'Timid', '0/0/0/252/4/252'],
               ['Crawdaunt', 'Choice Band', 'Adaptability', ['Knock Off', 'Crabhammer', 'Aqua Jet', 'Crunch'],
                'Adamant', '0/252/0/0/4/252'],
               ['Clefable', 'Leftovers', 'Magic Guard', ['Soft-Boiled', 'Moonblast', 'Knock Off', 'Calm Mind'], 'Bold',
                '252/0/188/0/0/68']]]
    other_team = create_packed_teams(team_2)[0]

    other_player = SimpleHeuristicsPlayer(
        battle_format="gen8ou",
        player_configuration=PlayerConfiguration("other player", None),
        server_configuration=LocalhostServerConfiguration,
        max_concurrent_battles=50,
        team=other_team
    )

    random_player = SimpleHeuristicsPlayer(
        battle_format="gen8ou",
        player_configuration=PlayerConfiguration("random3", None),
        server_configuration=LocalhostServerConfiguration,
        max_concurrent_battles=50,
        team=get_random_team()
    )

    sample_team = """
Urshifu-Rapid-Strike @ Choice Band  
Ability: Unseen Fist  
EVs: 252 Atk / 4 Def / 252 Spe  
Jolly Nature  
- Surging Strikes  
- Close Combat  
- Aqua Jet  
- U-turn  

Heatran @ Air Balloon  
Ability: Flash Fire  
EVs: 252 SpA / 4 SpD / 252 Spe  
Timid Nature  
IVs: 0 Atk  
- Magma Storm  
- Taunt  
- Earth Power  
- Stealth Rock  

Rotom-Wash @ Leftovers  
Ability: Levitate  
Shiny: Yes  
EVs: 252 HP / 248 SpD / 8 Spe  
Calm Nature  
IVs: 0 Atk  
- Volt Switch  
- Hydro Pump  
- Thunder Wave  
- Pain Split  

Landorus-Therian (M) @ Leftovers  
Ability: Intimidate  
EVs: 248 HP / 8 Def / 252 SpD  
Careful Nature  
IVs: 23 Spe  
- Defog  
- Earthquake  
- U-turn  
- Knock Off  

Tapu Lele @ Choice Scarf  
Ability: Psychic Surge  
EVs: 252 SpA / 4 SpD / 252 Spe  
Timid Nature  
IVs: 0 Atk  
- Psyshock  
- Moonblast  
- Focus Blast  
- Future Sight  

Kartana @ Protective Pads  
Ability: Beast Boost  
Shiny: Yes  
EVs: 252 Atk / 4 SpD / 252 Spe  
Jolly Nature  
- Swords Dance  
- Knock Off  
- Sacred Sword  
- Leaf Blade
"""

    class RandomTeamFromPool(Teambuilder):
        def __init__(self, teams):
            self.teams = [self.join_team(self.parse_showdown_team(team)) for team in teams]

        def yield_team(self):
            return np.random.choice(self.teams)

    sample_builder = RandomTeamFromPool([sample_team])
    sample_player = SimpleHeuristicsPlayer(
        battle_format="gen8ou",
        player_configuration=PlayerConfiguration("sample", None),
        server_configuration=LocalhostServerConfiguration,
        max_concurrent_battles=50,
        team=sample_builder
    )

    await gen_alg_player.battle_against(sample_player, n_battles=100)

    print("gen alg winrate:", gen_alg_player.n_won_battles)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
