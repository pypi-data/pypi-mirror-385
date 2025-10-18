from typing import Mapping

from nasap_net import Assembly, Component
from nasap_net.algorithms import isomorphisms_iter
from nasap_net.types import A, C
from ._reaction_result_generation import _generate_reaction_result
from ..models import Reaction, _MLE


class _IncorrectReactionResultError(ValueError):
    """
    Exception raised when the reproduced reaction result is inconsistent with
    the given result.
    """


def _generate_sample_rev_mle(
        reaction: Reaction[A],
        assemblies: Mapping[A, Assembly],
        components: Mapping[C, Component]
        ) -> _MLE:
    """Determine the binding site trio on the right-hand side of a reaction."""
    init_assembly = assemblies[reaction.init_assem_id]
    if reaction.entering_assem_id is None:
        entering_assembly = None
    else:
        entering_assembly = assemblies[reaction.entering_assem_id]

    reaction_result = _generate_reaction_result(
        init_assembly,
        entering_assembly,
        reaction.metal_bs,
        reaction.leaving_bs,
        reaction.entering_bs
    )

    try:
        product_isom = next(isomorphisms_iter(
            reaction_result.product_assembly,
            assemblies[reaction.product_assem_id],
            components))
    except StopIteration:
        raise _IncorrectReactionResultError(
            "The product assembly cannot be mapped to the expected one."
            ) from None

    rev_metal_bs = product_isom[reaction_result.metal_bs]
    rev_leaving_bs = product_isom[reaction_result.entering_bs]

    if reaction_result.leaving_assembly is None:
        rev_entering_bs = product_isom[reaction_result.leaving_bs]
    else:
        assert reaction.leaving_assem_id is not None
        try:
            leaving_isom = next(isomorphisms_iter(
                reaction_result.leaving_assembly,
                assemblies[reaction.leaving_assem_id],
                components))
        except StopIteration:
            raise _IncorrectReactionResultError(
                "The leaving assembly cannot be mapped to the expected one."
                ) from None
        rev_entering_bs = leaving_isom[reaction_result.leaving_bs]
    return _MLE(rev_metal_bs, rev_leaving_bs, rev_entering_bs)
