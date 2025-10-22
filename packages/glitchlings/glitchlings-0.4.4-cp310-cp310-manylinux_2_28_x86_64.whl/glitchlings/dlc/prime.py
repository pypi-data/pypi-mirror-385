"""Integration helpers for the optional verifiers prime DLC."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from enum import Enum
from typing import Any, Callable, Protocol, cast

from ..compat import require_datasets, require_jellyfish, require_verifiers
from ..util.adapters import coerce_gaggle
from ..zoo import Gaggle, Glitchling, Mim1c, Typogre
from ._shared import resolve_columns as _resolve_columns_shared
from ._shared import resolve_environment as _resolve_environment_shared


class VerifierEnvironment(Protocol):
    """Minimal interface for verifiers environments."""

    dataset: Any


class VerifierSingleTurnEnv(Protocol):
    """Minimal interface for single-turn verifier environments."""

    dataset: Any
    rubric: Any


vf = require_verifiers("verifiers is not installed; install glitchlings[prime]")
_jellyfish = require_jellyfish("jellyfish is not installed; install glitchlings[prime]")
damerau_levenshtein_distance = _jellyfish.damerau_levenshtein_distance

try:
    from .huggingface import Dataset as _HuggingFaceDataset
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    _HuggingFaceDataset = None
else:
    if _HuggingFaceDataset is None:  # pragma: no cover - optional dependency
        _HuggingFaceDataset = None

Dataset: type[Any]
if _HuggingFaceDataset is None:
    Dataset = object
else:
    Dataset = _HuggingFaceDataset


def _resolve_environment(env: str | VerifierEnvironment) -> VerifierEnvironment:
    """Return a fully-instantiated verifier environment."""
    resolved = _resolve_environment_shared(
        env,
        loader=vf.load_environment,
        environment_type=cast(type[Any], vf.Environment),
    )
    return cast(VerifierEnvironment, resolved)


def _resolve_columns(dataset: Any, columns: Sequence[str] | None) -> list[str]:
    """Identify which dataset columns should be corrupted."""
    return _resolve_columns_shared(dataset, columns)


class Difficulty(Enum):
    """Difficulty levels for tutorial environments."""

    Easy = 0.25
    Normal = 1.0
    Hard = 1.75
    Extreme = 3
    Impossible = 9


def tutorial_level(
    env: VerifierEnvironment | str,
    seed: int = 151,
    difficulty: Difficulty = Difficulty.Normal,
) -> VerifierEnvironment:
    """Create a low-corruption environment using tuned defaults."""
    tuned_mim1c = Mim1c(rate=0.01 * difficulty.value)
    tuned_typogre = Typogre(rate=0.025 * difficulty.value)

    return load_environment(
        env,
        glitchlings=[tuned_mim1c, tuned_typogre],
        seed=seed,
    )


def load_environment(
    env: str | VerifierEnvironment,
    glitchlings: Iterable[str | Glitchling] | Glitchling | str | Gaggle | None = None,
    *,
    seed: int = 151,
    columns: Sequence[str] | None = None,
) -> VerifierEnvironment:
    """Load an environment and optionally corrupt it with glitchlings."""
    environment = _resolve_environment(env)

    if glitchlings is None:
        return environment

    gaggle = coerce_gaggle(glitchlings, seed=seed)

    dataset = environment.dataset
    corrupt_columns = _resolve_columns(dataset, columns)
    environment.dataset = gaggle.corrupt_dataset(dataset, corrupt_columns)
    return environment


def _as_gaggle(
    glitchlings: Iterable[str | Glitchling] | Glitchling | str | Gaggle,
    *,
    seed: int,
) -> Gaggle:
    """Coerce any supported glitchling specification into a :class:`Gaggle`."""
    return coerce_gaggle(glitchlings, seed=seed)


def _extract_completion_text(completion: Any) -> str:
    """Normalise a completion payload into a plain string."""
    if isinstance(completion, str):
        return completion

    if isinstance(completion, list) and completion:
        first = completion[0]
        if isinstance(first, dict) and "content" in first:
            return str(first["content"])
        return str(first)

    return str(completion)


def symmetric_damerau_levenshtein_similarity(
    _: Any,
    completion: Any,
    answer: str,
) -> float:
    """Return ``1 - (distance / max_len)`` using Damerau-Levenshtein distance."""
    completion_text = _extract_completion_text(completion)
    target = answer or ""
    denominator = max(len(completion_text), len(target), 1)
    distance = cast(int, damerau_levenshtein_distance(completion_text, target))
    score = 1.0 - (distance / denominator)
    return max(0.0, min(1.0, score))


DEFAULT_CLEANUP_INSTRUCTIONS = (
    "You are a meticulous copy editor. Restore the provided text to its original form."
)


def echo_chamber(
    dataset_id: str,
    column: str,
    glitchlings: Iterable[str | Glitchling] | Glitchling | str | Gaggle,
    *,
    seed: int = 151,
    instructions: str = DEFAULT_CLEANUP_INSTRUCTIONS,
    reward_function: Callable[..., float] | None = None,
    split: str | None = None,
    **load_dataset_kwargs: Any,
) -> VerifierSingleTurnEnv:
    """Create an Echo Chamber Prime environment from a Hugging Face dataset column.

    Args:
        dataset_id: Identifier of the Hugging Face dataset to load.
        column: Name of the column whose text should be glitched.
        glitchlings: Glitchling specifiers that will corrupt the prompts.
        seed: RNG seed forwarded to :func:`glitchlings.util.adapters.coerce_gaggle`.
        instructions: System instructions supplied to the environment prompts.
        reward_function: Optional callable used to score completions. Defaults to
            :func:`symmetric_damerau_levenshtein_similarity` when omitted.
        split: Optional dataset split to load.
        **load_dataset_kwargs: Extra keyword arguments forwarded to
            :func:`datasets.load_dataset`.

    """
    datasets_module = require_datasets("datasets is required to build an echo chamber")
    load_dataset = getattr(datasets_module, "load_dataset", None)
    if load_dataset is None:  # pragma: no cover - defensive
        message = "datasets is required to build an echo chamber"
        raise ModuleNotFoundError(message)

    dataset_dict_cls = getattr(datasets_module, "DatasetDict", dict)

    hf_dataset: Any
    if split is None:
        hf_dataset = load_dataset(dataset_id, **load_dataset_kwargs)
        if isinstance(hf_dataset, dataset_dict_cls):
            try:
                hf_dataset = next(iter(hf_dataset.values()))
            except StopIteration as exc:  # pragma: no cover - defensive
                raise ValueError("The specified dataset does not contain any splits") from exc
    else:
        hf_dataset = load_dataset(dataset_id, split=split, **load_dataset_kwargs)

    if isinstance(hf_dataset, dataset_dict_cls):
        raise ValueError("Specify which split to use when the dataset loads as a DatasetDict.")

    filtered_dataset = hf_dataset.filter(
        lambda row: row.get(column) is not None,
        load_from_cache_file=False,
    )

    source_column_names = list(filtered_dataset.column_names)

    def _build_prompt(row: dict[str, Any]) -> dict[str, Any]:
        text = str(row[column])
        prompt = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": f"Corrupted text:\n{text}"},
        ]
        return {"prompt": prompt, "answer": text}

    base_dataset = filtered_dataset.map(
        _build_prompt,
        remove_columns=source_column_names,
        load_from_cache_file=False,
    )

    try:
        dataset_length = len(base_dataset)
    except TypeError:
        preview_rows: list[dict[str, Any]]
        take_fn = getattr(base_dataset, "take", None)
        if callable(take_fn):
            preview_rows = list(take_fn(1))
        else:
            iterator = iter(base_dataset)
            try:
                first_row = next(iterator)
            except StopIteration:
                preview_rows = []
            else:
                preview_rows = [first_row]
        if not preview_rows:
            raise ValueError(
                f"Column '{column}' did not yield any textual entries in dataset '{dataset_id}'."
            )
    else:
        if dataset_length == 0:
            raise ValueError(
                f"Column '{column}' did not yield any textual entries in dataset '{dataset_id}'."
            )

    gaggle = _as_gaggle(glitchlings, seed=seed)
    glitched_dataset = gaggle.corrupt_dataset(base_dataset, ["prompt"])

    rubric_func = reward_function or symmetric_damerau_levenshtein_similarity
    rubric = vf.Rubric(funcs=[rubric_func], weights=[1.0])
    return cast(
        VerifierSingleTurnEnv,
        vf.SingleTurnEnv(dataset=glitched_dataset, rubric=rubric),
    )
