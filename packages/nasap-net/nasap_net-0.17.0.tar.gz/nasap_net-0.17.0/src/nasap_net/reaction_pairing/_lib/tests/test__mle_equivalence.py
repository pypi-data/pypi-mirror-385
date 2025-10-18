import pytest

from nasap_net import Assembly, Component
from nasap_net.reaction_pairing._lib import _are_equivalent_mles
from nasap_net.reaction_pairing.models import _MLE


@pytest.fixture
def components():
    return {
        'L': Component(['a', 'b']),
        'M': Component(['a', 'b']),
        'X': Component(['a']),
    }


def test_inter(components):
    # MX2 + L (-> MLX + X)
    # Although the metal and leaving binding sites are different,
    # the pair of binding sites (metal, leaving) are equivalent, i.e.,
    # (M0.a, X0.a) is equivalent to (M0.b, X1.a).
    MX2 = Assembly(
        {'M0': 'M', 'X0': 'X', 'X1': 'X'},
        [('X0.a', 'M0.a'), ('M0.b', 'X1.a')]
        )
    L = Assembly({'L0': 'L'})
    assert _are_equivalent_mles(
        MX2, L,
        _MLE('M0.a', 'X0.a', 'L0.a'),
        _MLE('M0.b', 'X1.a', 'L0.a'),
        components)


def test_intra(components):
    # Add an additional assembly M2L3
    # M2L3: (a)L0(b)-(a)M0(b)-(a)L1(b)-(a)M1(b)-(a)L2(b)
    M2L3 = Assembly(
        {'M0': 'M', 'M1': 'M', 'L0': 'L', 'L1': 'L', 'L2': 'L'},
        [('L0.b', 'M0.a'), ('M0.b', 'L1.a'), ('L1.b', 'M1.a'),
         ('M1.b', 'L2.a')]
        )

    # M2L3 (-> M2L2-ring + L)
    # Although the metal and leaving binding sites are different,
    # the trio of binding sites (metal, leaving, entering) are equivalent,
    # i.e., (M0.a, L0.b, L2.b) is equivalent to (M1.b, L2.a, L0.a).
    assert _are_equivalent_mles(
        M2L3, None,
        _MLE('M0.a', 'L0.b', 'L2.b'),
        _MLE('M1.b', 'L2.a', 'L0.a'),
        components)
