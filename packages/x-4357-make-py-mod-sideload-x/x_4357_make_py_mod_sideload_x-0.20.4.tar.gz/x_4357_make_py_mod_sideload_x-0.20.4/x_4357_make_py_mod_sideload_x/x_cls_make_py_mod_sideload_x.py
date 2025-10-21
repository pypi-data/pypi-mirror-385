"""Minimal sideload helper with typed sideload interface."""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import sys
from collections.abc import Mapping, Sequence
from os import PathLike, fspath
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Protocol, cast

from jsonschema import ValidationError

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec


from x_make_common_x.json_contracts import validate_payload

from x_make_py_mod_sideload_x.json_contracts import (
    ERROR_SCHEMA,
    INPUT_SCHEMA,
    OUTPUT_SCHEMA,
)

StrPath = str | PathLike[str]

SCHEMA_VERSION = "x_make_py_mod_sideload_x.run/1.0"


# Legacy-compatible entry point
def _resolve_module_file(base_path: StrPath, module: str) -> str:
    path_str = fspath(base_path)
    if not path_str:
        message = "base_path must be a non-empty string"
        raise ValueError(message)

    base_dir = Path(path_str)
    if not base_dir.exists():
        message = f"base_path does not exist: {base_dir}"
        raise FileNotFoundError(message)

    module_path = Path(module)
    if module_path.is_absolute() and module_path.is_file():
        return module_path.as_posix()

    candidates: list[Path] = []
    if module.endswith(".py"):
        candidates.append(base_dir / module)
    else:
        dotted_parts = module.split(".")
        if len(dotted_parts) > 1:
            *pkg_parts, mod_part = dotted_parts
            candidates.append(base_dir.joinpath(*pkg_parts, f"{mod_part}.py"))
        candidates.append(base_dir / f"{module}.py")
        candidates.append(base_dir / module / "__init__.py")

    for candidate in candidates:
        if candidate.is_file():
            return candidate.as_posix()

    message = (
        f"Cannot resolve module file for module={module} under base_path={base_dir}"
    )
    raise ImportError(message)


def _create_spec(module_file: str) -> ModuleSpec:
    spec = importlib.util.spec_from_file_location(
        f"sideload_{abs(hash(module_file))}",
        module_file,
    )
    if spec is None or spec.loader is None:
        message = f"Failed to create module spec for {module_file}"
        raise ImportError(message)
    return spec


def _load_module(base_path: StrPath, module: str) -> ModuleType:
    module_file = _resolve_module_file(base_path, module)
    spec = _create_spec(module_file)
    module_obj = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        message = f"Loader missing for module spec {spec.name}"
        raise ImportError(message)
    loader.exec_module(module_obj)
    return module_obj


def _get_attribute(module_obj: ModuleType, attr_name: str) -> object:
    if not hasattr(module_obj, attr_name):
        module_file_raw = cast("object | None", getattr(module_obj, "__file__", None))
        if isinstance(module_file_raw, str):
            module_file = module_file_raw
        elif module_file_raw is None:
            module_file = "<unknown>"
        else:
            module_file = str(module_file_raw)
        message = (
            f"{ModuleType.__name__} loaded from "
            f"{module_file} has no attribute {attr_name!r}"
        )
        raise AttributeError(message)

    attr = cast("object", getattr(module_obj, attr_name))
    if inspect.isclass(attr):
        attr_type = cast("type[object]", attr)
        return attr_type()
    return attr


class ModuleLoader(Protocol):
    def load_module(self, base_path: StrPath, module: str) -> ModuleType: ...

    def get_attribute(self, module_obj: ModuleType, attr_name: str) -> object: ...


class DefaultModuleLoader:
    def load_module(self, base_path: StrPath, module: str) -> ModuleType:
        return _load_module(base_path, module)

    def get_attribute(self, module_obj: ModuleType, attr_name: str) -> object:
        return _get_attribute(module_obj, attr_name)


class PyModuleSideload:
    """Utility class that sideloads Python modules safely."""

    def __init__(self, module_loader: ModuleLoader | None = None) -> None:
        self._module_loader: ModuleLoader = module_loader or DefaultModuleLoader()

    def run(
        self, base_path: StrPath, module: str, obj: str | None = None
    ) -> ModuleType | object:
        module_obj = self._module_loader.load_module(base_path, module)
        if obj is None:
            return module_obj
        return self._module_loader.get_attribute(module_obj, obj)


class ModuleSideloadRunner(PyModuleSideload):
    def run(
        self, base_path: StrPath, module: str, obj: str | None = None
    ) -> ModuleType | object:
        """Load a module file under base_path and return module or attribute.

        base_path: directory containing modules or packages
        module: a filename (foo.py), a dotted name (pkg.mod) or a module name
        obj: optional attribute name to return from the module
        """
        return super().run(base_path, module, obj)


