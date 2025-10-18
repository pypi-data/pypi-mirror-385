import itertools
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass

from nasap_net.models import Assembly, BindingSite, Bond
from nasap_net.types import ID
from .lib import extract_unique_site_combinations, separate_if_possible
from .models import MLE, MLEKind, Reaction


class ReactionExplorer(ABC):
    def explore(self) -> Iterator[Reaction]:
        mles = self._iter_mles()
        unique_mles = self._get_unique_mles(mles)
        for mle in unique_mles:
            yield self._perform_reaction(mle)

    @abstractmethod
    def _iter_mles(self) -> Iterator[MLE]:
        pass

    @abstractmethod
    def _get_unique_mles(self, mles: Iterable[MLE]) -> Iterator[MLE]:
        pass

    @abstractmethod
    def _perform_reaction(self, mle: MLE) -> Reaction:
        pass


@dataclass(frozen=True)
class IntraReactionExplorer(ReactionExplorer):
    """Class to explore intra-molecular reactions within an assembly.

    Parameters
    ----------
    assembly : Assembly
        The assembly in which intra-molecular reactions are to be explored.
    mle_kind : MLEKind
        The kinds of components involved in the reaction:
            - `mle_kind.metal`: The component kind of the metal binding site.
            - `mle_kind.leaving`: The component kind of the leaving binding site.
            - `mle_kind.entering`: The component kind of the entering binding site.

    Methods
    -------
    explore() -> Iterator[Reaction]
        Explore and yield all possible intra-molecular reactions within the
        assembly based on the specified MLE kind.
    """
    assembly: Assembly
    mle_kind: MLEKind

    def _iter_mles(self) -> Iterator[MLE]:
        """Get all possible MLEs for intra-molecular reactions in an assembly.

        This function generates all MLEs (combinations of metal binding sites,
        leaving binding sites, and entering binding sites) for intra-molecular
        reactions within a given assembly based on the specified component kinds.

        Returned MLEs meet the following conditions:
          - The metal binding site and leaving binding site are connected to each other.
          - The component kind of the metal binding site is `mle_kind.metal`.
          - The component kind of the leaving binding site is `mle_kind.leaving`.
          - The entering binding site is free and has the component kind `mle_kind.entering`.
        """
        ml_pair = _enum_ml_pair(
            self.assembly,
            metal_kind=self.mle_kind.metal, leaving_kind=self.mle_kind.leaving)

        entering_sites = self.assembly.find_sites(
            has_bond=False, component_kind=self.mle_kind.entering)

        for (metal, leaving), entering in itertools.product(
                ml_pair, entering_sites):
            yield MLE(metal, leaving, entering)

    def _get_unique_mles(self, mles: Iterable[MLE]) -> Iterator[MLE]:
        unique_mle_trios = extract_unique_site_combinations(
            [(mle.metal, mle.leaving, mle.entering) for mle in mles],
             self.assembly)
        for unique_mle in unique_mle_trios:
            metal, leaving, entering = unique_mle.site_comb
            yield MLE(
                metal, leaving, entering,
                duplication=unique_mle.duplication)

    def _perform_reaction(self, mle: MLE) -> Reaction:
        raw_product = (
            self.assembly
                .remove_bond(mle.metal, mle.leaving)
                .add_bond(mle.metal, mle.entering)
        )

        product, leaving = separate_if_possible(
            raw_product, metal_comp_id=mle.metal.component_id)

        return Reaction(
            init_assem=self.assembly,
            entering_assem=None,
            product_assem=product,
            leaving_assem=leaving,
            metal_bs=mle.metal,
            leaving_bs=mle.leaving,
            entering_bs=mle.entering,
            duplicate_count=mle.duplication
        )


