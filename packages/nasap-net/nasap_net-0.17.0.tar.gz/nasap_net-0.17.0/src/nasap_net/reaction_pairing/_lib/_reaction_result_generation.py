from dataclasses import dataclass

from nasap_net import Assembly, perform_inter_exchange, perform_intra_exchange


@dataclass(frozen=True)
class _ReactionResult:
    product_assembly: Assembly
    leaving_assembly: Assembly | None
    metal_bs: str
    leaving_bs: str
    entering_bs: str


def _generate_reaction_result(
        init_assembly: Assembly, entering_assembly: Assembly | None,
        metal_bs: str, leaving_bs: str, entering_bs: str
        ) -> _ReactionResult:
    if entering_assembly is None:  # intra
        product, leaving = perform_intra_exchange(
            init_assembly, metal_bs, leaving_bs, entering_bs)
        return _ReactionResult(
            product, leaving, metal_bs, leaving_bs, entering_bs)
    else:
        product, leaving = perform_inter_exchange(
            init_assembly, entering_assembly,
            metal_bs, leaving_bs, entering_bs)
        # Note that the `perform_inter_exchange` renames binding sites.
        return _ReactionResult(
            product, leaving,
            f'init_{metal_bs}',
            f'init_{leaving_bs}',
            f'entering_{entering_bs}',
            )
