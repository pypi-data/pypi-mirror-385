from fred.cli.interface import AbstractCLI


class OGDCLI(AbstractCLI):

    def version(self):
        from fred.ogd.version import version
        return version

    def execute(self, name: str):
        import importlib

        module = importlib.import_module(f"fred.ogd.{name}.cli")
        with module.OGDExtCLI.default_config() as cli:
            return cli
