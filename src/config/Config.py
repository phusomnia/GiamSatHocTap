import yaml

class Config:
    def __init__(self, data=None):
        self._config = data or {}

    def load_env_yaml(self, path: str = "src/config/app-config.yaml"):
        with open(path, "r") as f:
            self._config = yaml.safe_load(f) or {}
        return self

    def load_prompts(self, path: str = "src/config/prompts/generation-prompts.yaml"):
        with open(path, "r") as f:
            self._config = yaml.safe_load(f) or {}
        return self

    def __getattr__(self, name):
        try:
            value = self._config[name]
        except KeyError:
            raise AttributeError(f"No such config key: {name}")

        if isinstance(value, dict):
            return Config(value)

        return value

    def __repr__(self):
        return f"Config({self._config})"