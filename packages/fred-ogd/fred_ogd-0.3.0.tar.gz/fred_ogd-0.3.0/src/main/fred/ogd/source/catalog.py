import enum

from fred.ogd.source.interface import SourceInterface
from fred.ogd.source._request import SourceRequest


class SourceCatalog(enum.Enum):
    REQUEST = SourceRequest

    def auto(self, **kwargs) -> SourceInterface:
        match self:
            case self.REQUEST:
                return SourceRequest(**kwargs)
            case _:
                raise NotImplementedError(f"Auto instantiation not implemented for {self.name}")
