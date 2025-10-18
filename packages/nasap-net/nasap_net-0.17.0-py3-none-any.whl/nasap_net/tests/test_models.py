from dataclasses import FrozenInstanceError

import pytest

from nasap_net.models import Assembly, BindingSite, Bond, Component


def test_component():
    M = Component(kind="M", sites=["a", "b"])
    assert M.kind == "M"
    assert M.site_ids == frozenset({"a", "b"})


def test_component_immutability():
    M = Component(kind="M", sites=["a", "b"])
    with pytest.raises(FrozenInstanceError):
        M.kind = "M2"
    with pytest.raises(FrozenInstanceError):
        M.site_ids = frozenset({"c"})


def test_binding_site():
    site = BindingSite(component_id="M1", site_id="a")
    assert site.component_id == "M1"
    assert site.site_id == "a"


def test_binding_site_ordering():
    site1 = BindingSite(component_id="M1", site_id="a")
    site2 = BindingSite(component_id="M1", site_id="b")
    site3 = BindingSite(component_id="M2", site_id="a")
    assert site1 < site2
    assert site1 < site3
    assert site2 < site3


def test_binding_site_equality():
    site1 = BindingSite(component_id="M1", site_id="a")
    site2 = BindingSite(component_id="M1", site_id="a")
    site3 = BindingSite(component_id="M1", site_id="b")
    assert site1 == site2
    assert site1 != site3


def test_bond():
    bond = Bond(comp_id1="L1", site1="a", comp_id2="M1", site2="b")
    assert bond.sites == (
        BindingSite(component_id="L1", site_id="a"),
        BindingSite(component_id="M1", site_id="b")
        )


def test_binding_site_ordering_in_bond():
    bond1 = Bond(comp_id1="L1", site1="a", comp_id2="M1", site2="b")
    bond2 = Bond(comp_id1="M1", site1="b", comp_id2="L1", site2="a")
    assert bond1 == bond2
    assert bond1.sites[0] < bond1.sites[1]


def test_bond_same_site_error():
    with pytest.raises(ValueError):
        Bond(comp_id1="M1", site1="a", comp_id2="M1", site2="b")
    # Should not raise
    Bond(comp_id1="M1", site1="a", comp_id2="M2", site2="a")


def test_assembly():
    L = Component(kind="L", sites={"a", "b"})
    M = Component(kind="M", sites={"a", "b"})
    assembly = Assembly(
        components={"L1": L, "M1": M},
        bonds={Bond(comp_id1="L1", site1="a", comp_id2="M1", site2="a")}
        )
    assert assembly.components == {"L1": L, "M1": M}
    assert assembly.bonds == frozenset({
        Bond(comp_id1="L1", site1="a", comp_id2="M1", site2="a")})
