"""Compatibility helpers centralising optional dependency imports and extras."""

from __future__ import annotations

import re
from dataclasses import dataclass
from importlib import import_module, metadata
from types import ModuleType
from typing import Any, Callable, Iterable, Protocol, cast


class _MissingSentinel:
    __slots__ = ()


_MISSING = _MissingSentinel()


class _MarkerProtocol(Protocol):
    def evaluate(self, environment: dict[str, str]) -> bool:
        ...


class _RequirementProtocol(Protocol):
    marker: _MarkerProtocol | None
    name: str

    def __init__(self, requirement: str) -> None:
        ...


try:  # pragma: no cover - packaging is bundled with modern Python environments
    from packaging.markers import default_environment as _default_environment
except ModuleNotFoundError:  # pragma: no cover - fallback when packaging missing
    _default_environment = None

try:  # pragma: no cover - packaging is bundled with modern Python environments
    from packaging.requirements import Requirement as _RequirementClass
except ModuleNotFoundError:  # pragma: no cover - fallback when packaging missing
    _RequirementClass = None

default_environment: Callable[[], dict[str, str]] | None
if _default_environment is None:
    default_environment = None
else:
    default_environment = cast(Callable[[], dict[str, str]], _default_environment)

Requirement: type[_RequirementProtocol] | None
if _RequirementClass is None:
    Requirement = None
else:
    Requirement = cast(type[_RequirementProtocol], _RequirementClass)


@dataclass
class OptionalDependency:
    """Lazily import an optional dependency and retain the import error."""

    module_name: str
    _cached: ModuleType | None | _MissingSentinel = _MISSING
    _error: ModuleNotFoundError | None = None

    def _attempt_import(self) -> ModuleType | None:
        try:
            module = import_module(self.module_name)
        except ModuleNotFoundError as exc:
            self._cached = None
            self._error = exc
            return None
        else:
            self._cached = module
            self._error = None
            return module

    def get(self) -> ModuleType | None:
        """Return the imported module or ``None`` when unavailable."""
        cached = self._cached
        if isinstance(cached, _MissingSentinel):
            return self._attempt_import()
        if cached is None:
            return None
        return cached

    def load(self) -> ModuleType:
        """Return the dependency, raising the original import error when absent."""
        module = self.get()
        if module is None:
            error = self._error
            if error is not None:
                raise error
            message = f"{self.module_name} is not installed"
            raise ModuleNotFoundError(message)
        return module

    def require(self, message: str) -> ModuleType:
        """Return the dependency or raise ``ModuleNotFoundError`` with ``message``."""
        try:
            return self.load()
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(message) from exc

    def available(self) -> bool:
        """Return ``True`` when the dependency can be imported."""
        return self.get() is not None

    def reset(self) -> None:
        """Forget any cached import result."""
        self._cached = _MISSING
        self._error = None

    def attr(self, attribute: str) -> Any | None:
        """Return ``attribute`` from the dependency when available."""
        module = self.get()
        if module is None:
            return None
        return getattr(module, attribute, None)

    @property
    def error(self) -> ModuleNotFoundError | None:
        """Return the most recent ``ModuleNotFoundError`` (if any)."""
        self.get()
        return self._error


pytorch_lightning = OptionalDependency("pytorch_lightning")
datasets = OptionalDependency("datasets")
verifiers = OptionalDependency("verifiers")
jellyfish = OptionalDependency("jellyfish")
jsonschema = OptionalDependency("jsonschema")
nltk = OptionalDependency("nltk")
torch = OptionalDependency("torch")


def reset_optional_dependencies() -> None:
    """Clear cached optional dependency imports (used by tests)."""
    for dependency in (pytorch_lightning, datasets, verifiers, jellyfish, jsonschema, nltk, torch):
        dependency.reset()


def get_datasets_dataset() -> Any | None:
    """Return Hugging Face ``Dataset`` class when the dependency is installed."""
    return datasets.attr("Dataset")


