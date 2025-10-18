from dataclasses import dataclass
from typing import Generic

from nasap_net.types import A


@dataclass(frozen=True)
class Reaction(Generic[A]):
    init_assem_id: A
    entering_assem_id: A | None
    product_assem_id: A
    leaving_assem_id: A | None
    metal_bs: str
    leaving_bs: str
    entering_bs: str


@dataclass(frozen=True)
class _MLE:
    metal: str
    leaving: str
    entering: str
