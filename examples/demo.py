"""Generate and inspect a synthetic record without executing its logic."""
import argparse
import json
from pathlib import Path
from agent_foundry_blueprint_compiler import compile_blueprint, compile_runtime_package, parse_blueprint

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="New directory for generated files")
    args = parser.parse_args()
    record = json.loads(Path(__file__).with_name("record.json").read_text(encoding="utf-8"))
    blueprint = compile_blueprint(record)
    runtime = compile_runtime_package(blueprint)
    assert runtime["package"]["logic"]["logic_source"] == record["logic"]
    reformatted = compile_runtime_package(blueprint.replace("\n\n", "\n\n\n"))
    assert reformatted["record_sha256"] == runtime["record_sha256"]
    assert reformatted["blueprint_sha256"] != runtime["blueprint_sha256"]
    try:
        parse_blueprint(blueprint.replace("Normalize Text Returns", "Other Returns"))
    except ValueError as error:
        rejection = str(error)
    else:
        raise AssertionError("Mixed package fence accepted")
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=False)
        (args.out / "package.blueprint.txt").write_text(blueprint, encoding="utf-8")
        (args.out / "runtime.json").write_text(json.dumps(runtime, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"name": runtime["package"]["name"], "round_trip": True,
        "mixed_package_rejected": rejection, "formatting_changes_raw_hash_only": True,
        "blueprint_sha256": runtime["blueprint_sha256"], "record_sha256": runtime["record_sha256"],
        "logic_executed": False}, indent=2))

if __name__ == "__main__":
    main()
