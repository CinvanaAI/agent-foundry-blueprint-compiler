# Agent Foundry Blueprint Compiler

A Python library for capability definitions you can read before you run. It converts a package record into seven named blueprint blocks, parses those blocks back, and rejects crossed or missing boundaries. It never executes the embedded Python.

## Try it

Python 3.11 or newer. From the checkout:

```sh
python -m pip install -e .
python -m examples.demo
```

The complete input is [examples/record.json](examples/record.json). The example creates `package.blueprint.txt` and `runtime.json` in a new temporary directory, prints that directory, and proves that a block belonging to a different package is rejected. Expected fields include `round_trip: true` and `mixed_package_rejected: true`.

## How it works

Human-readable boundaries and machine-checkable round trips make a capability definition inspectable before execution. Read the [mechanism and implementation notes](docs/MECHANISM.md) for the specific boundaries and source links.

## Scope

The public grammar deliberately uses strict JSON sections. Importing a historical editor export may require normalization; round-trip support applies to this documented grammar.

## Verify

`python -m pytest` runs the behavior tests (install `pytest` first). The runnable example above provides a separate first-use check.

MIT licensed; see [LICENSE.md](LICENSE.md). Origin and release boundaries are documented in [ORIGIN.md](ORIGIN.md) and [SECURITY.md](SECURITY.md).
## Inspect the example result

Open the [saved synthetic result](examples/captured-result.json) alongside its [input and demonstration](examples/demo.py). The result is from the bundled synthetic example; local machine paths and temporary run identifiers are excluded from public projections.
