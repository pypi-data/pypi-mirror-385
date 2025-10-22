import enum

from fred.ogd.layer.interface import LayerInterface
from fred.ogd.layer._landing import LayerLanding


class LayerCatalog(enum.Enum):
    LANDING = LayerLanding

    def auto(self, **kwargs) -> LayerInterface:
        match self:
            case self.LANDING:
                return LayerLanding.auto(**kwargs)
            case _:
                raise NotImplementedError(f"Auto instantiation not implemented for {self.name}")
