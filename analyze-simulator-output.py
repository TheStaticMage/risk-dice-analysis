#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze the output of the Risk dice simulator.
Written by The Static Mage
https://github.com/thestaticmage/risk-dice-analysis
"""

import argparse
from collections import defaultdict
from os.path import basename

DEBUG = False

def debug_print(message):
    if DEBUG:
        print(message)


def main():
    parser = argparse.ArgumentParser(description="Analyze Risk Dice Simulator Output")
    parser.add_argument("-f", "--file", type=str, required=True, help="File containing the simulator output")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--print-summary", action="store_true", help="Print summary statistics (default: True)")
    parser.add_argument("--print-histogram", action="store_true", help="Print the frequency histogram (default: True)")

    args = parser.parse_args()

    if args.debug:
        global DEBUG
        DEBUG = True
        debug_print("Debug mode enabled")

    count = 0
    frequency = defaultdict(int)
    min_diff = max_diff = 0
    total_diff = 0
    total_diff_squared = 0

    with open(args.file, "r") as file:
        for line in file:
            attacker_losses, defender_losses, diff, rolls, calc_time = map(lambda x: float(x) if '.' in x else int(x), line.strip().split(","))
            debug_print(f"Attacker Losses: {attacker_losses}, Defender Losses: {defender_losses}, Difference: {diff}, Rolls: {rolls}, Time: {calc_time}")

            frequency[diff] += 1

            count += 1
            if count == 1:
                min_diff = max_diff = diff
                total_diff = diff
                total_diff_squared = diff ** 2
            else:
                min_diff = min(min_diff, diff)
                max_diff = max(max_diff, diff)
                total_diff += diff
                total_diff_squared += diff ** 2

    if count > 0:
        if not args.print_summary and not args.print_histogram:
            args.print_summary = True
            args.print_histogram = True

        if args.print_summary:
            average_diff = total_diff / count
            variance = (total_diff_squared / count) - (average_diff ** 2)
            std_dev = variance ** 0.5

            print(f"Analysis of {basename(args.file)}:")
            print(f"Total Trials: {count}")
            print(f"Average Difference: {average_diff}")
            print(f"Standard Deviation: {std_dev}")
            print(f"Minimum Difference: {min_diff}")
            print(f"Maximum Difference: {max_diff}")

        if args.print_histogram:
            print("Difference,Frequency")
            for diff, freq in sorted(frequency.items(), key=lambda x: x[0]):
                print(f"{diff},{freq}")
    else:
        print("No data to analyze.")


if __name__ == "__main__":
    main()