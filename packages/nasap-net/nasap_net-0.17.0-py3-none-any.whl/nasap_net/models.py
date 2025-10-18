from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from functools import cached_property
from types import MappingProxyType
from typing import Self

from frozendict import frozendict

from nasap_net.types import ID


class IDNotSetError(Exception):
    pass


@dataclass(frozen=True, order=True)
class BindingSite:
    """A specific binding site on a specific component."""
    component_id: ID
    site_id: ID


@dataclass(frozen=True, init=False)
class Bond(Iterable):
    """A bond between two binding sites on two components."""
    sites: tuple[BindingSite, BindingSite]

    def __init__(self, comp_id1: ID, site1: ID, comp_id2: ID, site2: ID):
        if comp_id1 == comp_id2:
            raise ValueError("Components in a bond must be different.")
        comp_and_site1 = BindingSite(component_id=comp_id1, site_id=site1)
        comp_and_site2 = BindingSite(component_id=comp_id2, site_id=site2)
        object.__setattr__(
            self, 'sites',
            tuple(sorted((comp_and_site1, comp_and_site2))))  # type:ignore

    def __iter__(self) -> Iterator[BindingSite]:
        return iter(self.sites)

    @property
    def component_ids(self) -> tuple[ID, ID]:
        """Return the component IDs involved in the bond."""
        return self.sites[0].component_id, self.sites[1].component_id

    @classmethod
    def from_sites(cls, site1: BindingSite, site2: BindingSite) -> 'Bond':
        """Create a Bond from two BindingSite instances."""
        return cls(
            comp_id1=site1.component_id,
            comp_id2=site2.component_id,
            site1=site1.site_id,
            site2=site2.site_id
            )


@dataclass(frozen=True)
class AuxEdge:
    """An auxiliary edge between two binding sites on the same component."""
    site_id1: ID
    site_id2: ID
    kind: str | None = None

    def get_binding_sites(
            self, comp_id: ID) -> tuple[BindingSite, BindingSite]:
        """Return the binding sites of this auxiliary edge."""
        return (
            BindingSite(component_id=comp_id, site_id=self.site_id1),
            BindingSite(component_id=comp_id, site_id=self.site_id2)
        )


@dataclass(frozen=True, init=False)
class Component:
    """Component"""
    kind: str
    site_ids: frozenset[ID]
    aux_edges: frozenset[AuxEdge]

    def __init__(
            self, kind: str, sites: Iterable[ID],
            aux_edges: Iterable[AuxEdge] | None = None
            ):
        object.__setattr__(self, 'kind', kind)
        object.__setattr__(self, 'site_ids', frozenset(sites))
        if aux_edges is None:
            aux_edges = frozenset()
        else:
            aux_edges = frozenset(aux_edges)
        object.__setattr__(self, 'aux_edges', aux_edges)

    def get_binding_sites(self, comp_id: ID) -> frozenset[BindingSite]:
        """Return the binding sites of this component."""
        return frozenset(
            BindingSite(component_id=comp_id, site_id=site_id)
            for site_id in self.site_ids
        )


class InvalidBondError(Exception):
    def __init__(self, *, bond: Bond, msg: str = ""):
        self.bond = bond
        combined_msg = f"Invalid bond: {bond}"
        if msg:
            combined_msg += f" - {msg}"
        super().__init__(combined_msg)


