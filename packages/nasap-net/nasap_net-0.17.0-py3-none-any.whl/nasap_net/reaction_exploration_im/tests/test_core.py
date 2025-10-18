from nasap_net.models import Assembly, Bond, Component
from nasap_net.reaction_exploration_im import MLEKind, explore_reactions


def test():
    M = Component(kind='M', sites=[0, 1])
    L = Component(kind='L', sites=[0, 1])
    X = Component(kind='X', sites=[0])
    assemblies = {
        # MX2: X0(0)-(0)M0(1)-(0)X1
        'MX2': Assembly(
            components={'X0': X, 'M0': M, 'X1': X},
            bonds=[Bond('X0', 0, 'M0', 0), Bond('M0', 1, 'X1', 0)]),
        'free_L': Assembly(components={'L0': L}, bonds=[]),
        'free_X': Assembly(components={'X0': X}, bonds=[]),
        # MLX: (0)L0(1)-(0)M0(1)-(0)X0
        'MLX': Assembly(
            components={'L0': L, 'M0': M, 'X0': X},
            bonds=[Bond('L0', 1, 'M0', 0), Bond('M0', 1, 'X0', 0)]),
        # ML2: (0)L0(1)-(0)M0(1)-(0)L1(1)
        'ML2': Assembly(
            components={'L0': L, 'M0': M, 'L1': L},
            bonds=[Bond('L0', 1, 'M0', 0), Bond('M0', 1, 'L1', 0)]),
        # M2L2X: X0(0)-(0)M0(1)-(0)L0(1)-(0)M1(1)-(0)L1(1)
        'M2L2X': Assembly(
            components={'X0': X, 'M0': M, 'L0': L, 'M1': M, 'L1': L},
            bonds=[Bond('X0', 0, 'M0', 0), Bond('M0', 1, 'L0', 0),
                   Bond('L0', 1, 'M1', 0), Bond('M1', 1, 'L1', 0)]),
        # M2LX2: X0(0)-(0)M0(1)-(0)L0(1)-(0)M1(1)-(0)X1
        'M2LX2': Assembly(
            components={'X0': X, 'M0': M, 'L0': L, 'M1': M, 'X1': X},
            bonds=[Bond('X0', 0, 'M0', 0), Bond('M0', 1, 'L0', 0),
                   Bond('L0', 1, 'M1', 0), Bond('M1', 1, 'X1', 0)]),
        # M2L2-ring: //-(0)M0(1)-(0)L0(1)-(0)M1(1)-(0)L1(1)-//
        'M2L2-ring': Assembly(
            components={'M0': M, 'L0': L, 'M1': M, 'L1': L},
            bonds=[Bond('M0', 1, 'L0', 0), Bond('L0', 1, 'M1', 0),
                   Bond('M1', 1, 'L1', 0), Bond('L1', 1, 'M0', 0)]),
    }
    result = set(explore_reactions(assemblies, [MLEKind('M', 'X', 'L')]))
    # TODO: add more detailed checks
    assert len(result) == 7
