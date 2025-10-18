from collections import defaultdict
from collections.abc import Hashable, Iterable
from dataclasses import dataclass, field

from frozendict import frozendict

from nasap_net.isomorphism import is_isomorphic
from nasap_net.models import Assembly


class AssemblyNotFoundError(Exception):
    """Exception raised when no isomorphic assembly is found in the search space."""
    pass


@dataclass(frozen=True, init=False)
class IsomorphicAssemblyFinder:
    """Class to find isomorphic assemblies in a search space.

    Parameters
    ----------
    search_space : Iterable[Assembly]
        The search space of assemblies to find isomorphic assemblies from.
    """
    search_space: frozenset[Assembly]
    _sig_to_assemblies: frozendict[Hashable, frozenset[Assembly]] = field(init=False)

    def __init__(self, search_space: Iterable[Assembly]) -> None:
        object.__setattr__(self, 'search_space', frozenset(search_space))
        sig_to_assems: defaultdict[Hashable, set[Assembly]] = defaultdict(set)
        for assembly in self.search_space:
            sig = light_signature(assembly)
            sig_to_assems[sig].add(assembly)
        object.__setattr__(self, '_sig_to_assemblies', frozendict(
            {k: frozenset(v) for k, v in sig_to_assems.items()}
        ))

    def find(self, target: Assembly) -> Assembly:
        """Find an isomorphic assembly in the search space.

        Parameters
        ----------
        target : Assembly
            The target assembly to find an isomorphic assembly for.

        Returns
        -------
        Assembly
            An assembly from the search space that is isomorphic to the target.

        Raises
        ------
        AssemblyNotFoundError
            If no isomorphic assembly is found in the search space.
        """
        sig = light_signature(target)
        candidates = self._sig_to_assemblies.get(sig)
        if not candidates:
            raise AssemblyNotFoundError(
                f"No isomorphic assembly found for {target}")
        for candidate in candidates:
            if is_isomorphic(target, candidate):
                return candidate
        raise AssemblyNotFoundError(
            f"No isomorphic assembly found for {target}")


def light_signature(assembly: Assembly) -> Hashable:
    """Compute a light signature of the assembly for quick filtering.

    Assemblies with different signatures are guaranteed to be non-isomorphic.
    Assemblies with the same signature may or may not be isomorphic.

    The signature consists of:
    - A sorted tuple of component kinds.
    - A sorted tuple of sorted tuples of bond component kinds.

    Parameters
    ----------
    assembly : Assembly
        The assembly to compute the signature for.

    Returns
    -------
    Hashable
        The light signature of the assembly.
    """
    return (
        # component kinds
        tuple(sorted(comp.kind for comp in assembly.components.values())),
        # bond component kinds
        tuple(sorted(
            tuple(sorted([
                assembly.get_component_kind_of_site(site1),
                assembly.get_component_kind_of_site(site2),
            ]))
            for site1, site2 in assembly.bonds
        ))
    )
