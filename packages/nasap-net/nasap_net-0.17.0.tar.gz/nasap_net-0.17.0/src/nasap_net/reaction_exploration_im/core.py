from collections.abc import Iterable, Mapping
from itertools import chain, product
from typing import Iterator, TypeVar

from nasap_net.models import Assembly
from nasap_net.types import ID
from .explorer import InterReactionExplorer, IntraReactionExplorer
from .lib import ReactionOutOfScopeError, ReactionResolver
from .models import MLEKind, Reaction

_T = TypeVar('_T', bound=ID)

def explore_reactions(
        assemblies: Mapping[_T, Assembly],
        mle_kinds: Iterable[MLEKind],
        ) -> Iterator[Reaction]:
    # Add assembly IDs to assemblies
    assems_with_ids = [
        assem.copy_with(id_=assem_id)
        for assem_id, assem in assemblies.items()]

    reaction_iters: list[Iterator[Reaction]] = []
    for mle_kind in mle_kinds:
        # Intra-molecular reactions
        for assem in assems_with_ids:
            intra_explorer = IntraReactionExplorer(assem, mle_kind)
            reaction_iters.append(intra_explorer.explore())

        # Inter-molecular reactions
        for init_assem, entering_assem in product(assems_with_ids, repeat=2):
            inter_explorer = InterReactionExplorer(
                init_assem, entering_assem, mle_kind)
            reaction_iters.append(inter_explorer.explore())

    resolver = ReactionResolver(assems_with_ids)

    for reaction in chain.from_iterable(reaction_iters):
        try:
            yield resolver.resolve(reaction)
        except ReactionOutOfScopeError:
            continue