@dataclass(frozen=True)
class InterReactionExplorer(ReactionExplorer):
    """Class to explore inter-molecular reactions between two assemblies.

    Parameters
    ----------
    init_assembly : Assembly
        The initial assembly. This assembly contains the metal and leaving
        binding sites.
    entering_assembly : Assembly
        The entering assembly. This assembly contains the entering binding site.
    mle_kind : MLEKind
        The kinds of components involved in the reaction:
            - `mle_kind.metal`: The component kind of the metal binding site.
            - `mle_kind.leaving`: The component kind of the leaving binding site.
            - `mle_kind.entering`: The component kind of the entering binding site.

    Methods
    -------
    explore() -> Iterator[Reaction]
        Explore and yield all possible inter-molecular reactions between the
        two assemblies based on the specified MLE kind.
    """
    init_assembly: Assembly
    entering_assembly: Assembly
    mle_kind: MLEKind

    def _iter_mles(self) -> Iterator[MLE]:
        """Get all possible MLEs for inter-molecular reactions between two assemblies.

        This function generates all MLEs (combinations of metal binding sites,
        leaving binding sites, and entering binding sites) for inter-molecular
        reactions between an initial assembly and an entering assembly
        based on the specified component kinds.

        Returned MLEs meet the following conditions:
          - The metal binding site and leaving binding site are connected to each other.
          - The component kind of the metal binding site is `mle_kind.metal`.
          - The component kind of the leaving binding site is `mle_kind.leaving`.
          - The entering binding site is free and has the component kind `mle_kind.entering`.
        """
        ml_pair = _enum_ml_pair(
            self.init_assembly,
            metal_kind=self.mle_kind.metal, leaving_kind=self.mle_kind.leaving)

        entering_sites = self.entering_assembly.find_sites(
            has_bond=False, component_kind=self.mle_kind.entering)

        for (metal, leaving), entering in itertools.product(
                ml_pair, entering_sites):
            yield MLE(metal, leaving, entering)

    def _get_unique_mles(self, mles: Iterable[MLE]) -> Iterator[MLE]:
        mles1, mles2 = itertools.tee(mles)
        unique_ml_pairs = extract_unique_site_combinations(
            [(mle.metal, mle.leaving) for mle in mles1], self.init_assembly)
        unique_entering_sites = extract_unique_site_combinations(
            [(mle.entering,) for mle in mles2], self.entering_assembly)
        for unique_ml, unique_e in itertools.product(
                unique_ml_pairs, unique_entering_sites):
            metal, leaving = unique_ml.site_comb
            (entering,) = unique_e.site_comb
            yield MLE(
                metal, leaving, entering,
                duplication=unique_ml.duplication * unique_e.duplication)

    def _perform_reaction(self, mle: MLE) -> Reaction:
        def init_renaming_func(comp_id: ID) -> ID:
            return f'init_{comp_id}'

        def entering_renaming_func(comp_id: ID) -> ID:
            return f'entering_{comp_id}'

        # Renaming
        renamed_init_assem = _rename_assembly(
            self.init_assembly, init_renaming_func)
        renamed_entering_assem = _rename_assembly(
            self.entering_assembly, entering_renaming_func)
        renamed_mle = MLE(
            metal=BindingSite(
                component_id=init_renaming_func(mle.metal.component_id),
                site_id=mle.metal.site_id),
            leaving=BindingSite(
                component_id=init_renaming_func(mle.leaving.component_id),
                site_id=mle.leaving.site_id),
            entering=BindingSite(
                component_id=entering_renaming_func(mle.entering.component_id),
                site_id=mle.entering.site_id),
            duplication=mle.duplication
        )

        raw_product = (
            _combine_assemblies(renamed_init_assem, renamed_entering_assem)
                .remove_bond(renamed_mle.metal, renamed_mle.leaving)
                .add_bond(renamed_mle.metal, renamed_mle.entering)
        )

        product, leaving = separate_if_possible(
            raw_product, metal_comp_id=renamed_mle.metal.component_id)
        
        # Double the duplication count if both assemblies are the same.
        # This is because the frequency of "A + A" is twice that of "A + B".
        if self.init_assembly == self.entering_assembly:
            dup = mle.duplication * 2
        else:
            dup = mle.duplication

        return Reaction(
            init_assem=self.init_assembly,
            entering_assem=self.entering_assembly,
            product_assem=product,
            leaving_assem=leaving,
            metal_bs=mle.metal,
            leaving_bs=mle.leaving,
            entering_bs=mle.entering,
            duplicate_count=dup
        )


def _enum_ml_pair(
        assem: Assembly, metal_kind: str, leaving_kind: str
        ) -> set[tuple[BindingSite, BindingSite]]:
    ml_pair: set[tuple[BindingSite, BindingSite]] = set()
    for bond in assem.bonds:
        site1, site2 = bond.sites
        kind1 = assem.get_component_kind_of_site(site1)
        kind2 = assem.get_component_kind_of_site(site2)
        if (kind1, kind2) == (metal_kind, leaving_kind):
            ml_pair.add((site1, site2))
        elif (kind1, kind2) == (leaving_kind, metal_kind):
            ml_pair.add((site2, site1))
    return ml_pair


class ComponentIDCollisionError(Exception):
    pass


def _rename_assembly(
        assembly: Assembly, renaming_func: Callable[[ID], ID]) -> Assembly:
    renamed_components = {
        renaming_func(id_): comp
        for id_, comp in assembly.components.items()}
    renamed_bonds = {
        Bond(comp_id1=renaming_func(site1.component_id), site1=site1.site_id,
             comp_id2=renaming_func(site2.component_id), site2=site2.site_id)
        for (site1, site2) in assembly.bonds}
    return Assembly(components=renamed_components, bonds=renamed_bonds)


def _combine_assemblies(
        init_assem: Assembly, entering_assem: Assembly,
        ) -> Assembly:
    if set(init_assem.components) & set(entering_assem.components):
        raise ComponentIDCollisionError(
            "Component ID collision detected between the two assemblies.")

    new_components = (
            dict(init_assem.components) | dict(entering_assem.components))
    new_bonds = init_assem.bonds | entering_assem.bonds
    return Assembly(components=new_components, bonds=new_bonds)