def require_datasets(message: str = "datasets is not installed") -> ModuleType:
    """Ensure the Hugging Face datasets dependency is present."""
    return datasets.require(message)


def get_pytorch_lightning_datamodule() -> Any | None:
    """Return the PyTorch Lightning ``LightningDataModule`` when available."""
    return pytorch_lightning.attr("LightningDataModule")


def require_pytorch_lightning(message: str = "pytorch_lightning is not installed") -> ModuleType:
    """Ensure the PyTorch Lightning dependency is present."""
    return pytorch_lightning.require(message)


def require_verifiers(message: str = "verifiers is not installed") -> ModuleType:
    """Ensure the verifiers dependency is present."""
    return verifiers.require(message)


def require_jellyfish(message: str = "jellyfish is not installed") -> ModuleType:
    """Ensure the jellyfish dependency is present."""
    return jellyfish.require(message)


def require_torch(message: str = "torch is not installed") -> ModuleType:
    """Ensure the PyTorch dependency is present."""
    return torch.require(message)


def get_torch_dataloader() -> Any | None:
    """Return PyTorch ``DataLoader`` when the dependency is installed."""
    torch_module = torch.get()
    if torch_module is None:
        return None

    utils_module = getattr(torch_module, "utils", None)
    if utils_module is None:
        return None

    data_module = getattr(utils_module, "data", None)
    if data_module is None:
        return None

    return getattr(data_module, "DataLoader", None)


def get_installed_extras(
    extras: Iterable[str] | None = None,
    *,
    distribution: str = "glitchlings",
) -> dict[str, bool]:
    """Return a mapping of optional extras to installation availability."""
    try:
        dist = metadata.distribution(distribution)
    except metadata.PackageNotFoundError:
        return {}

    provided = {extra.lower() for extra in dist.metadata.get_all("Provides-Extra") or []}
    targets = {extra.lower() for extra in extras} if extras is not None else provided
    requirements = dist.requires or []
    mapping: dict[str, set[str]] = {extra: set() for extra in provided}

    for requirement in requirements:
        names = _extras_from_requirement(requirement, provided)
        if not names:
            continue
        req_name = _requirement_name(requirement)
        for extra in names:
            mapping.setdefault(extra, set()).add(req_name)

    status: dict[str, bool] = {}
    for extra in targets:
        deps = mapping.get(extra)
        if not deps:
            status[extra] = False
            continue
        status[extra] = all(_distribution_installed(dep) for dep in deps)
    return status


def _distribution_installed(name: str) -> bool:
    try:
        metadata.distribution(name)
    except metadata.PackageNotFoundError:
        return False
    return True


_EXTRA_PATTERN = re.compile(r'extra\\s*==\\s*"(?P<extra>[^"]+)"')


def _extras_from_requirement(requirement: str, candidates: set[str]) -> set[str]:
    if Requirement is not None and default_environment is not None:
        req = Requirement(requirement)
        if req.marker is None:
            return set()
        extras: set[str] = set()
        for extra in candidates:
            environment = default_environment()
            environment["extra"] = extra
            if req.marker.evaluate(environment):
                extras.add(extra)
        return extras

    matches = set()
    for match in _EXTRA_PATTERN.finditer(requirement):
        extra = match.group("extra").lower()
        if extra in candidates:
            matches.add(extra)
    return matches


def _requirement_name(requirement: str) -> str:
    if Requirement is not None:
        req = Requirement(requirement)
        return req.name

    candidate = requirement.split(";", 1)[0].strip()
    for delimiter in ("[", "(", " ", "<", ">", "=", "!", "~"):
        index = candidate.find(delimiter)
        if index != -1:
            return candidate[:index]
    return candidate


__all__ = [
    "OptionalDependency",
    "datasets",
    "verifiers",
    "jellyfish",
    "jsonschema",
    "nltk",
    "get_datasets_dataset",
    "require_datasets",
    "require_verifiers",
    "require_jellyfish",
    "get_installed_extras",
    "reset_optional_dependencies",
]
