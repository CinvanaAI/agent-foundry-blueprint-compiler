# Agent Foundry Blueprint Compiler: mechanism

[compiler.py](../agent_foundry_blueprint_compiler/compiler.py) owns compilation, fence parsing and canonical JSON hashes. `compile_blueprint(record)` returns text; `parse_blueprint(text)` returns a normalized record; `compile_runtime_package(text)` adds hashes of the blueprint and normalized record. The name, logic and list-shaped sections are checked. Argument meanings and function correctness are still the caller’s responsibility.

## Limits that matter

The public grammar deliberately uses strict JSON sections. Importing a historical editor export may require normalization; round-trip support applies to this documented grammar.

## Demonstration contract

Input: A JSON package record containing a Python text-normalizer function.

Expected observation: Seven fenced blocks round-trip to one normalized record; a mixed-package fence is rejected.

The bundled example uses synthetic material. Its observed output establishes that bounded path, not every possible integration.
