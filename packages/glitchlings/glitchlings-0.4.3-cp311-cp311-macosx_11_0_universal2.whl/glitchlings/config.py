"""Configuration utilities for runtime behaviour and declarative attack setups."""

from __future__ import annotations

import importlib
import os
import warnings
from dataclasses import dataclass, field
from io import TextIOBase
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Mapping, Protocol, Sequence, cast

from glitchlings.compat import jsonschema

try:  # Python 3.11+
    import tomllib as _tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    _tomllib = importlib.import_module("tomli")


class _TomllibModule(Protocol):
    def load(self, fp: IO[bytes]) -> Any:
        ...


tomllib = cast(_TomllibModule, _tomllib)


class _YamlModule(Protocol):
    YAMLError: type[Exception]

    def safe_load(self, stream: str) -> Any:
        ...


yaml = cast(_YamlModule, importlib.import_module("yaml"))

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .zoo import Gaggle, Glitchling


CONFIG_ENV_VAR = "GLITCHLINGS_CONFIG"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.toml")
DEFAULT_LEXICON_PRIORITY = ["vector", "wordnet"]
DEFAULT_ATTACK_SEED = 151

ATTACK_CONFIG_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["glitchlings"],
    "properties": {
        "glitchlings": {
            "type": "array",
            "minItems": 1,
            "items": {
                "anyOf": [
                    {"type": "string", "minLength": 1},
                    {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "type": {"type": "string", "minLength": 1},
                            "parameters": {"type": "object"},
                        },
                        "additionalProperties": True,
                    },
                    {
                        "type": "object",
                        "required": ["type"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "type": {"type": "string", "minLength": 1},
                            "parameters": {"type": "object"},
                        },
                        "additionalProperties": True,
                    },
                ]
            },
        },
        "seed": {"type": "integer"},
    },
    "additionalProperties": False,
}


@dataclass(slots=True)
class LexiconConfig:
    """Lexicon-specific configuration section."""

    priority: list[str] = field(default_factory=lambda: list(DEFAULT_LEXICON_PRIORITY))
    vector_cache: Path | None = None


@dataclass(slots=True)
class RuntimeConfig:
    """Top-level runtime configuration loaded from ``config.toml``."""

    lexicon: LexiconConfig
    path: Path


_CONFIG: RuntimeConfig | None = None


def reset_config() -> None:
    """Forget any cached runtime configuration."""
    global _CONFIG
    _CONFIG = None


def reload_config() -> RuntimeConfig:
    """Reload the runtime configuration from disk."""
    reset_config()
    return get_config()


