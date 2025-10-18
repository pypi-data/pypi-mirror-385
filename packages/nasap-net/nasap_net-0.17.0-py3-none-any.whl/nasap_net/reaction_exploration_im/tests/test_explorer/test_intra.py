import pytest

from nasap_net.models import Assembly, AuxEdge, BindingSite, Bond, Component
from nasap_net.reaction_exploration_im.explorer import IntraReactionExplorer
from nasap_net.reaction_exploration_im.models import MLE, MLEKind, Reaction


@pytest.fixture
def M() -> Component:
    return Component(
        kind='M', sites=[0, 1, 2, 3],
        aux_edges=[AuxEdge(0, 1), AuxEdge(1, 2), AuxEdge(2, 3), AuxEdge(3, 0)])

@pytest.fixture
def L() -> Component:
    return Component(kind='L', sites=[0, 1])

@pytest.fixture
def X() -> Component:
    return Component(kind='X', sites=[0])

@pytest.fixture
def ML2X2_cis(M, L, X) -> Assembly:
    return Assembly(
        id_='ML2X2_cis',
        components={'M0': M, 'L0': L, 'L1': L, 'X0': X, 'X1': X},
        bonds=[
            Bond('M0', 0, 'X0', 0),
            Bond('M0', 1, 'X1', 0),
            Bond('M0', 2, 'L0', 0),
            Bond('M0', 3, 'L1', 0),
        ]
    )

@pytest.fixture
def ML2X_trans_ring(M, L, X) -> Assembly:
    return Assembly(
        components={'M0': M, 'L0': L, 'L1': L, 'X1': X},
        bonds=[
            Bond('M0', 0, 'L0', 1),
            Bond('M0', 1, 'X1', 0),
            Bond('M0', 2, 'L0', 0),
            Bond('M0', 3, 'L1', 0),
        ]
    )

@pytest.fixture
def ML2X_cis_ring(M, L, X) -> Assembly:
    return Assembly(
        components={'M0': M, 'L0': L, 'L1': L, 'X1': X},
        bonds=[
            Bond('M0', 0, 'L1', 1),
            Bond('M0', 1, 'X1', 0),
            Bond('M0', 2, 'L0', 0),
            Bond('M0', 3, 'L1', 0)
        ]
    )

@pytest.fixture
def free_X(X) -> Assembly:
    return Assembly(
        components={'X0': X},
        bonds=[]
    )


def test_explore(ML2X2_cis, ML2X_trans_ring, ML2X_cis_ring, free_X):
    explorer = IntraReactionExplorer(ML2X2_cis, MLEKind('M', 'X', 'L'))
    assert set(explorer.explore()) == {
        Reaction(
            init_assem=ML2X2_cis,
            entering_assem=None,
            product_assem=ML2X_trans_ring,
            leaving_assem=free_X,
            metal_bs=BindingSite('M0', 0),
            leaving_bs=BindingSite('X0', 0),
            entering_bs=BindingSite('L0', 1),
            duplicate_count=2
        ),
        Reaction(
            init_assem=ML2X2_cis,
            entering_assem=None,
            product_assem=ML2X_cis_ring,
            leaving_assem=free_X,
            metal_bs=BindingSite('M0', 0),
            leaving_bs=BindingSite('X0', 0),
            entering_bs=BindingSite('L1', 1),
            duplicate_count=2
        )
    }


def test__iter_mles(ML2X2_cis):
    explorer = IntraReactionExplorer(ML2X2_cis, MLEKind('M', 'X', 'L'))
    mles = set(explorer._iter_mles())
    assert mles == {
        MLE(BindingSite('M0', 0), BindingSite('X0', 0), BindingSite('L0', 1)),
        MLE(BindingSite('M0', 0), BindingSite('X0', 0), BindingSite('L1', 1)),
        MLE(BindingSite('M0', 1), BindingSite('X1', 0), BindingSite('L0', 1)),
        MLE(BindingSite('M0', 1), BindingSite('X1', 0), BindingSite('L1', 1)),
    }


def test__get_unique_mles(ML2X2_cis):
    explorer = IntraReactionExplorer(ML2X2_cis, MLEKind('M', 'X', 'L'))
    mles = {
        MLE(BindingSite('M0', 0), BindingSite('X0', 0), BindingSite('L0', 1)),
        MLE(BindingSite('M0', 0), BindingSite('X0', 0), BindingSite('L1', 1)),
        MLE(BindingSite('M0', 1), BindingSite('X1', 0), BindingSite('L0', 1)),
        MLE(BindingSite('M0', 1), BindingSite('X1', 0), BindingSite('L1', 1)),
    }
    assert set(explorer._get_unique_mles(mles)) == {
        MLE(
            BindingSite('M0', 0), BindingSite('X0', 0), BindingSite('L0', 1),
            duplication=2),
        MLE(
            BindingSite('M0', 0), BindingSite('X0', 0), BindingSite('L1', 1),
            duplication=2),
    }


def test__perform_reaction(ML2X2_cis, ML2X_trans_ring, free_X):
    explorer = IntraReactionExplorer(ML2X2_cis, MLEKind('M', 'X', 'L'))
    mle_with_dup = MLE(
        BindingSite('M0', 0), BindingSite('X0', 0), BindingSite('L0', 1),
        duplication=2)

    assert explorer._perform_reaction(mle_with_dup) == Reaction(
        init_assem=ML2X2_cis,
        entering_assem=None,
        product_assem=ML2X_trans_ring,
        leaving_assem=free_X,
        metal_bs=BindingSite('M0', 0),
        leaving_bs=BindingSite('X0', 0),
        entering_bs=BindingSite('L0', 1),
        duplicate_count=2
    )
