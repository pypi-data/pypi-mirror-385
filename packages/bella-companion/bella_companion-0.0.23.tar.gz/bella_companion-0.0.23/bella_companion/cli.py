import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from bella_companion.eucovid import run_beast as run_eucovid_beast
from bella_companion.platyrrhine import plot_platyrrhine_results
from bella_companion.platyrrhine import run_beast as run_platyrrhine
from bella_companion.platyrrhine import summarize_logs as summarize_platyrrhine
from bella_companion.simulations import generate_data, generate_figures, print_metrics
from bella_companion.simulations import run_beast as run_simulations
from bella_companion.simulations import summarize_logs as summarize_simulations


def main():
    load_dotenv(Path(os.getcwd()) / ".env")

    parser = argparse.ArgumentParser(
        prog="bella",
        description="Companion tool with experiments and evaluation for Bayesian Evolutionary Layered Learning Architectures (BELLA) BEAST2 package.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "sim-data", help="Generate synthetic simulation datasets."
    ).set_defaults(func=generate_data)

    subparsers.add_parser(
        "sim-run", help="Run BEAST2 analyses on simulation datasets."
    ).set_defaults(func=run_simulations)

    subparsers.add_parser(
        "sim-summarize", help="Summarize BEAST2 log outputs for simulations."
    ).set_defaults(func=summarize_simulations)

    subparsers.add_parser(
        "sim-metrics", help="Compute and print metrics from simulation results."
    ).set_defaults(func=print_metrics)

    subparsers.add_parser(
        "sim-figures", help="Generate plots and figures from simulation results."
    ).set_defaults(func=generate_figures)

    subparsers.add_parser(
        "platyrrhine-run", help="Run BEAST2 analyses on empirical platyrrhine datasets."
    ).set_defaults(func=run_platyrrhine)

    subparsers.add_parser(
        "platyrrhine-summarize",
        help="Summarize BEAST2 log outputs for empirical platyrrhine datasets.",
    ).set_defaults(func=summarize_platyrrhine)

    subparsers.add_parser(
        "platyrrhine-figures",
        help="Generate plots and figures from empirical platyrrhine results.",
    ).set_defaults(func=plot_platyrrhine_results)

    subparsers.add_parser(
        "eucovid-run", help="Run BEAST2 analyses on empirical eucovid datasets."
    ).set_defaults(func=run_eucovid_beast)

    args = parser.parse_args()
    args.func()
