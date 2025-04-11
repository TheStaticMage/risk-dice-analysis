#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Risk dice simulator
Written by The Static Mage
https://github.com/thestaticmage/risk-dice-analysis

Parallelize the simulation:
num_cores="24"
seq "$num_cores" | xargs -I{} -P "$num_cores" ./risk-dice-simulator.py -a ### -d ### -t ### -c -o "output{}.txt"
"""

import argparse
import random
import time

DEBUG = False
PRECOMPUTED_ROLLS = []
MAX_ATTACKERS = 3
MAX_DEFENDERS = 2
HEADER = "Attacker Losses,Defender Losses,Difference,Max Rolls,Non-Max Rolls,Elapsed Time"

def main():
    parser = argparse.ArgumentParser(description="Risk Dice Simulator")
    parser.add_argument("-a", "--attacking-troops", type=int, required=True, help="Number of attacking troops")
    parser.add_argument("-d", "--defending-troops", type=int, required=True, help="Number of defending troops")
    parser.add_argument("-c", "--capital", action="store_true", help="Indicates if this is a capital battle")
    parser.add_argument("-t", "--trials", type=int, default=1, help="Number of trials to simulate (default: 1)")
    parser.add_argument("-r", "--random-seed", type=int, default=0, help="Seed for random number generator (default: randomized)")
    parser.add_argument("-o", "--output-file", type=str, help="Output file to save results")
    parser.add_argument("--header", action="store_true", help="Print header in output file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-precomputed-rolls", action="store_true", help="Do not use any precomputed dice rolls (runs slower)")

    args = parser.parse_args()

    if args.debug:
        global DEBUG
        DEBUG = True
        debug_print("Debug mode enabled")

    if args.capital:
        global MAX_DEFENDERS
        MAX_DEFENDERS = 3
        debug_print("Capital battle mode enabled")

    if not args.no_precomputed_rolls:
        precompute_max_dice_rolls()

    if args.random_seed != 0:
        random.seed(args.random_seed)

    debug_print(f"Attacking Troops: {args.attacking_troops}")
    debug_print(f"Defending Troops: {args.defending_troops}")
    debug_print(f"Capital Battle: {args.capital}")
    debug_print(f"Number of Trials: {args.trials}")
    debug_print(f"Random Seed: {args.random_seed}")

    if args.output_file:
        output = open(args.output_file, "w")
        if args.header:
            output.write(HEADER + "\n")
    else:
        output = None
        if args.header:
            print(HEADER)

    for trial in range(args.trials):
        total_attacker_losses, total_defender_losses, max_rolls, non_max_rolls, elapsed_time = simulate_battle(args.attacking_troops, args.defending_troops)
        diff = total_defender_losses - total_attacker_losses
        debug_print(f"Trial {trial + 1}: Attacker Losses: {total_attacker_losses}; Defender Losses: {total_defender_losses}; Difference: {diff}")

        result = f"{total_attacker_losses},{total_defender_losses},{diff},{max_rolls},{non_max_rolls},{elapsed_time:.2f}"
        if output:
            output.write(result + "\n")
        else:
            print(result)

    if output:
        output.close()
        debug_print(f"Results saved to {args.output_file}")


def debug_print(message):
    if DEBUG:
        print(message)


def calculate_losses(attacker_rolls, defender_rolls):
    """
    Calculate the number of losses for both attacker and defender based on their rolls.
    """
    attacker_losses = 0
    defender_losses = 0
    attacker_rolls.sort(reverse=True)
    defender_rolls.sort(reverse=True)

    for i in range(min(len(attacker_rolls), len(defender_rolls))):
        if attacker_rolls[i] > defender_rolls[i]:
            defender_losses += 1
        else:
            attacker_losses += 1

    return attacker_losses, defender_losses


def precompute_max_dice_rolls():
    """
    Precomputing the maximum dice rolls cuts the execution time by an order of
    magnitude. That's because for future iterations we only need to pick one
    random number instead of 5 or 6.
    """

    global PRECOMPUTED_ROLLS
    start_time = time.time()
    for a1 in range(1, 7):
        for a2 in range(1, 7):
            for a3 in range(1, 7):
                for d1 in range(1, 7):
                    for d2 in range(1, 7):
                        if MAX_DEFENDERS == 3:
                            for d3 in range(1, 7):
                                attacker_losses, defender_losses = calculate_losses([a1, a2, a3], [d1, d2, d3])
                                PRECOMPUTED_ROLLS.append((attacker_losses, defender_losses))
                        else:
                            attacker_losses, defender_losses = calculate_losses([a1, a2, a3], [d1, d2])
                            PRECOMPUTED_ROLLS.append((attacker_losses, defender_losses))

    debug_print(f"Precomputed {len(PRECOMPUTED_ROLLS)} maximum dice rolls in {time.time() - start_time:.5f} seconds")


def roll_one_die():
    """
    Simulate rolling a single six sided die.
    """
    return random.randint(1, 6)


def roll_dice(attacking_troops: int, defending_troops: int):
    """
    Simulate the dice rolls for a battle between attacking and defending troops
    according to the rules of Risk. It is assumed that the caller has already
    subtracted the one troop that the attacker must leave behind before calling
    this function.

    Returns the number of losses for both attacker and defender, and true or
    false as to whether this is the "maximum" roll. The maximum roll means that
    the maximum allowable number of attackers and defenders are participating in
    the battle.
    """
    attackers = min(attacking_troops, MAX_ATTACKERS)
    defenders = min(defending_troops, MAX_DEFENDERS)
    is_max_roll = attackers >= MAX_ATTACKERS and defenders >= MAX_DEFENDERS

    if len(PRECOMPUTED_ROLLS) > 0 and is_max_roll:
        attacker_losses, defender_losses = PRECOMPUTED_ROLLS[random.randint(0, len(PRECOMPUTED_ROLLS)-1)]
        debug_print(f"[pre-computed] Losses: {attacker_losses},{defender_losses}; Troops: {attacking_troops-attacker_losses},{defending_troops-defender_losses}")
        return attacker_losses, defender_losses, is_max_roll

    attacker_rolls = [roll_one_die() for _ in range(attackers)]
    defender_rolls = [roll_one_die() for _ in range(defenders)]
    attacker_losses, defender_losses = calculate_losses(attacker_rolls, defender_rolls)
    debug_print(f"[simulated] Attacker: {attacker_rolls}; Defender: {defender_rolls}; Losses: {attacker_losses},{defender_losses}; Troops: {attacking_troops-attacker_losses},{defending_troops-defender_losses}")

    return attacker_losses, defender_losses, is_max_roll


def simulate_battle(attacking_troops: int, defending_troops: int):
    """
    Simulate a complete battle between attacking and defending troops until one
    side is eliminated.
    """
    total_attacker_losses = 0
    total_defender_losses = 0

    start_time = time.time()
    non_maximum_rolls = 0
    maximum_rolls = 0

    # Per the rules of Risk, the attacker must leave one troop behind if they
    # conquer a territory. Therefore attacks are permitted only if the attacker
    # has more than one troop.
    while attacking_troops > 1 and defending_troops > 0:
        attacker_losses, defender_losses, is_max_roll = roll_dice(attacking_troops-1, defending_troops)
        total_attacker_losses += attacker_losses
        total_defender_losses += defender_losses
        non_maximum_rolls += 1 - int(is_max_roll)
        maximum_rolls += int(is_max_roll)

        attacking_troops -= attacker_losses
        defending_troops -= defender_losses

    return total_attacker_losses, total_defender_losses, maximum_rolls, non_maximum_rolls, 1000*(time.time() - start_time)


if __name__ == "__main__":
    main()
