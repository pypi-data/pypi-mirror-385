# SPDX-License-Identifier: MIT
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from evolib.config.base_component_config import HeliConfig
from evolib.config.component_registry import get_component_config_class
from evolib.interfaces.enums import (
    EvolutionStrategy,
    ReplacementStrategy,
    SelectionStrategy,
)


class EvolutionConfig(BaseModel):
    """
    Top-level evolution policy.

    Holds only the high-level strategy choice; operator-specific behavior lives in the
    Para* representations and operator modules.
    """

    model_config = ConfigDict(extra="forbid")

    strategy: EvolutionStrategy = Field(
        ..., description="High-level evolution strategy (e.g. (mu_plus_lambda)."
    )

    heli: Optional[HeliConfig] = Field(
        default=None,
        description=(
            "Optional HELI (Hierarchical Evolution with Lineage Incubation)"
            "configuration. "
            "Defines local subpopulation incubation for structure-mutated individuals."
        ),
    )


class SelectionConfig(BaseModel):
    """
    Parent selection settings.

    Depending on the selected strategy, only some fields are relevant; the actual
    semantics are implemented in the selection registry.
    """

    model_config = ConfigDict(extra="forbid")

    strategy: SelectionStrategy = Field(
        ..., description="Parent selection strategy (e.g. tournament, ranking)."
    )
    num_parents: Optional[int] = Field(
        None, description="Optional override for the number of parents to pick."
    )
    tournament_size: Optional[int] = Field(
        None, description="Tournament size for tournament selection."
    )
    exp_base: Optional[float] = Field(
        None, description="Base for exponential ranking selection."
    )
    fitness_maximization: Optional[bool] = Field(
        False, description="If True, higher fitness is considered better."
    )


class ReplacementConfig(BaseModel):
    """
    Survivor replacement (environmental selection) settings.

    Concrete behavior is implemented in the replacement registry.
    """

    model_config = ConfigDict(extra="forbid")

    strategy: ReplacementStrategy = Field(
        ..., description="Survivor selection strategy (e.g. replace_worst, anneal)."
    )
    num_replace: Optional[int] = Field(
        None, description="How many individuals to replace (strategy-dependent)."
    )
    temperature: Optional[float] = Field(
        None, description="Temperature parameter for annealing-like strategies."
    )


class StoppingCriteria(BaseModel):
    """Optional stopping criteria for early stopping."""

    model_config = ConfigDict(extra="forbid")

    target_fitness: Optional[float] = Field(
        None,
        description="Stop once fitness is below (or above if maximize) this value.",
    )
    minimize: bool = Field(
        True, description="Whether the problem is a minimization task (default: True)."
    )
    patience: Optional[int] = Field(
        None, description="Stop if no improvement for this many generations."
    )
    min_delta: float = Field(
        0.0, description="Minimum fitness change to qualify as improvement."
    )
    time_limit_s: Optional[float] = Field(
        None, description="Wall-clock time limit in seconds."
    )


class ParallelConfig(BaseModel):
    """
    Optional parallelization backend.

    Controls whether fitness evaluation is run sequentially or distributed (currently
    only Ray is supported).
    """

    model_config = ConfigDict(extra="forbid")

    backend: str = Field(
        default="none",
        description="Parallel backend to use: 'none' (default) or 'ray'.",
    )
    num_cpus: Optional[int] = Field(
        default=None,
        description="Number of CPUs to allocate (Ray only). "
        "If None, Ray chooses automatically.",
    )
    address: Optional[str] = Field(
        default=None,
        description="Ray cluster address (e.g. 'auto' or '127.0.0.1:6379'). "
        "If None, starts a local Ray instance.",
    )


class FullConfig(BaseModel):
    """
    Main configuration model for an evolutionary run.

    Aggregates global run parameters, high-level policies (evolution/selection/
    replacement), and a 'modules' mapping that is resolved into typed ComponentConfigs.

    1) YAML → dict 2) dict → FullConfig(**data) 3) model_validator(mode="before")
    resolves each raw 'modules[name]' dict into a    typed ComponentConfig (e.g.
    VectorComponentConfig, EvoNetComponentConfig).
    """

    model_config = ConfigDict(extra="forbid")

    # Global run parameters
    parent_pool_size: int = Field(
        ..., description="Number of parents retained in each generation."
    )
    offspring_pool_size: int = Field(
        ..., description="Number of offspring produced per generation."
    )
    max_generations: int = Field(
        ..., description="Maximum number of generations to run."
    )
    max_indiv_age: int = Field(
        0,
        description="Maximum allowed individual age in generations; 0 disables aging.",
    )
    num_elites: int = Field(
        ..., description="Number of elite individuals preserved each generation."
    )
    random_seed: Optional[int] = Field(
        None,
        description="Global seed for random number generators. "
        "Use an integer for reproducible runs or None "
        "for stochastic runs.",
    )
    stopping: Optional[StoppingCriteria] = Field(
        None, description="Optional early stopping configuration."
    )

    # Module configs (resolved to typed ComponentConfig instances by the validator)
    modules: Dict[str, Any]

    # High-level policies (optional)
    evolution: EvolutionConfig | None = Field(
        default=None, description="Global evolution strategy configuration."
    )
    selection: SelectionConfig | None = Field(
        default=None, description="Parent selection configuration."
    )
    replacement: ReplacementConfig | None = Field(
        default=None, description="Survivor selection (replacement) configuration."
    )

    # Optional parallelization backend
    parallel: Optional[ParallelConfig] = Field(
        default=None, description="Optional parallelization backend configuration."
    )

    @model_validator(mode="before")
    @classmethod
    def resolve_component_configs(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Replace raw 'modules[name]' dicts with typed ComponentConfig objects.

        Steps:
          1) Read raw dict from 'modules[name]'
          2) Determine 'type' (default: "vector")
          3) Lookup ComponentConfig class in the registry
          4) Instantiate the typed model with the raw dict

        After this hook, 'modules' contains fully validated Pydantic models.

        Raises
        ------
        ValueError
            If a module 'type' is unknown to the component registry.
        """
        raw_modules = data.get("modules", {})
        resolved: dict[str, Any] = {}

        for name, cfg in raw_modules.items():
            type_name = cfg.get("type", "vector")
            cfg_cls = get_component_config_class(type_name)
            resolved[name] = cfg_cls(**cfg)

        data["modules"] = resolved
        return data

    @model_validator(mode="after")
    def _check_consistency(self) -> "FullConfig":
        """Global sanity checks for the main configuration."""
        if self.parent_pool_size <= 0:
            raise ValueError("parent_pool_size must be > 0")
        if self.offspring_pool_size <= 0:
            raise ValueError("offspring_pool_size must be > 0")
        if self.num_elites < 0:
            raise ValueError("num_elites must be >= 0")
        if self.num_elites > self.parent_pool_size:
            raise ValueError("num_elites cannot exceed parent_pool_size")
        if self.max_generations <= 0:
            raise ValueError("max_generations must be > 0")
        if self.max_indiv_age < 0:
            raise ValueError("max_indiv_age must be >= 0")
        return self
