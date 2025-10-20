from __future__ import annotations

import ast
from typing import Any

from .adjax import Adjax, adjax
from .apostrofae import Apostrofae, apostrofae
from .core import (
    Gaggle,
    Glitchling,
    is_rust_pipeline_enabled,
    is_rust_pipeline_supported,
    pipeline_feature_flag_enabled,
    plan_glitchling_specs,
    plan_glitchlings,
)
from .jargoyle import Jargoyle, jargoyle
from .jargoyle import dependencies_available as _jargoyle_available
from .mim1c import Mim1c, mim1c
from .redactyl import Redactyl, redactyl
from .reduple import Reduple, reduple
from .rushmore import Rushmore, rushmore
from .scannequin import Scannequin, scannequin
from .typogre import Typogre, typogre
from .zeedub import Zeedub, zeedub

__all__ = [
    "Typogre",
    "typogre",
    "Mim1c",
    "mim1c",
    "Jargoyle",
    "jargoyle",
    "Apostrofae",
    "apostrofae",
    "Adjax",
    "adjax",
    "Reduple",
    "reduple",
    "Rushmore",
    "rushmore",
    "Redactyl",
    "redactyl",
    "Scannequin",
    "scannequin",
    "Zeedub",
    "zeedub",
    "Glitchling",
    "Gaggle",
    "plan_glitchlings",
    "plan_glitchling_specs",
    "is_rust_pipeline_enabled",
    "is_rust_pipeline_supported",
    "pipeline_feature_flag_enabled",
    "summon",
    "BUILTIN_GLITCHLINGS",
    "DEFAULT_GLITCHLING_NAMES",
    "parse_glitchling_spec",
    "get_glitchling_class",
]

_HAS_JARGOYLE = _jargoyle_available()

_BUILTIN_GLITCHLING_LIST: list[Glitchling] = [typogre, apostrofae, mim1c]
if _HAS_JARGOYLE:
    _BUILTIN_GLITCHLING_LIST.append(jargoyle)
_BUILTIN_GLITCHLING_LIST.extend([adjax, reduple, rushmore, redactyl, scannequin, zeedub])

BUILTIN_GLITCHLINGS: dict[str, Glitchling] = {
    glitchling.name.lower(): glitchling for glitchling in _BUILTIN_GLITCHLING_LIST
}

_BUILTIN_GLITCHLING_TYPES: dict[str, type[Glitchling]] = {
    typogre.name.lower(): Typogre,
    apostrofae.name.lower(): Apostrofae,
    mim1c.name.lower(): Mim1c,
    adjax.name.lower(): Adjax,
    reduple.name.lower(): Reduple,
    rushmore.name.lower(): Rushmore,
    redactyl.name.lower(): Redactyl,
    scannequin.name.lower(): Scannequin,
    zeedub.name.lower(): Zeedub,
}
if _HAS_JARGOYLE:
    _BUILTIN_GLITCHLING_TYPES[jargoyle.name.lower()] = Jargoyle

DEFAULT_GLITCHLING_NAMES: list[str] = list(BUILTIN_GLITCHLINGS.keys())


def parse_glitchling_spec(specification: str) -> Glitchling:
    """Return a glitchling instance configured according to ``specification``."""
    text = specification.strip()
    if not text:
        raise ValueError("Glitchling specification cannot be empty.")

    if "(" not in text:
        glitchling = BUILTIN_GLITCHLINGS.get(text.lower())
        if glitchling is None:
            raise ValueError(f"Glitchling '{text}' not found.")
        return glitchling

    if not text.endswith(")"):
        raise ValueError(f"Invalid parameter syntax for glitchling '{text}'.")

    name_part, arg_source = text[:-1].split("(", 1)
    name = name_part.strip()
    if not name:
        raise ValueError(f"Invalid glitchling specification '{text}'.")

    lower_name = name.lower()
    glitchling_type = _BUILTIN_GLITCHLING_TYPES.get(lower_name)
    if glitchling_type is None:
        raise ValueError(f"Glitchling '{name}' not found.")

    try:
        call_expr = ast.parse(f"_({arg_source})", mode="eval").body
    except SyntaxError as exc:
        raise ValueError(f"Invalid parameter syntax for glitchling '{name}': {exc.msg}") from exc

    if not isinstance(call_expr, ast.Call) or call_expr.args:
        raise ValueError(f"Glitchling '{name}' parameters must be provided as keyword arguments.")

    kwargs: dict[str, Any] = {}
    for keyword in call_expr.keywords:
        if keyword.arg is None:
            raise ValueError(
                f"Glitchling '{name}' does not support unpacking arbitrary keyword arguments."
            )
        try:
            kwargs[keyword.arg] = ast.literal_eval(keyword.value)
        except (ValueError, SyntaxError) as exc:
            raise ValueError(
                f"Failed to parse value for parameter '{keyword.arg}' on glitchling '{name}': {exc}"
            ) from exc

    try:
        return glitchling_type(**kwargs)
    except TypeError as exc:
        raise ValueError(f"Failed to instantiate glitchling '{name}': {exc}") from exc


def get_glitchling_class(name: str) -> type[Glitchling]:
    """Look up the glitchling class registered under ``name``."""
    key = name.strip().lower()
    if not key:
        raise ValueError("Glitchling name cannot be empty.")

    glitchling_type = _BUILTIN_GLITCHLING_TYPES.get(key)
    if glitchling_type is None:
        raise ValueError(f"Glitchling '{name}' not found.")

    return glitchling_type


def summon(glitchlings: list[str | Glitchling], seed: int = 151) -> Gaggle:
    """Summon glitchlings by name (using defaults) or instance (to change parameters)."""
    summoned: list[Glitchling] = []
    for entry in glitchlings:
        if isinstance(entry, Glitchling):
            summoned.append(entry)
            continue

        try:
            summoned.append(parse_glitchling_spec(entry))
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

    return Gaggle(summoned, seed=seed)