def _failure_payload(message: str, *, details: Mapping[str, object] | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"status": "failure", "message": message}
    if details:
        payload["details"] = dict(details)
    try:
        validate_payload(payload, ERROR_SCHEMA)
    except ValidationError:
        pass
    return payload


def _string_or_none(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _ensure_json_mapping(raw: object) -> dict[str, object]:
    if isinstance(raw, Mapping):
        return {str(key): value for key, value in raw.items()}
    return {}


def main_json(payload: Mapping[str, object], *, ctx: object | None = None) -> dict[str, object]:
    del ctx
    try:
        validate_payload(payload, INPUT_SCHEMA)
    except ValidationError as exc:
        return _failure_payload(
            "input payload failed validation",
            details={
                "error": exc.message,
                "path": [str(part) for part in exc.path],
                "schema_path": [str(part) for part in exc.schema_path],
            },
        )

    parameters_obj = payload.get("parameters", {})
    parameters = cast("Mapping[str, object]", parameters_obj)

    base_path_obj = parameters.get("base_path")
    module_obj = parameters.get("module")
    attribute_obj = parameters.get("attribute")
    loader_options_obj = parameters.get("loader_options")

    base_path = _string_or_none(base_path_obj)
    module_name = _string_or_none(module_obj)
    attribute_name = _string_or_none(attribute_obj)
    loader_options = _ensure_json_mapping(loader_options_obj)

    if not base_path:
        return _failure_payload(
            "base_path must be a non-empty string",
            details={"field": "base_path"},
        )
    if not module_name:
        return _failure_payload(
            "module must be a non-empty string",
            details={"field": "module"},
        )

    runner = ModuleSideloadRunner()
    messages: list[str] = []
    metadata: dict[str, object] = {"module_name": module_name}
    if loader_options:
        metadata["loader_options"] = loader_options

    try:
        module_obj_loaded = runner._module_loader.load_module(base_path, module_name)  # type: ignore[attr-defined]
    except (FileNotFoundError, ImportError, ValueError, OSError) as exc:
        return _failure_payload(
            "module resolution failed",
            details={
                "error": str(exc),
                "base_path": base_path,
                "module": module_name,
            },
        )

    module_file_obj = cast("object | None", getattr(module_obj_loaded, "__file__", None))
    module_file = module_file_obj if isinstance(module_file_obj, str) else None
    if module_file is None:
        module_file = _resolve_module_file(base_path, module_name)

    messages.append(f"Loaded {module_name}")

    object_kind = "module"
    attribute_result: object | None = None
    if attribute_name:
        try:
            attribute_result = runner._module_loader.get_attribute(module_obj_loaded, attribute_name)  # type: ignore[attr-defined]
        except AttributeError as exc:
            return _failure_payload(
                "attribute resolution failed",
                details={
                    "error": str(exc),
                    "attribute": attribute_name,
                    "module_file": module_file,
                },
            )
        messages.append(f"Resolved attribute {attribute_name}")
        object_kind = "attribute"
        metadata["attribute_type"] = type(attribute_result).__name__

    result_payload: dict[str, object] = {
        "status": "success",
        "schema_version": SCHEMA_VERSION,
        "module_file": module_file,
        "attribute": attribute_name,
        "object_kind": object_kind,
    }
    if messages:
        result_payload["messages"] = messages
    if metadata:
        result_payload["metadata"] = metadata

    try:
        validate_payload(result_payload, OUTPUT_SCHEMA)
    except ValidationError as exc:
        return _failure_payload(
            "generated output failed schema validation",
            details={
                "error": exc.message,
                "path": [str(part) for part in exc.path],
                "schema_path": [str(part) for part in exc.schema_path],
            },
        )

    return result_payload


def _load_json_payload(file_path: str | None) -> Mapping[str, object]:
    if file_path:
        with Path(file_path).open("r", encoding="utf-8") as handle:
            return cast("Mapping[str, object]", json.load(handle))
    return cast("Mapping[str, object]", json.load(sys.stdin))


def _run_json_cli(args: Sequence[str]) -> None:
    parser = argparse.ArgumentParser(description="x_make_py_mod_sideload_x JSON runner")
    parser.add_argument("--json", action="store_true", help="Read JSON payload from stdin")
    parser.add_argument("--json-file", type=str, help="Path to JSON payload file")
    parsed = parser.parse_args(args)

    if not (parsed.json or parsed.json_file):
        parser.error("JSON input required. Use --json for stdin or --json-file <path>.")

    payload = _load_json_payload(parsed.json_file if parsed.json_file else None)
    result = main_json(payload)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


# Packaging-friendly aliases
x_cls_make_py_mod_sideload_x = ModuleSideloadRunner
xclsmakepymodsideloadx = ModuleSideloadRunner

__all__ = [
    "ModuleSideloadRunner",
    "PyModuleSideload",
    "main_json",
    "x_cls_make_py_mod_sideload_x",
    "xclsmakepymodsideloadx",
]


if __name__ == "__main__":
    _run_json_cli(sys.argv[1:])
