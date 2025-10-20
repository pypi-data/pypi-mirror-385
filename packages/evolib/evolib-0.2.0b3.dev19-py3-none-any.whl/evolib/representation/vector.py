# SPDX-License-Identifier: MIT

import numpy as np

from evolib.config.vector_component_config import VectorComponentConfig
from evolib.interfaces.enums import MutationStrategy
from evolib.interfaces.types import ModuleConfig
from evolib.operators.mutation import (
    adapt_mutation_probability_by_diversity,
    adapt_mutation_strength,
    adapt_mutation_strength_by_diversity,
    adapt_mutation_strengths,
    adapted_tau,
    exponential_mutation_probability,
    exponential_mutation_strength,
)
from evolib.representation._apply_config_mapping import (
    apply_crossover_config,
    apply_mutation_config,
)
from evolib.representation.base import ParaBase
from evolib.representation.evo_params import EvoControlParams
from evolib.representation.netvector import NetVector


class Vector(ParaBase):
    """
    A parameter vector representation used as an evolutionary module.

    This class supports different structural interpretations of the parameter dimension
    (flat, tensor, net, etc.), bounds, mutation strategies, and crossover.
    """

    def __init__(self) -> None:
        # Core parameter vector
        self.vector: np.ndarray = np.zeros(1)
        self.shape: tuple[int, ...] = (1,)

        # Whether to randomize initial mutation strengths
        self.randomize_mutation_strengths: bool | None = None

        # Parameter bounds (e.g. [-1, 1])
        self.bounds: tuple[float, float] | None = None
        self.init_bounds: tuple[float, float] | None = None

        # Evolution control parameters (mutation, crossover, etc.)
        self.evo_params = EvoControlParams()

    def apply_config(self, cfg: ModuleConfig) -> None:
        """
        Apply a configuration object to initialize this Vector.

        Args:
            cfg: A VectorComponentConfig defining dimension, structure,
                 initialization, and mutation/crossover strategies.
        """

        if not isinstance(cfg, VectorComponentConfig):
            raise TypeError("Expected VectorComponentConfig")

        evo_params = self.evo_params

        # Interpret dimension based on structure type
        structure = getattr(cfg, "structure", "flat")

        if structure == "net":
            # Map to a neural-network-like parameter vector
            if not isinstance(cfg.dim, list):
                raise ValueError("structure='net' requires dim as list[int]")
            net = NetVector(dim=cfg.dim, activation=cfg.activation or "tanh")
            cfg.shape = (int(net.n_parameters),)
            cfg.dim = int(net.n_parameters)

        elif structure == "tensor":
            if not isinstance(cfg.dim, list):
                raise ValueError("structure='tensor' requires dim as list[int]")
            cfg.shape = tuple(cfg.dim)
            cfg.dim = int(np.prod(cfg.shape))

        elif structure == "blocks":
            if not isinstance(cfg.dim, list):
                raise ValueError("structure='blocks' requires dim as list[int]")
            cfg.shape = None
            cfg.dim = sum(cfg.dim)

        elif structure == "grouped":
            if not isinstance(cfg.dim, list):
                raise ValueError("structure='grouped' requires dim as list[int]")
            cfg.shape = None
            cfg.dim = sum(cfg.dim)

        elif structure == "flat":
            if isinstance(cfg.dim, list):
                cfg.shape = tuple(cfg.dim)
                cfg.dim = int(np.prod(cfg.shape))
            else:
                cfg.shape = (cfg.dim,)
        else:
            raise ValueError(f"Unknown structure type: '{structure}'")

        # Assign dimensions and allocate vector
        self.dim = cfg.dim
        self.shape = cfg.shape or (cfg.dim,)
        self.vector = np.zeros(self.dim)

        # Bounds
        self.bounds = cfg.bounds
        self.init_bounds = cfg.init_bounds or self.bounds

        # Mutation
        if cfg.mutation is None:
            raise ValueError("Mutation config is required for Vector.")
        evo_params.tau = cfg.tau or 0.0
        self.randomize_mutation_strengths = cfg.randomize_mutation_strengths or False

        evo_params.mutation_strategy = cfg.mutation.strategy

        # Apply mutation and crossover configs
        apply_mutation_config(evo_params, cfg.mutation)
        apply_crossover_config(evo_params, cfg.crossover)

    def mutate(self) -> None:
        """
        Apply Gaussian mutation to the parameter vector.

        Two modes are supported:
        - Per-parameter mutation strengths (`mutation_strengths` defined).
        - Global mutation strength with optional mutation probability.
        """
        if self.evo_params.mutation_strengths is not None:

            # Adaptive per-parameter mutation
            noise = np.random.normal(
                loc=0.0, scale=self.evo_params.mutation_strengths, size=len(self.vector)
            )

            self.vector += noise
        else:
            if self.evo_params.mutation_strength is None:
                raise ValueError("mutation_strength must be set.")
            # Global mutation (single sigma applied to all parameters)
            noise = np.random.normal(
                loc=0.0, scale=self.evo_params.mutation_strength, size=self.vector.shape
            )
            prob = self.evo_params.mutation_probability or 1.0
            mask = (np.random.rand(len(self.vector)) < prob).astype(np.float64)
            self.vector += noise * mask

        if self.bounds is not None:
            self.vector = np.clip(self.vector, *self.bounds)

    def print_status(self) -> None:
        """Convenience: print the formatted internal state string."""
        status = self.get_status()
        print(status)

    def get_status(self) -> str:
        """
        Return a human-readable summary of the internal state.

        Includes vector preview, mutation strength(s), tau, and crossover probability.
        """
        parts = []

        vector_preview = np.round(self.vector[:4], 3).tolist()
        parts.append(f"Vector={vector_preview}{'...' if len(self.vector) > 4 else ''}")

        if self.evo_params.mutation_strength is not None:
            parts.append(
                f"Global mutation_strength=" f"{self.evo_params.mutation_strength:.4f}"
            )

        if self.evo_params.crossover_probability is not None:
            parts.append(f"crossover_prob={self.evo_params.crossover_probability:.4f}")

        if self.evo_params.tau != 0.0:
            parts.append(f"tau={self.evo_params.tau:.4f}")

        if self.evo_params.mutation_strengths is not None:
            parts.append(
                f"Para mutation strength: "
                f"mean={np.mean(self.evo_params.mutation_strengths):.4f}, "
                f"min={np.min(self.evo_params.mutation_strengths):.4f}, "
                f"max={np.max(self.evo_params.mutation_strengths):.4f}"
            )

        return " | ".join(parts)

    def get_history(self) -> dict[str, float]:
        """
        Return mutation-related values for logging.

        Includes global tau, global mutation strength, and statistics on per-parameter
        strengths if applicable.
        """
        history = {}

        # global updatefaktor
        if self.evo_params.tau is not None:
            history["tau"] = float(self.evo_params.tau)

        # globale mutationstregth (optional)
        if self.evo_params.mutation_strength is not None:
            history["mutation_strength"] = float(self.evo_params.mutation_strength)

        # vector mutationsstrength
        if self.evo_params.mutation_strengths is not None:
            strengths = self.evo_params.mutation_strengths
            history.update(
                {
                    "sigma_mean": float(np.mean(strengths)),
                    "sigma_min": float(np.min(strengths)),
                    "sigma_max": float(np.max(strengths)),
                }
            )

        return history

    def update_mutation_parameters(
        self, generation: int, max_generations: int, diversity_ema: float | None = None
    ) -> None:
        """
        Update mutation parameters based on the chosen strategy.

        Args:
            generation: Current generation index.
            max_generations: Maximum number of generations planned.
            diversity_ema: Exponential moving average of population diversity
                           (required for adaptive-global strategies).
        """

        ep = self.evo_params
        """Update mutation parameters based on strategy and generation."""
        if ep.mutation_strategy == MutationStrategy.EXPONENTIAL_DECAY:
            ep.mutation_strength = exponential_mutation_strength(
                ep, generation, max_generations
            )

            ep.mutation_probability = exponential_mutation_probability(
                ep, generation, max_generations
            )

        elif ep.mutation_strategy == MutationStrategy.ADAPTIVE_GLOBAL:
            if diversity_ema is None:
                raise ValueError(
                    "diversity_ema must be provided" "for ADAPTIVE_GLOBAL strategy"
                )
            if ep.mutation_strength is None:
                raise ValueError(
                    "mutation_strength must be provided for ADAPTIVE_GLOBAL strategy"
                )
            if ep.mutation_probability is None:
                raise ValueError(
                    "mutation_probability must be provided"
                    "for ADAPTIVE_GLOBAL strategy"
                )

            ep.mutation_probability = adapt_mutation_probability_by_diversity(
                ep.mutation_probability, diversity_ema, ep
            )

            ep.mutation_strength = adapt_mutation_strength_by_diversity(
                ep.mutation_strength, diversity_ema, ep
            )

        elif ep.mutation_strategy == MutationStrategy.ADAPTIVE_INDIVIDUAL:
            # Ensure tau is initialized
            if ep.tau is None or ep.tau == 0.0:
                ep.tau = adapted_tau(len(self.vector))

            if ep.min_mutation_strength is None or ep.max_mutation_strength is None:
                raise ValueError(
                    "min_mutation_strength and max_mutation_strength" "must be defined."
                )
            if self.bounds is None:
                raise ValueError("bounds must be set")
            # Ensure mutation_strength is initialized
            if ep.mutation_strength is None:
                ep.mutation_strength = np.random.uniform(
                    ep.min_mutation_strength, ep.max_mutation_strength
                )

            # Perform adaptive update
            ep.mutation_strength = adapt_mutation_strength(ep, self.bounds)

        elif ep.mutation_strategy == MutationStrategy.ADAPTIVE_PER_PARAMETER:
            # Ensure tau is initialized
            if ep.tau == 0.0 or ep.tau is None:
                ep.tau = adapted_tau(len(self.vector))

            # Ensure mutation_strength is initialized
            if ep.min_mutation_strength is None or ep.max_mutation_strength is None:
                raise ValueError(
                    "min_mutation_strength and max_mutation_strength" "must be defined."
                )

            if self.bounds is None:
                raise ValueError("bounds must be set")

            if ep.mutation_strengths is None:
                ep.mutation_strengths = np.random.uniform(
                    ep.min_mutation_strength,
                    ep.max_mutation_strength,
                    size=len(self.vector),
                )

            # Perform adaptive update
            ep.mutation_strengths = adapt_mutation_strengths(ep, self.bounds)

    def crossover_with(self, partner: "ParaBase") -> None:
        """
        Perform crossover with another Vector instance.

        The internal crossover function may produce either one or two offspring. Bounds
        are applied to clip the resulting parameter values.
        """
        if not isinstance(partner, Vector):
            return

        if self.evo_params._crossover_fn is None:
            return

        result = self.evo_params._crossover_fn(self.vector, partner.vector)

        if isinstance(result, tuple):
            child1, child2 = result
        else:
            child1 = child2 = result

        if self.bounds is None or partner.bounds is None:
            raise ValueError("Both participants must define bounds before crossover.")

        min_val, max_val = self.bounds
        self.vector = np.clip(child1, min_val, max_val)

        min_val_p, max_val_p = partner.bounds
        partner.vector = np.clip(child2, min_val_p, max_val_p)
