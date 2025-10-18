from collections import UserDict, defaultdict
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from typing import Generic

from nasap_net import Assembly, Component
from nasap_net.types import A, C, R
from ._lib import _IncorrectReactionResultError, _are_equivalent_mles, \
    _generate_sample_rev_mle
from .models import Reaction, _MLE


class IncorrectReactionResultError(ValueError):
    """
    Exception raised when the reproduced reaction result is inconsistent with
    the given result.
    """


class DuplicateReactionError(ValueError):
    """
    Exception raised when there are duplicate reactions in the input.
    """


def pair_reverse_reactions(
        id_to_reaction: Mapping[R, Reaction[A]],
        assemblies: Mapping[A, Assembly],
        components: Mapping[C, Component]
        ) -> dict[R, R | None]:
    """Pair reactions with their reverse reactions.

    Parameters
    ----------
    id_to_reaction: dict mapping reaction IDs to Reaction objects.
        All reactions must be unique. IDs can be all integers or all strings.
    assemblies: dict mapping assembly IDs to Assembly objects.
        IDs can be all integers or all strings.
    components: dict mapping component IDs to Component objects.
        IDs can be all integers or all strings.

    Returns
    -------
    dict mapping each reaction ID to its reverse reaction ID, or None if no
    reverse reaction exists.
        If reaction A is the reverse of reaction B, then the mapping will
        include both A -> B and B -> A.

    Raises
    ------
    IncorrectReactionResultError
        If the reproduced reaction result is inconsistent with the given
        result.
    DuplicateReactionError
        If there are duplicate reactions in the input.
    """
    return _pair_reverse_reactions(
        id_to_reaction, assemblies, components, skip_already_found=True)


@dataclass(frozen=True)
class _ReactionIndex(Generic[A]):
    init_assem_id: A
    entering_assem_id: A | None
    product_assem_id: A
    leaving_assem_id: A | None


class _NoOverwriteDict(UserDict):
    """A dict that raises an error when overwriting an existing key."""
    def __setitem__(self, key, value):
        if key in self.data:
            raise KeyError(f"Key '{key}' already exists.")
        super().__setitem__(key, value)


# skip_already_found option is for testing purpose.
def _pair_reverse_reactions(
        id_to_reaction: Mapping[R, Reaction[A]],
        assemblies: Mapping[A, Assembly],
        components: Mapping[C, Component],
        skip_already_found: bool = True
        ) -> dict[R, R | None]:
    """Implementation of `pair_reverse_reactions` with an option to skip
    already found reactions.
    """
    index_to_id = defaultdict(set)
    for target_reaction_id, target_reaction in id_to_reaction.items():
        index = _ReactionIndex(
            init_assem_id=target_reaction.init_assem_id,
            entering_assem_id=target_reaction.entering_assem_id,
            product_assem_id=target_reaction.product_assem_id,
            leaving_assem_id=target_reaction.leaving_assem_id
        )
        index_to_id[index].add(target_reaction_id)

    reaction_to_reverse: MutableMapping[R, R | None] = _NoOverwriteDict()

    for target_reaction_id, target_reaction in id_to_reaction.items():
        if skip_already_found and target_reaction_id in reaction_to_reverse:
            continue

        reversed_index = _ReactionIndex(
            init_assem_id=target_reaction.product_assem_id,
            entering_assem_id=target_reaction.leaving_assem_id,
            product_assem_id=target_reaction.init_assem_id,
            leaving_assem_id=target_reaction.entering_assem_id
            )

        candidate_ids = index_to_id.get(reversed_index)
        if not candidate_ids:
            reaction_to_reverse[target_reaction_id] = None
            continue

        try:
            sample_rev_mle = _generate_sample_rev_mle(
                target_reaction, assemblies, components)
        except _IncorrectReactionResultError:
            raise IncorrectReactionResultError() from None

        # Any reaction with MLE equivalent to the sample_rev_mle
        # is a reverse reaction.
        for candidate_id in candidate_ids:
            candidate = id_to_reaction[candidate_id]
            candidate_mle = _MLE(
                candidate.metal_bs, candidate.leaving_bs,
                candidate.entering_bs)

            rev_init_assembly = assemblies[target_reaction.product_assem_id]
            rev_entering_assembly = None
            if target_reaction.leaving_assem_id is not None:
                rev_entering_assembly = assemblies[
                    target_reaction.leaving_assem_id]

            if _are_equivalent_mles(
                    rev_init_assembly, rev_entering_assembly,
                    sample_rev_mle, candidate_mle,
                    components
                    ):
                reaction_to_reverse[target_reaction_id] = candidate_id
                reaction_to_reverse[candidate_id] = target_reaction_id
                # Multiple matches are impossible since there are no
                # duplicate reactions.
                break
        else:
            reaction_to_reverse[target_reaction_id] = None

    return dict(reaction_to_reverse)
