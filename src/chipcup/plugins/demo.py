"""Built-in example entry point inside the PEP 420 chipcup.plugins namespace."""


class DemoPlugin:
    api_version = "1"

    @staticmethod
    def handshake() -> dict[str, str]:
        return {"name": "demo", "api_version": "1"}
