
class LayerInterface:
    
    @classmethod
    def auto(cls, **kwargs) -> "LayerInterface":
        raise NotImplementedError("Auto instantiation not implemented for base LayerInterface")

    def run(self, **kwargs) -> bool:
        raise NotImplementedError("Run method not implemented for base LayerInterface")
