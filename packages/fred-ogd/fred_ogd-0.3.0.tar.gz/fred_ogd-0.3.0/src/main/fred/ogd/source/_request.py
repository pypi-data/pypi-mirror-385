from dataclasses import dataclass

import requests

from fred.settings import logger_manager
from fred.ogd.source.interface import SourceInterface

logger = logger_manager.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class SourceRequest(SourceInterface):
    target_url: str

    def request(self, **kwargs) -> requests.Response:
        response = requests.get(self.target_url, **kwargs)
        response.raise_for_status()
        if not response.ok:
            raise requests.HTTPError(f"Request failed with status code {response.status_code}")
        return response

    def fetch_snapshot_data(self, **kwargs) -> dict | str:
        response = self.request(**kwargs)
        try:
            return response.json()
        except requests.JSONDecodeError:
            return response.text
        except Exception as e:
            logger.error(f"An error occurred during fetch: {e}")
            raise e
