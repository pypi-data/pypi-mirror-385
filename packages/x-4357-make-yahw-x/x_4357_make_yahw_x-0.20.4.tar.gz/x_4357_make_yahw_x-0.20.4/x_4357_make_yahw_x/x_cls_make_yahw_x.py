from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import cast

from jsonschema import ValidationError
from x_make_common_x.json_contracts import validate_payload

from x_make_yahw_x.json_contracts import ERROR_SCHEMA, INPUT_SCHEMA, OUTPUT_SCHEMA


class XClsMakeYahwX:
    def __init__(self, ctx: object | None = None) -> None:
        # store optional orchestrator context for backward-compatible upgrades
        self._ctx = ctx

    def run(self) -> str:
        return "Hello world!"


def main() -> str:
    return XClsMakeYahwX().run()


SCHEMA_VERSION = "x_make_yahw_x.run/1.0"


def _failure_payload(message: str, *, details: Mapping[str, object] | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"status": "failure", "message": message}
    if details:
        payload["details"] = dict(details)
    try:
        validate_payload(payload, ERROR_SCHEMA)
    except ValidationError:
        pass
    return payload


def _build_context(ctx: object | None, overrides: Mapping[str, object] | None) -> object | None:
    if not overrides:
        return ctx
    namespace = SimpleNamespace(**{str(key): value for key, value in overrides.items()})
    if ctx is not None:
        namespace._parent_ctx = ctx
    return namespace


def main_json(payload: Mapping[str, object], *, ctx: object | None = None) -> dict[str, object]:
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
    context_obj = parameters.get("context")
    context_mapping = cast("Mapping[str, object] | None", context_obj if isinstance(context_obj, Mapping) else None)

    runtime_ctx = _build_context(ctx, context_mapping)

    try:
        runner = XClsMakeYahwX(ctx=runtime_ctx)
        message = runner.run()
    except Exception as exc:  # noqa: BLE001
        return _failure_payload(
            "yahw execution failed",
            details={"error": str(exc)},
        )

    if not isinstance(message, str) or not message.strip():
        return _failure_payload(
            "yahw returned an empty message",
            details={"result": message},
        )

    metadata: dict[str, object] = {}
    if context_mapping:
        metadata["context_keys"] = sorted(str(key) for key in context_mapping.keys())
        metadata["context_entries"] = len(metadata["context_keys"])
    if runtime_ctx is not ctx and runtime_ctx is not None and ctx is not None:
        metadata["parent_ctx_attached"] = True

    result_payload: dict[str, object] = {
        "status": "success",
        "schema_version": SCHEMA_VERSION,
        "message": message,
    }
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
    parser = argparse.ArgumentParser(description="x_make_yahw_x JSON runner")
    parser.add_argument("--json", action="store_true", help="Read JSON payload from stdin")
    parser.add_argument("--json-file", type=str, help="Path to JSON payload file")
    parsed = parser.parse_args(args)

    if not (parsed.json or parsed.json_file):
        parser.error("JSON input required. Use --json for stdin or --json-file <path>.")

    payload = _load_json_payload(parsed.json_file if parsed.json_file else None)
    result = main_json(payload)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


x_cls_make_yahw_x = XClsMakeYahwX

__all__ = ["XClsMakeYahwX", "main", "main_json", "x_cls_make_yahw_x"]


if __name__ == "__main__":
    _run_json_cli(sys.argv[1:])
