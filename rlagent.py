from typing import Awaitable, Union
import numpy as np
from gym.spaces import Space, Box
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.player import *
from poke_env.player.battle_order import BattleOrder

class Agent(Player):

    def choose_move(self, battle: AbstractBattle) -> BattleOrder | Awaitable[BattleOrder]:
        return super().choose_move(battle)
