import os

from fred.version import Version


version = Version.from_path(name="fred-ogd", dirpath=os.path.dirname(__file__))
