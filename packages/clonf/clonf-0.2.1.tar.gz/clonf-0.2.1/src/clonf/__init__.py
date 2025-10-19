from .annotations import CliArgument, CliOption
import typing as t
import importlib

if t.TYPE_CHECKING:
    from clonf.integrations.click.types import TClonfClick

    clonf_click: TClonfClick


_dynamic_imports: dict[str, str] = {"clonf_click": "clonf.integrations.click"}


def __getattr__(name: str) -> t.Any:
    if name in _dynamic_imports:
        return getattr(importlib.import_module(_dynamic_imports[name]), name)

    raise AttributeError(  # pragma: no cover
        f"module {__name__!r} has no attribute {name!r}"
    )


__all__ = ["CliArgument", "CliOption", "_dynamic_imports", "clonf_click"]
