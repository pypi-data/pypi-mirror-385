import numpy as np

from evolib.core.individual import Indiv
from evolib.interfaces.enums import MutationStrategy
from evolib.representation.vector import Vector


def test_mutate_vector_changes_values() -> None:
    para = Vector()
    para.vector = np.zeros(3)
    para.bounds = (-1, 1)
    para.evo_params.mutation_strength = 0.1
    para.evo_params.mutation_probability = 1.0
    para.evo_params.mutation_strategy = MutationStrategy.CONSTANT

    indiv = Indiv(para=para)

    before = para.vector.copy()
    indiv.mutate()
    after = para.vector

    assert not np.array_equal(after, before), "Mutation did not change parameter vector"
