import os
import uuid
import json
import datetime as dt
from typing import Optional

from pydantic import BaseModel


class Snapshot(BaseModel):
    data: dict | str
    created_at: str
    metadata: dict

    @classmethod
    def auto(cls, data: dict | str, created_at: Optional[str] = None, metadata: Optional[dict] = None) -> "Snapshot":
        from fred.utils.dateops import datetime_utcnow
        return cls(
            data=data,
            created_at=created_at or datetime_utcnow().isoformat(),
            metadata=metadata or {},
        )

    @property
    def dt_created_at(self) -> dt.datetime:
        return dt.datetime.fromisoformat(self.created_at)

    @property
    def data_uuid(self) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_OID, self.data if isinstance(self.data, str) else json.dumps(self.data, default=str)))

    def filename(self, ts_format: Optional[str] = None, include_uuid: bool = False) -> str:
        ts_format = ts_format or "%Y-%m-%d-%H-%M-%S"
        data_id = f"-{self.data_uuid}" if include_uuid else ""
        return f"snapshot-{self.dt_created_at.strftime(ts_format)}{data_id}.json"

    def content(self) -> str:
        return self.model_dump_json()

    def save(self, path: str, filename: Optional[str] = None, ts_format: Optional[str] = None, include_uuid: bool = False) -> None:
        filename = filename or self.filename(ts_format=ts_format, include_uuid=include_uuid)
        filepath = os.path.join(path, filename)
        with open(filepath, "w") as file:
            file.write(self.content())
