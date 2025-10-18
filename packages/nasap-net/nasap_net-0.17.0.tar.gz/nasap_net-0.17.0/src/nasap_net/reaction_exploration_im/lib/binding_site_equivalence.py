from dataclasses import dataclass, field
from typing import Iterable

from nasap_net.isomorphism import get_all_isomorphisms
from nasap_net.models import Assembly, BindingSite
from nasap_net.utils import UnionFind


@dataclass(frozen=True)
class UniqueComb:
    """A unique binding site or binding site set with duplication count."""
    site_comb: tuple[BindingSite, ...]
    duplication: int = field(kw_only=True)


def extract_unique_site_combinations(
        binding_site_combs: Iterable[tuple[BindingSite, ...]],
        assembly: Assembly,
        ) -> set[UniqueComb]:
    """Compute unique binding sites or binding site sets."""
    grouped_node_combs = group_equivalent_node_combs(
        binding_site_combs, assembly)

    return {
        UniqueComb(
            site_comb=sorted(comb_group)[0],
            duplication=len(comb_group))
        for comb_group in grouped_node_combs
    }


def group_equivalent_node_combs(
        node_combs: Iterable[tuple[BindingSite, ...]],
        assembly: Assembly,
        ) -> set[frozenset[tuple[BindingSite, ...]]]:
    """Group equivalent node combinations."""
    node_combs = set(node_combs)
    uf = UnionFind(node_combs)

    self_isomorphisms = get_all_isomorphisms(assembly, assembly)
    binding_site_isoms = [
        isom.binding_site_mapping for isom in self_isomorphisms]

    for isom in binding_site_isoms:
        for comb in node_combs:
            mapped_comb = tuple(isom[site] for site in comb)
            if mapped_comb in node_combs:
                uf.union(comb, mapped_comb)
    return {
        frozenset(elements) for elements
        in uf.root_to_elements.values()}
