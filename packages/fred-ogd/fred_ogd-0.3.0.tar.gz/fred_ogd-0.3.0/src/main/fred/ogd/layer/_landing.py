import os
from typing import Optional
from dataclasses import dataclass

from fred.dao.comp.catalog import CompCatalog, FredKeyVal
from fred.ogd.source.catalog import SourceCatalog
from fred.ogd.source.interface import SourceInterface
from fred.ogd.layer.interface import LayerInterface
from fred.ogd.source.model import Snapshot


@dataclass(frozen=True, slots=True)
class LayerLanding(LayerInterface):
    source: SourceInterface
    keyval: FredKeyVal

    @classmethod
    def auto(
            cls,
            source: str,
            backend: str,
            source_kwargs: Optional[dict] = None,
            backend_kwargs: Optional[dict] = None,
    ) -> "LayerLanding":
        source_instance = SourceCatalog[source].auto(**(source_kwargs or {}))
        keyval_instance = CompCatalog.KEYVAL.mount(srv_ref=backend, **(backend_kwargs or {}))
        return cls(source=source_instance, keyval=keyval_instance)
    
    def snapshot(self, **kwargs) -> Snapshot:
        return self.source.snapshot(**kwargs)

    def run(
            self,
            output_path: Optional[str] = None,
            ts_format: Optional[str] = None,
            include_uuid: bool = False,
            snapshot_kwargs: Optional[dict] = None,
            key_setting_kwargs: Optional[dict] = None,
    ) -> bool:
        snapshot = self.snapshot(**(snapshot_kwargs or {}))
        filename = snapshot.filename(ts_format=ts_format, include_uuid=include_uuid)
        content = snapshot.content()
        snapshot_key = self.keyval(key=os.path.join(output_path or "", filename))
        if not snapshot_key.get():
            snapshot_key.set(content, **(key_setting_kwargs or {}))
            return True
        return False
