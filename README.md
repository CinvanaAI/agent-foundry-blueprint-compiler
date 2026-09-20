# Agent Foundry Blueprint Compiler

Turn one capability record into a readable seven-section blueprint, then parse it back into a runtime package record. The useful boundary is **reviewable text ↔ structured data**: Python logic remains text throughout.

This grew out of the Python Agent Foundry importer. This public compiler uses strict JSON inside named fences; it is a clean continuation, not a drop-in parser for every old editor export. [Origin](ORIGIN.md)

## Follow one record through

Python 3.11 or later, from this checkout:

```sh
python -m pip install -e .
python -m examples.demo
python -m examples.demo --out ./blueprint-output
python -m unittest discover -s tests -v
```

The optional output directory must be new. The example never executes the embedded logic.

1. [record.json](examples/record.json) describes “Normalize Text,” its argument and return value.
2. [package.blueprint.txt](examples/package.blueprint.txt) shows the exact seven generated fences.
3. [runtime.json](examples/runtime.json) contains the parsed package plus two hashes.
4. [captured-result.json](examples/captured-result.json) records the round-trip and rejected cross-package fence.

Open the files beside each other. The logic survives the round-trip; its field is normalized to `{"logic_source": ...}`. These artifacts come from [demo.py](examples/demo.py) using synthetic input.

## Use it in another tool

```python
from agent_foundry_blueprint_compiler import compile_blueprint, compile_runtime_package
record = {"name": "Greeting", "logic": "def greet():\n    return 'hello'"}
runtime = compile_runtime_package(compile_blueprint(record))
assert runtime["package"]["name"] == "Greeting"
assert runtime["package"]["logic"]["logic_source"] == record["logic"]
```

Add `arguments`, `returns`, `recognitions`, `required_replacements` or `optional_replacements` as lists of objects. Omitted lists become empty. Unknown top-level record keys are not preserved; objects inside those lists do not receive deeper domain validation.

[compiler.py](agent_foundry_blueprint_compiler/compiler.py) owns the complete mechanism:

| Step | Contract |
| --- | --- |
| Compile blueprint | Safe package name, nonempty logic, list-of-object sections; normalize logic line endings/trailing whitespace |
| Parse blueprint | Exactly seven known, unique sections with matching package identity and valid JSON bodies |
| Compile runtime record | Preserve the parsed record; hash the supplied blueprint and the canonical record separately |

A whitespace change between fences changes the blueprint hash while leaving the record hash unchanged. Neither hash is a signature or proof that logic is safe.

## Scope and next useful work

This checks the envelope, not Python syntax, argument compatibility or replacement semantics. It does not apply replacements, load dependencies or execute code. A useful extension would validate a selected domain's argument/return objects after parsing while keeping this format round-trip stable.

[Mechanism](docs/MECHANISM.md) · [Tests](tests/test_compiler.py) · [Security](SECURITY.md) · [License](LICENSE.md)
