from frozendict import frozendict

from nasap_net.isomorphism import Isomorphism, get_all_isomorphisms
from nasap_net.models import Assembly, BindingSite, Bond, Component


def test_get_all_isomorphisms():
    M = Component(kind='M', sites=[0, 1])
    X = Component(kind='X', sites=[0])
    MX2 = Assembly(
        components={'M1': M, 'X1': X, 'X2': X},
        bonds=[Bond('M1', 0, 'X1', 0), Bond('M1', 1, 'X2', 0)]
    )
    MX2_2 = Assembly(
        components={'M10': M, 'X10': X, 'X20': X},
        bonds=[Bond('M10', 0, 'X10', 0), Bond('M10', 1, 'X20', 0)]
    )

    isoms = get_all_isomorphisms(MX2, MX2_2)
    assert len(isoms) == 2
    assert isoms == {
        Isomorphism(
            comp_id_mapping=frozendict(
                {'M1': 'M10', 'X1': 'X10', 'X2': 'X20'}),
            binding_site_mapping=frozendict({
                BindingSite('M1', 0): BindingSite('M10', 0),
                BindingSite('M1', 1): BindingSite('M10', 1),
                BindingSite('X1', 0): BindingSite('X10', 0),
                BindingSite('X2', 0): BindingSite('X20', 0),
            })
        ),
        Isomorphism(
            comp_id_mapping=frozendict(
                {'M1': 'M10', 'X1': 'X20', 'X2': 'X10'}),
            binding_site_mapping=frozendict({
                BindingSite('M1', 0): BindingSite('M10', 1),
                BindingSite('M1', 1): BindingSite('M10', 0),
                BindingSite('X1', 0): BindingSite('X20', 0),
                BindingSite('X2', 0): BindingSite('X10', 0),
            })
        ),
    }
