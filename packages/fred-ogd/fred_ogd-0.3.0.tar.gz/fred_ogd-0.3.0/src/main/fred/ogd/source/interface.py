from fred.ogd.source.model import Snapshot


class SourceInterface:
    
    def snapshot(self, **kwargs) -> Snapshot:
        snapshot_data = self.fetch_snapshot_data(**kwargs)
        return Snapshot.auto(
            data=snapshot_data,
            **kwargs
        )
