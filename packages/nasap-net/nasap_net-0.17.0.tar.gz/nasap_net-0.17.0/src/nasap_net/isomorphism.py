from collections.abc import Hashable, Mapping
from dataclasses import dataclass

import igraph as ig
from bidict import frozenbidict
from frozendict import frozendict

from nasap_net.models import Assembly, BindingSite
from nasap_net.types import ID


@dataclass(frozen=True, init=False)
class GraphConversionResult:
    graph: ig.Graph
    core_mapping: frozenbidict[ID, int]
    binding_site_mapping: frozenbidict[BindingSite, int]

    def __init__(
            self,
            graph: ig.Graph,
            core_mapping: Mapping[ID, int],
            binding_site_mapping: Mapping[BindingSite, int],
    ) -> None:
        object.__setattr__(self, 'graph', graph)
        object.__setattr__(
            self, 'core_mapping', frozenbidict(core_mapping))
        object.__setattr__(
            self, 'binding_site_mapping',
            frozenbidict(binding_site_mapping))


def convert_assembly_to_igraph(assembly: Assembly) -> GraphConversionResult:
    g = ig.Graph()
    core_mapping = {}
    binding_site_mapping = {}

    for comp_id, comp in assembly.components.items():
        # Add the core node
        g.add_vertices(  # More efficient than add_vertex
            1,
            {
                'comp_id': [comp_id],
                'comp_kind': [comp.kind],
                'core_or_site': ['core'],
            }
        )
        core_mapping[comp_id] = g.vcount() - 1

        # Add the binding sites
        g.add_vertices(
            len(comp.site_ids),
            {
                'comp_id': [comp_id] * len(comp.site_ids),
                'comp_kind': [comp.kind] * len(comp.site_ids),
                'core_or_site': ['site'] * len(comp.site_ids),
                'site_id': list(comp.site_ids),
            }
        )
        start_id = g.vcount() - len(comp.site_ids)
        for i, site in enumerate(comp.get_binding_sites(comp_id)):
            binding_site_mapping[site] = start_id + i

        # Add the edges between core and sites
        g.add_edges(
            [(core_mapping[comp_id], binding_site_mapping[site])
                for site in comp.get_binding_sites(comp_id)]
        )

        # Add the auxiliary edges
        for aux in comp.aux_edges:
            site1, site2 = aux.get_binding_sites(comp_id)
            if aux.kind is None:
                g.add_edges(
                    [(
                        binding_site_mapping[site1],
                        binding_site_mapping[site2]
                    )]
                )
            else:
                g.add_edges(
                    [(
                        binding_site_mapping[site1],
                        binding_site_mapping[site2]
                    )],
                    {'aux_kind': [aux.kind]}
                )

    # Add the bonds
    for bond in assembly.bonds:
        site1, site2 = bond.sites
        g.add_edge(
            binding_site_mapping[site1],
            binding_site_mapping[site2]
        )

    return GraphConversionResult(
        graph=g,
        core_mapping=core_mapping,
        binding_site_mapping=binding_site_mapping
    )


def is_isomorphic(assem1: Assembly, assem2: Assembly) -> bool:
    g1 = convert_assembly_to_igraph(assem1).graph
    g2 = convert_assembly_to_igraph(assem2).graph

    try:
        colors = _color_vertices_and_edges(g1, g2)
    except NoIsomorphismFoundError:
        return False

    return g1.isomorphic_vf2(
        g2,
        color1=colors.v_color1,
        color2=colors.v_color2,
        edge_color1=colors.e_color1,
        edge_color2=colors.e_color2,
    )


class NoIsomorphismFoundError(Exception):
    pass


@dataclass(frozen=True, init=False)
class Isomorphism:
    comp_id_mapping: frozendict[ID, ID]
    binding_site_mapping: frozendict[BindingSite, BindingSite]

    def __init__(
            self,
            comp_id_mapping: Mapping[ID, ID],
            binding_site_mapping: Mapping[BindingSite, BindingSite]
    ) -> None:
        object.__setattr__(
            self, 'comp_id_mapping', frozendict(comp_id_mapping))
        object.__setattr__(
            self, 'binding_site_mapping', frozendict(binding_site_mapping))


