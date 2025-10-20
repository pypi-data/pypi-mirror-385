# SPDX-License-Identifier: MIT
"""
Persistence utilities for saving and resuming evolutionary runs.

This module provides standardized support for:
- Checkpointing full populations (Pop)
- Saving and restoring best individuals (Indiv)
- Loading checkpoints for resuming interrupted runs

All files are stored in the 'checkpoints/' directory by default.
"""


from pathlib import Path
from typing import Any, Optional, cast

from evolib.config.schema import FullConfig
from evolib.core.individual import Indiv
from evolib.core.population import Pop
from evolib.initializers.registry import build_composite_initializer
from evolib.interfaces.types import FitnessFunction
from evolib.io.serialization import (
    load_indiv,
    load_population_pickle,
    save_indiv,
    save_population_pickle,
)
from evolib.utils.config_loader import load_config
from evolib.utils.random import set_random_seed

# Internal checkpoint directory
_CHECKDIR = Path("checkpoints")
_CHECKDIR.mkdir(exist_ok=True)

CHECKPOINT_DIR = _CHECKDIR


def _checkpoint_path(run_name: str) -> Path:
    return _CHECKDIR / f"{run_name}.pkl"


def _best_indiv_path(run_name: str) -> Path:
    return _CHECKDIR / f"{run_name}_best.pkl"


def save_checkpoint(pop: Pop, *, run_name: str = "default") -> None:
    """
    Save the full population to a checkpoint file.

    The file will be stored under 'checkpoints/{run_name}.pkl'.

    Args:
        pop (Pop): Population instance to be saved.
        run_name (str): Optional name to distinguish checkpoint runs.
    """
    path = _checkpoint_path(run_name)

    initializer_backup = pop.para_initializer
    pop.para_initializer = cast(Any, None)

    try:
        save_population_pickle(pop, path)
    finally:
        pop.para_initializer = initializer_backup


def resume_from_checkpoint(
    run_name: str = "default",
    fitness_function: Optional[FitnessFunction] = None,
    silent_fail: bool = True,
) -> Optional[Pop]:
    """
    Resume a previously saved evolutionary run.

    Args:
    run_name (str): Identifier of the checkpoint file.
    fitness_function (callable, optional): Fitness function to assign.
    silent_fail (bool): If True, return None instead of raising FileNotFoundError.


    Returns:
    Optional[Pop]: The resumed population or None if not found and silent_fail is True.
    """
    path = _checkpoint_path(run_name)
    if not path.exists():
        if silent_fail:
            return None
        raise FileNotFoundError(f"Checkpoint '{path}' not found.")

    pop = load_population_pickle(path)

    if fitness_function:
        pop.set_fitness_function(fitness_function)

    # Restore initializer
    pop.para_initializer = build_composite_initializer(pop.config)

    return pop


def resume_or_create(
    config_path: str, fitness_function: FitnessFunction, run_name: str = "default"
) -> Pop:
    """
    Try to resume a saved run, otherwise initialize a new population.

    Args:
    config_path (str): Path to the YAML configuration.
    fitness_function (callable): Fitness function for individuals.
    run_name (str): Optional name for checkpoint file.


    Returns:
    Pop: A ready-to-run population.
    """

    pop = resume_from_checkpoint(
        run_name=run_name, fitness_function=fitness_function, silent_fail=True
    )

    if pop is not None:
        print(f"[Resume] Loaded checkpoint for run_name={run_name}")
        cfg: FullConfig = load_config(config_path)
        random_seed = cfg.random_seed
        set_random_seed(random_seed)
        return pop

    print(f"[Create] New population for run_name={run_name}")
    return Pop(config_path=config_path, fitness_function=fitness_function)


def save_best_indiv(pop: Pop, *, run_name: str = "default") -> None:
    """
    Save the best individual from a population to a separate file.

    The file will be stored as 'checkpoints/{run_name}_best.pkl'.

    Args:
        pop (Pop): Population from which to extract and save the best individual.
        run_name (str): Optional name to identify the saved individual.
    """

    best = pop.best()
    path = _best_indiv_path(run_name)
    save_indiv(best, path)


def load_best_indiv(run_name: str = "default") -> Indiv:
    """
    Load the best individual saved via `save_best_indiv()`.

    Args:
        run_name (str): Name used during saving (without '_best.pkl' suffix).

    Returns:
        Indiv: Deserialized best individual.

    Raises:
        FileNotFoundError: If the corresponding file does not exist.
    """

    path = _best_indiv_path(run_name)
    if not path.exists():
        raise FileNotFoundError(f"Best-indiv file '{path}' not found.")

    indiv = load_indiv(path)

    return indiv