@dataclass(frozen=True, init=False)
class Assembly:
    """An assembly of components connected by bonds.

    Parameters
    ----------
    components : Mapping[C, Component[S]]
        A mapping from component IDs to their corresponding components.
    bonds : Iterable[Bond[C, S]]
        An iterable of bonds connecting the components.

    Raises
    ------
    ValueError
        - If any bond references a non-existent component or site.
        - If a component bonds to itself.
        - If a site is used more than once.
        - If the assembly is not connected.

    Warnings
    --------
    - The assembly does not enforce connectivity; it is the user's
      responsibility to ensure that the assembly is connected as needed.
    """
    _components: frozendict[ID, Component]
    bonds: frozenset[Bond]
    _id: ID | None

    def __init__(
            self, components: Mapping[ID, Component],
            bonds: Iterable[Bond],
            *,
            id_: ID | None = None
            ):
        object.__setattr__(self, '_components', frozendict(components))
        object.__setattr__(self, 'bonds', frozenset(bonds))
        object.__setattr__(self, '_id', id_)
        self._validate()

    @property
    def id(self) -> ID:
        """Return the ID of the assembly."""
        if self._id is None:
            raise IDNotSetError("Assembly ID is not set.")
        return self._id

    def _validate(self):
        component_keys = set(self._components.keys())
        used_sites = set()
        for bond in self.bonds:
            # Validate that the components exist
            for comp_id in bond.component_ids:
                if comp_id not in component_keys:
                    raise InvalidBondError(
                        bond=bond,
                        msg=f"Component {comp_id} not found in assembly.")

            # Validate that the sites exist in the respective components
            for site in bond.sites:
                component = self._components[site.component_id]
                if site.site_id not in component.site_ids:
                    raise InvalidBondError(
                        bond=bond,
                        msg=(
                            f"Site {site.site_id} not found in component "
                            f"{site.component_id}."))

                # Validate that the site is not already used
                if site in used_sites:
                    raise InvalidBondError(
                        bond=bond,
                        msg=f"Site {site} is already used in another bond.")
                used_sites.add(site)

    @property
    def components(self) -> Mapping[ID, Component]:
        """Return the components in the assembly as an immutable mapping."""
        return MappingProxyType(self._components)

    def _get_component_of_site(self, site: BindingSite) -> Component:
        """Return the component corresponding to the given binding site."""
        return self._components[site.component_id]

    def get_component_kind_of_site(self, site: BindingSite) -> str:
        """Return the component kind of the given binding site."""
        return self._components[site.component_id].kind

    def find_sites(
            self, *, has_bond: bool | None = None,
            component_kind: str | None = None
            ) -> frozenset[BindingSite]:
        """Return binding sites based on their bond status.
        """
        if has_bond is None and component_kind is None:
            return self._all_sites

        sites = set()
        for site in self._all_sites:
            if has_bond is not None:
                if has_bond != self.has_bond(site):
                    continue
            if component_kind is not None:
                if self.get_component_kind_of_site(site) != component_kind:
                    continue
            sites.add(site)
        return frozenset(sites)

    def has_bond(self, site: BindingSite) -> bool:
        """Check if a binding site has a bond."""
        return site in self._site_connection

    @cached_property
    def _all_sites(self) -> frozenset[BindingSite]:
        """Return all binding sites in the assembly."""
        sites = set()
        for comp_id, component in self._components.items():
            for site in component.site_ids:
                sites.add(BindingSite(component_id=comp_id, site_id=site))
        return frozenset(sites)

    @cached_property
    def _site_connection(self) -> Mapping[BindingSite, BindingSite]:
        """Return a mapping of each binding site to its connected binding site.

        Only bonded sites are included in the mapping.
        """
        connection = {}
        for bond in self.bonds:
            site1, site2 = bond.sites
            connection[site1] = site2
            connection[site2] = site1
        return MappingProxyType(connection)

    def add_bond(self, site1: BindingSite, site2: BindingSite):
        """Return a new assembly with an additional bond."""
        new_bond = Bond.from_sites(site1, site2)
        new_bonds = set(self.bonds)
        new_bonds.add(new_bond)
        return self.copy_with(bonds=new_bonds)

    def remove_bond(self, site1: BindingSite, site2: BindingSite):
        """Return a new assembly with a bond removed."""
        bond_to_remove = Bond.from_sites(site1, site2)
        new_bonds = set(self.bonds)
        new_bonds.remove(bond_to_remove)
        return self.copy_with(bonds=new_bonds)

    def copy_with(
            self,
            *,
            components: Mapping[ID, Component] | None = None,
            bonds: Iterable[Bond] | None = None,
            id_: ID | None = None,
            ) -> Self:
        """Return a copy of the assembly with optional modifications."""
        if components is None:
            components = self.components
        if bonds is None:
            bonds = self.bonds
        return self.__class__(
            components=components, bonds=bonds, id_=id_)