def get_config() -> RuntimeConfig:
    """Return the cached runtime configuration, loading it if necessary."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _load_runtime_config()
    return _CONFIG


def _load_runtime_config() -> RuntimeConfig:
    path = _resolve_config_path()
    data = _read_toml(path)
    mapping = _validate_runtime_config_data(data, source=path)

    lexicon_section = mapping.get("lexicon", {})

    priority = lexicon_section.get("priority", DEFAULT_LEXICON_PRIORITY)
    if not isinstance(priority, Sequence) or isinstance(priority, (str, bytes)):
        raise ValueError("lexicon.priority must be a sequence of strings.")
    normalized_priority = []
    for item in priority:
        string_value = str(item)
        if not string_value:
            raise ValueError("lexicon.priority entries must be non-empty strings.")
        normalized_priority.append(string_value)

    vector_cache = _resolve_optional_path(
        lexicon_section.get("vector_cache"),
        base=path.parent,
    )
    lexicon_config = LexiconConfig(
        priority=normalized_priority,
        vector_cache=vector_cache,
    )

    return RuntimeConfig(lexicon=lexicon_config, path=path)


def _resolve_config_path() -> Path:
    override = os.environ.get(CONFIG_ENV_VAR)
    if override:
        return Path(override)
    return DEFAULT_CONFIG_PATH


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        if path == DEFAULT_CONFIG_PATH:
            return {}
        raise FileNotFoundError(f"Configuration file '{path}' not found.")
    with path.open("rb") as handle:
        loaded = tomllib.load(handle)
    if isinstance(loaded, Mapping):
        return dict(loaded)
    raise ValueError(f"Configuration file '{path}' must contain a top-level mapping.")


def _validate_runtime_config_data(data: Any, *, source: Path) -> Mapping[str, Any]:
    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise ValueError(f"Configuration file '{source}' must contain a top-level mapping.")

    allowed_sections = {"lexicon"}
    unexpected_sections = [str(key) for key in data if key not in allowed_sections]
    if unexpected_sections:
        extras = ", ".join(sorted(unexpected_sections))
        raise ValueError(f"Configuration file '{source}' has unsupported sections: {extras}.")

    lexicon_section = data.get("lexicon", {})
    if not isinstance(lexicon_section, Mapping):
        raise ValueError("Configuration 'lexicon' section must be a table.")

    allowed_lexicon_keys = {"priority", "vector_cache"}
    unexpected_keys = [str(key) for key in lexicon_section if key not in allowed_lexicon_keys]
    if unexpected_keys:
        extras = ", ".join(sorted(unexpected_keys))
        raise ValueError(f"Unknown lexicon settings: {extras}.")

    for key in ("vector_cache",):
        value = lexicon_section.get(key)
        if value is not None and not isinstance(value, (str, os.PathLike)):
            raise ValueError(f"lexicon.{key} must be a path or string when provided.")

    return data


def _resolve_optional_path(value: Any, *, base: Path) -> Path | None:
    if value in (None, ""):
        return None

    candidate = Path(str(value))
    if not candidate.is_absolute():
        candidate = (base / candidate).resolve()
    return candidate


@dataclass(slots=True)
class AttackConfig:
    """Structured representation of a glitchling roster loaded from YAML."""

    glitchlings: list["Glitchling"]
    seed: int | None = None


def load_attack_config(
    source: str | Path | TextIOBase,
    *,
    encoding: str = "utf-8",
) -> AttackConfig:
    """Load and parse an attack configuration from YAML."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        label = str(path)
        try:
            text = path.read_text(encoding=encoding)
        except FileNotFoundError as exc:
            raise ValueError(f"Attack configuration '{label}' was not found.") from exc
    elif isinstance(source, TextIOBase):
        label = getattr(source, "name", "<stream>")
        text = source.read()
    else:
        raise TypeError("Attack configuration source must be a path or text stream.")

    data = _load_yaml(text, label)
    return parse_attack_config(data, source=label)


def _validate_attack_config_schema(data: Any, *, source: str) -> Mapping[str, Any]:
    if data is None:
        raise ValueError(f"Attack configuration '{source}' is empty.")
    if not isinstance(data, Mapping):
        raise ValueError(f"Attack configuration '{source}' must be a mapping.")

    unexpected = [key for key in data if key not in {"glitchlings", "seed"}]
    if unexpected:
        extras = ", ".join(sorted(unexpected))
        raise ValueError(f"Attack configuration '{source}' has unsupported fields: {extras}.")

    if "glitchlings" not in data:
        raise ValueError(f"Attack configuration '{source}' must define 'glitchlings'.")

    raw_glitchlings = data["glitchlings"]
    if not isinstance(raw_glitchlings, Sequence) or isinstance(raw_glitchlings, (str, bytes)):
        raise ValueError(f"'glitchlings' in '{source}' must be a sequence.")

    seed = data.get("seed")
    if seed is not None and not isinstance(seed, int):
        raise ValueError(f"Seed in '{source}' must be an integer if provided.")

    for index, entry in enumerate(raw_glitchlings, start=1):
        if isinstance(entry, Mapping):
            name_candidate = entry.get("name") or entry.get("type")
            if not isinstance(name_candidate, str) or not name_candidate.strip():
                raise ValueError(f"{source}: glitchling #{index} is missing a 'name'.")
            parameters = entry.get("parameters")
            if parameters is not None and not isinstance(parameters, Mapping):
                raise ValueError(
                    f"{source}: glitchling '{name_candidate}' parameters must be a mapping."
                )

    schema_module = jsonschema.get()
    if schema_module is not None:
        try:
            schema_module.validate(instance=data, schema=ATTACK_CONFIG_SCHEMA)
        except schema_module.exceptions.ValidationError as exc:  # pragma: no cover - optional dep
            message = exc.message
            raise ValueError(f"Attack configuration '{source}' is invalid: {message}") from exc

    return data