def get_isomorphism(assem1: Assembly, assem2: Assembly) -> Isomorphism:
    conv_res1 = convert_assembly_to_igraph(assem1)
    conv_res2 = convert_assembly_to_igraph(assem2)

    g1 = conv_res1.graph
    g2 = conv_res2.graph

    try:
        colors = _color_vertices_and_edges(g1, g2)
    except NoIsomorphismFoundError:
        raise NoIsomorphismFoundError() from None

    mapping: list[int]
    _, mapping, _ = g1.isomorphic_vf2(
        g2,
        color1=colors.v_color1,
        color2=colors.v_color2,
        edge_color1=colors.e_color1,
        edge_color2=colors.e_color2,
        return_mapping_12=True,
    )

    return _decode_mapping(mapping, conv_res1, conv_res2)


def get_all_isomorphisms(
        assem1: Assembly, assem2: Assembly) -> set[Isomorphism]:
    conv_res1 = convert_assembly_to_igraph(assem1)
    conv_res2 = convert_assembly_to_igraph(assem2)

    try:
        colors = _color_vertices_and_edges(conv_res1.graph, conv_res2.graph)
    except NoIsomorphismFoundError:
        raise NoIsomorphismFoundError() from None

    res: list[list[int]] = conv_res1.graph.get_isomorphisms_vf2(
        conv_res2.graph,
        color1=colors.v_color1,
        color2=colors.v_color2,
        edge_color1=colors.e_color1,
        edge_color2=colors.e_color2,
    )

    return {_decode_mapping(mapping, conv_res1, conv_res2) for mapping in res}


def _decode_mapping(
        mapping: list[int],
        conv_res1: GraphConversionResult,
        conv_res2: GraphConversionResult,
) -> Isomorphism:
    comp_id_mapping = {}
    binding_site_mapping = {}
    for v1, v2 in enumerate(mapping):
        if v1 in conv_res1.core_mapping.inv:
            comp_id1 = conv_res1.core_mapping.inv[v1]
            comp_id2 = conv_res2.core_mapping.inv[v2]
            comp_id_mapping[comp_id1] = comp_id2
        else:
            assert v1 in conv_res1.binding_site_mapping.inv
            site1 = conv_res1.binding_site_mapping.inv[v1]
            site2 = conv_res2.binding_site_mapping.inv[v2]
            binding_site_mapping[site1] = site2
    return Isomorphism(
        comp_id_mapping=comp_id_mapping,
        binding_site_mapping=binding_site_mapping
    )


@dataclass(frozen=True)
class _Colors:
    v_color1: tuple[int, ...]
    v_color2: tuple[int, ...]
    e_color1: tuple[int, ...]
    e_color2: tuple[int, ...]


def _color_vertices_and_edges(g1: ig.Graph, g2: ig.Graph) -> _Colors:
    try:
        v_color1, v_color2 = _vertex_color_lists(g1, g2)
    except _NotIsomorphicError:
        raise NoIsomorphismFoundError() from None

    try:
        e_color1, e_color2 = _edge_color_lists(g1, g2)
    except _NotIsomorphicError:
        raise NoIsomorphismFoundError() from None

    return _Colors(
        v_color1=tuple(v_color1),
        v_color2=tuple(v_color2),
        e_color1=tuple(e_color1),
        e_color2=tuple(e_color2),
    )


class _NotIsomorphicError(Exception):
    pass


def _vertex_color_lists(
        g1: ig.Graph, g2: ig.Graph) -> tuple[list[int], list[int]]:
    def _readable_v_color(vertex: ig.Vertex) -> Hashable:
        return vertex['core_or_site'], vertex['comp_kind']

    colors1 = {_readable_v_color(v) for v in g1.vs}
    colors2 = {_readable_v_color(v) for v in g2.vs}
    if colors1 != colors2:
        raise _NotIsomorphicError()

    color_to_int: dict[Hashable, int] = {c: i for i, c in enumerate(colors1)}
    color_list1 = [color_to_int[_readable_v_color(v)] for v in g1.vs]
    color_list2 = [color_to_int[_readable_v_color(v)] for v in g2.vs]
    return color_list1, color_list2


def _edge_color_lists(
        g1: ig.Graph, g2: ig.Graph) -> tuple[list[int], list[int]]:
    def _readable_edge_color(edge: ig.Edge) -> Hashable | None:
        return edge['aux_kind'] if 'aux_kind' in edge.attributes() else None

    colors1 = {_readable_edge_color(e) for e in g1.es}
    colors2 = {_readable_edge_color(e) for e in g2.es}
    if colors1 != colors2:
        raise _NotIsomorphicError()

    color_to_int: dict[Hashable | None, int] = {
        c: i for i, c in enumerate(colors1)}
    color_list1 = [color_to_int[_readable_edge_color(e)] for e in g1.es]
    color_list2 = [color_to_int[_readable_edge_color(e)] for e in g2.es]
    return color_list1, color_list2
