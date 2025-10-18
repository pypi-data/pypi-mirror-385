from dataclasses import dataclass

from nasap_net.models import Assembly, BindingSite
from nasap_net.types import ID


@dataclass(frozen=True)
class MLEKind:
    metal: str
    leaving: str
    entering: str


class DuplicationNotSetError(Exception):
    pass


@dataclass(frozen=True, init=False)
class MLE:
    metal: BindingSite
    leaving: BindingSite
    entering: BindingSite
    _duplication: int | None = None

    def __init__(
            self,
            metal: BindingSite,
            leaving: BindingSite,
            entering: BindingSite,
            *,
            duplication: int | None = None
    ) -> None:
        object.__setattr__(self, 'metal', metal)
        object.__setattr__(self, 'leaving', leaving)
        object.__setattr__(self, 'entering', entering)
        object.__setattr__(self, '_duplication', duplication)

    @property
    def duplication(self) -> int:
        if self._duplication is None:
            raise DuplicationNotSetError("Duplication count is not set.")
        return self._duplication


@dataclass(frozen=True)
class Reaction:
    init_assem: Assembly
    entering_assem: Assembly | None
    product_assem: Assembly
    leaving_assem: Assembly | None
    metal_bs: BindingSite
    leaving_bs: BindingSite
    entering_bs: BindingSite
    duplicate_count: int

    @property
    def init_assem_id(self) -> ID:
        return self.init_assem.id

    @property
    def entering_assem_id(self) -> ID | None:
        if self.entering_assem is None:
            return None
        id_ = self.entering_assem.id
        if id_ is None:
            raise ValueError("Entering assembly does not have an ID.")
        return id_