def parse_attack_config(data: Any, *, source: str = "<config>") -> AttackConfig:
    """Convert arbitrary YAML data into a validated ``AttackConfig``."""
    mapping = _validate_attack_config_schema(data, source=source)

    raw_glitchlings = mapping["glitchlings"]

    glitchlings: list["Glitchling"] = []
    for index, entry in enumerate(raw_glitchlings, start=1):
        glitchlings.append(_build_glitchling(entry, source, index))

    seed = mapping.get("seed")

    return AttackConfig(glitchlings=glitchlings, seed=seed)


def build_gaggle(config: AttackConfig, *, seed_override: int | None = None) -> "Gaggle":
    """Instantiate a ``Gaggle`` according to ``config``."""
    from .zoo import Gaggle  # Imported lazily to avoid circular dependencies

    seed = seed_override if seed_override is not None else config.seed
    if seed is None:
        seed = DEFAULT_ATTACK_SEED

    return Gaggle(config.glitchlings, seed=seed)


def _load_yaml(text: str, label: str) -> Any:
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse attack configuration '{label}': {exc}") from exc


def _build_glitchling(entry: Any, source: str, index: int) -> "Glitchling":
    from .zoo import get_glitchling_class, parse_glitchling_spec

    if isinstance(entry, str):
        try:
            return parse_glitchling_spec(entry)
        except ValueError as exc:
            raise ValueError(f"{source}: glitchling #{index}: {exc}") from exc

    if isinstance(entry, Mapping):
        name_value = entry.get("name")
        legacy_type = entry.get("type")
        if name_value is None and legacy_type is not None:
            warnings.warn(
                f"{source}: glitchling #{index} uses 'type'; prefer 'name'.",
                DeprecationWarning,
                stacklevel=2,
            )
            name_value = legacy_type
        elif name_value is None:
            name_value = legacy_type

        if not isinstance(name_value, str) or not name_value.strip():
            raise ValueError(f"{source}: glitchling #{index} is missing a 'name'.")

        parameters = entry.get("parameters")
        if parameters is not None:
            if not isinstance(parameters, Mapping):
                raise ValueError(
                    f"{source}: glitchling '{name_value}' parameters must be a mapping."
                )
            kwargs = dict(parameters)
        else:
            kwargs = {
                key: value
                for key, value in entry.items()
                if key not in {"name", "type", "parameters"}
            }

        try:
            glitchling_type = get_glitchling_class(name_value)
        except ValueError as exc:
            raise ValueError(f"{source}: glitchling #{index}: {exc}") from exc

        try:
            return glitchling_type(**kwargs)
        except TypeError as exc:
            raise ValueError(
                f"{source}: glitchling #{index}: failed to instantiate '{name_value}': {exc}"
            ) from exc

    raise ValueError(f"{source}: glitchling #{index} must be a string or mapping.")


__all__ = [
    "AttackConfig",
    "DEFAULT_ATTACK_SEED",
    "DEFAULT_CONFIG_PATH",
    "DEFAULT_LEXICON_PRIORITY",
    "RuntimeConfig",
    "LexiconConfig",
    "build_gaggle",
    "get_config",
    "load_attack_config",
    "parse_attack_config",
    "reload_config",
    "reset_config",
]
