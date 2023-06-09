from poke_env.environment.move_category import MoveCategory
from poke_env.environment.side_condition import SideCondition
from poke_env.player.player import Player
from poke_env.environment.pokemon_type import *

import random


class ImprovedHeuristicsPlayer(Player):
    ENTRY_HAZARDS = {
        "spikes": SideCondition.SPIKES,
        "stealthrock": SideCondition.STEALTH_ROCK,
        "stickyweb": SideCondition.STICKY_WEB,
        "toxicspikes": SideCondition.TOXIC_SPIKES,
    }

    ANTI_HAZARDS_MOVES = {"rapidspin", "defog"}

    SPEED_TIER_COEFICIENT = 0.1
    HP_FRACTION_COEFICIENT = 0.4
    SWITCH_OUT_MATCHUP_THRESHOLD = -2

    def _estimate_matchup(self, mon, opponent):
        score = max([opponent.damage_multiplier(t) for t in mon.types if t is not None])
        score -= max(
            [mon.damage_multiplier(t) for t in opponent.types if t is not None]
        )
        if mon.base_stats["spe"] > opponent.base_stats["spe"]:
            score += self.SPEED_TIER_COEFICIENT
        elif opponent.base_stats["spe"] > mon.base_stats["spe"]:
            score -= self.SPEED_TIER_COEFICIENT

        score += mon.current_hp_fraction * self.HP_FRACTION_COEFICIENT
        score -= opponent.current_hp_fraction * self.HP_FRACTION_COEFICIENT

        return score

    def _should_switch_out(self, battle):
        active = battle.active_pokemon
        opponent = battle.opponent_active_pokemon
        # If there is a decent switch in...
        if [
            m
            for m in battle.available_switches
            if self._estimate_matchup(m, opponent) > 0
        ]:
            # ...and a 'good' reason to switch out
            if active.boosts["def"] <= -3 or active.boosts["spd"] <= -3:
                return True
            if (
                    active.boosts["atk"] <= -3
                    and active.stats["atk"] >= active.stats["spa"]
            ):
                return True
            if (
                    active.boosts["spa"] <= -3
                    and active.stats["atk"] <= active.stats["spa"]
            ):
                return True
            if (
                    self._estimate_matchup(active, opponent)
                    < self.SWITCH_OUT_MATCHUP_THRESHOLD
            ):
                return True
        return False

    def _stat_estimation(self, mon, stat):
        # Stats boosts value
        if mon.boosts[stat] > 1:
            boost = (2 + mon.boosts[stat]) / 2
        else:
            boost = 2 / (2 - mon.boosts[stat])
        return ((2 * mon.base_stats[stat] + 31) + 5) * boost

    def choose_move(self, battle):
        # Main mons shortcuts
        active = battle.active_pokemon
        opponent = battle.opponent_active_pokemon

        # Rough estimation of damage ratio
        physical_ratio = self._stat_estimation(active, "atk") / self._stat_estimation(
            opponent, "def"
        )
        special_ratio = self._stat_estimation(active, "spa") / self._stat_estimation(
            opponent, "spd"
        )

        if battle.available_moves and random.random() < 0.9 and (
                not self._should_switch_out(battle) or not battle.available_switches
        ):
            n_remaining_mons = len(
                [m for m in battle.team.values() if m.fainted is False]
            )
            n_opp_remaining_mons = 6 - len(
                [m for m in battle.team.values() if m.fainted is True]
            )

            # Heal if possible
            if active.current_hp_fraction < 0.66 and random.random() < 0.66:
                for move in battle.available_moves:
                    if move.heal > 0.3:
                        return self.create_order(move)

            # Entry hazard...
            if random.random() < 0.75:
                for move in battle.available_moves:
                    # ...setup
                    if (
                            n_opp_remaining_mons >= 3
                            and move.id in self.ENTRY_HAZARDS
                            and self.ENTRY_HAZARDS[move.id]
                            not in battle.opponent_side_conditions
                    ):
                        return self.create_order(move)

                    # ...removal
                    elif (
                            battle.side_conditions
                            and move.id in self.ANTI_HAZARDS_MOVES
                            and n_remaining_mons >= 2
                    ):
                        return self.create_order(move)

            # Setup moves
            if (
                    active.current_hp_fraction == 1
                    and self._estimate_matchup(active, opponent) > 0
                    and random.random() < 0.75
            ):
                for move in battle.available_moves:
                    if (
                            move.boosts
                            and sum(move.boosts.values()) >= 2
                            and move.target == "self"
                            and min(
                        [active.boosts[s] for s, v in move.boosts.items() if v > 0]
                    )
                            < 6
                    ):
                        return self.create_order(move)

            if random.random() < .9:
                move = max(
                    battle.available_moves,
                    key=lambda m: m.base_power
                                  * (1.5 if m.type in active.types else 1)
                                  * (
                                      physical_ratio
                                      if m.category == MoveCategory.PHYSICAL
                                      else special_ratio
                                  )
                                  * m.accuracy
                                  * m.expected_hits
                                  * opponent.damage_multiplier(m)
                                  * (0 if ((m.type == PokemonType.GROUND and (
                                battle.opponent_active_pokemon.ability == "levitate" or battle.opponent_active_pokemon.item == "airballoon"))
                                           or m.type == PokemonType.FIRE and battle.opponent_active_pokemon.ability == "flashfire") else 1)
                                  * (0 if (
                                m.status and battle.opponent_active_pokemon.status and m.defensive_category == MoveCategory.STATUS) else 1),
                )
            else:
                move = random.choice(battle.available_moves)
            return self.create_order(move)

        if battle.available_switches and random.random() < 0.9:
            return self.create_order(
                max(
                    battle.available_switches,
                    key=lambda s: self._estimate_matchup(s, opponent),
                )
            )

        return self.choose_random_move(battle)
