import unittest

from nltk.parse.generate import generate

from Circuit_generation.circuit_from_grammar import (
    GRAMMAR_SOURCES,
    generate_trees,
    get_grammar,
)


class CircuitGrammarTests(unittest.TestCase):
    def test_every_named_grammar_is_valid(self):
        for name in GRAMMAR_SOURCES:
            with self.subTest(grammar=name):
                self.assertIsNotNone(get_grammar(name))

    def test_compact_hybrid_expands_motifs_and_raw_elements(self):
        sentences = {
            tuple(tokens)
            for tokens in generate(get_grammar("compact_hybrid"), depth=5)
        }

        self.assertIn(("Rs", "+", "(", "CPE", "||", "R", ")"), sentences)
        self.assertIn(
            (
                "Rs", "+", "(", "CPE", "||", "(",
                "R", "+", "W", ")", ")",
            ),
            sentences,
        )
        self.assertIn(("Rs", "+", "L"), sentences)
        self.assertIn(("Rs", "+", "W"), sentences)

    def test_compact_only_blocks_expands_all_four_blocks(self):
        sentences = {
            tuple(tokens)
            for tokens in generate(get_grammar("compact_only_blocks"), depth=6)
        }

        expected = {
            ("Rs", "+", "(", "CPE", "||", "R", ")"),
            (
                "Rs", "+", "(", "CPE", "||", "(",
                "R", "+", "W", ")", ")",
            ),
            ("Rs", "+", "(", "R", "+", "W", ")"),
            ("Rs", "+", "(", "R", "+", "L", ")"),
        }
        self.assertTrue(expected.issubset(sentences))

    def test_motif_tokens_convert_to_executable_circuits(self):
        circuits = generate_trees("compact_only_blocks", depth=6)

        self.assertTrue(circuits)
        for circuit in circuits:
            self.assertTrue(hasattr(circuit, "impedance"))


if __name__ == "__main__":
    unittest.main()
