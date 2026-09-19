from __future__ import annotations

import hashlib
import json
import re
from typing import Any


SECTIONS = (
    "Package ID",
    "Required Replacements",
    "Optional Replacements",
    "Logic",
    "Arguments",
    "Returns",
    "Recognitions",
)
LIST_SECTIONS = set(SECTIONS) - {"Package ID", "Logic"}
SAFE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_ ]{0,127}$")


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _name(record: dict[str, Any]) -> str:
    name = str(record.get("name") or "").strip()
    if not SAFE_NAME.fullmatch(name):
        raise ValueError("Package name must be 1-128 safe letters, numbers, spaces, or underscores")
    return name


def _list(record: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = record.get(key, [])
    if value in (None, ""):
        return []
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{key} must be a list of objects")
    return value


def _logic(record: dict[str, Any]) -> str:
    value = record.get("logic", "")
    if isinstance(value, dict):
        value = value.get("logic_source", "")
    if not isinstance(value, str):
        raise ValueError("logic must be text or an object with logic_source")
    if not value.strip():
        raise ValueError("logic source is required")
    return value.replace("\r\n", "\n").replace("\r", "\n").rstrip()


def _block(heading: str, value: Any) -> str:
    return f"{heading}:\n{_canonical(value)}\nEnd {heading}"


def compile_blueprint(record: dict[str, Any]) -> str:
    if not isinstance(record, dict):
        raise ValueError("Package record must be an object")
    name = _name(record)
    values: dict[str, Any] = {
        "Package ID": name,
        "Required Replacements": _list(record, "required_replacements"),
        "Optional Replacements": _list(record, "optional_replacements"),
        "Logic": _logic(record),
        "Arguments": _list(record, "arguments"),
        "Returns": _list(record, "returns"),
        "Recognitions": _list(record, "recognitions"),
    }
    return "\n\n".join(_block(f"{name} {section}", values[section]) for section in SECTIONS) + "\n"


def _parse_blocks(text: str) -> list[tuple[str, Any]]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    blocks: list[tuple[str, Any]] = []
    index = 0
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        heading_line = lines[index]
        if not heading_line.endswith(":"):
            raise ValueError(f"Expected block heading at line {index + 1}")
        heading = heading_line[:-1]
        end = f"End {heading}"
        body: list[str] = []
        index += 1
        while index < len(lines) and lines[index] != end:
            body.append(lines[index])
            index += 1
        if index >= len(lines):
            raise ValueError(f"Unterminated block: {heading}")
        try:
            value = json.loads("\n".join(body))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON body in block {heading}: {exc}") from exc
        blocks.append((heading, value))
        index += 1
    return blocks


def parse_blueprint(text: str) -> dict[str, Any]:
    blocks = _parse_blocks(text)
    if len(blocks) != len(SECTIONS):
        raise ValueError(f"Blueprint must contain exactly {len(SECTIONS)} blocks")
    first_heading, name_value = blocks[0]
    name = str(name_value or "").strip()
    if first_heading != f"{name} Package ID":
        raise ValueError("Package ID heading and value disagree")
    seen: set[str] = set()
    values: dict[str, Any] = {}
    for heading, value in blocks:
        prefix = f"{name} "
        if not heading.startswith(prefix):
            raise ValueError("All blocks must belong to the same package")
        section = heading[len(prefix):]
        if section not in SECTIONS or section in seen:
            raise ValueError(f"Unknown or duplicate section: {section}")
        seen.add(section)
        values[section] = value
    if tuple(section for section in SECTIONS if section in seen) != SECTIONS:
        raise ValueError("Blueprint sections are incomplete")
    record = {
        "name": name,
        "required_replacements": values["Required Replacements"],
        "optional_replacements": values["Optional Replacements"],
        "logic": {"logic_source": values["Logic"]},
        "arguments": values["Arguments"],
        "returns": values["Returns"],
        "recognitions": values["Recognitions"],
    }
    _name(record)
    for key in ("required_replacements", "optional_replacements", "arguments", "returns", "recognitions"):
        _list(record, key)
    _logic(record)
    return record


def compile_runtime_package(text: str) -> dict[str, Any]:
    record = parse_blueprint(text)
    canonical = _canonical(record)
    return {
        "schema_version": "agent-foundry.runtime-package.v1",
        "package": record,
        "blueprint_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "record_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
