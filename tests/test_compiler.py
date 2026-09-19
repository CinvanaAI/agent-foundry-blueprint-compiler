from __future__ import annotations

import unittest

from agent_foundry_blueprint_compiler import compile_blueprint, compile_runtime_package, parse_blueprint


def record() -> dict:
    return {
        "name": "Normalize Text",
        "required_replacements": [{"anchor": "value", "to_be_replaced": "input"}],
        "optional_replacements": [],
        "logic": "def normalize(value):\n    return value.strip().lower()",
        "arguments": [{"argument_value_name": "value", "argument_question": "Text?"}],
        "returns": [{"return_value_name": "normalized", "return_description": "Clean text"}],
        "recognitions": [{"recognition_name": "author", "recognition_text": "Synthetic example"}],
    }


class CompilerTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        parsed = parse_blueprint(compile_blueprint(record()))
        self.assertEqual(parsed["name"], "Normalize Text")
        self.assertEqual(parsed["logic"]["logic_source"], record()["logic"])

    def test_output_is_deterministic(self) -> None:
        self.assertEqual(compile_blueprint(record()), compile_blueprint(record()))

    def test_runtime_has_two_hash_identities(self) -> None:
        runtime = compile_runtime_package(compile_blueprint(record()))
        self.assertEqual(len(runtime["blueprint_sha256"]), 64)
        self.assertEqual(len(runtime["record_sha256"]), 64)

    def test_missing_logic_fails(self) -> None:
        broken = record()
        broken["logic"] = ""
        with self.assertRaisesRegex(ValueError, "logic source"):
            compile_blueprint(broken)

    def test_unsafe_name_fails(self) -> None:
        broken = record()
        broken["name"] = "../escape"
        with self.assertRaisesRegex(ValueError, "Package name"):
            compile_blueprint(broken)

    def test_unterminated_block_fails(self) -> None:
        text = compile_blueprint(record()).replace("End Normalize Text Logic", "")
        with self.assertRaisesRegex(ValueError, "Unterminated"):
            parse_blueprint(text)

    def test_cross_package_block_fails(self) -> None:
        text = compile_blueprint(record()).replace("Normalize Text Returns", "Other Returns")
        with self.assertRaisesRegex(ValueError, "same package"):
            parse_blueprint(text)


if __name__ == "__main__":
    unittest.main()
