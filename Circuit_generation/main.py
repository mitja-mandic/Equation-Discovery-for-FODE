"""Generate circuit trees and list their Python impedance equations.

Edit the settings directly below, then run this file from your Python IDE.
No command-line arguments are required.
"""

from __future__ import annotations

from collections.abc import Iterable

if __package__:
    from .circuit_from_tree import circuit_from_tree
    from .generate_trees import Tree, format_tree, generate_trees
else:
    # Used when main.py is run directly instead of imported as a package.
    from circuit_from_tree import circuit_from_tree
    from generate_trees import Tree, format_tree, generate_trees


# ---------------------------------------------------------------------------
# SETTINGS: edit these values and press Run in your IDE.
# ---------------------------------------------------------------------------

GRAMMAR_NAME = "relaxed"  # "redone" uses zarc/randles; "relaxed" uses primitives.
TREE_DEPTH = 4


def build_equation_listing(trees: Iterable[Tree]) -> str:
    """Return a deterministic list of circuits and Python Z(omega) equations."""
    ordered_trees = sorted(trees, key=format_tree)
    if not ordered_trees:
        raise ValueError("The grammar did not generate any circuit trees")

    entries: list[str] = []
    for number, tree in enumerate(ordered_trees, start=1):
        circuit = circuit_from_tree(tree)
        parameters = ", ".join(circuit.parameter_names)
        entries.append(
            "\n".join(
                (
                    f"{number}. Circuit: {circuit}",
                    f"   Z_{number}(omega) = {circuit.impedance_expression()}",
                    f"   Parameters: {parameters}",
                )
            )
        )
    return "\n\n".join(entries)


def main() -> None:
    """Generate all trees and print their executable impedance equations."""
    trees = generate_trees(GRAMMAR_NAME, TREE_DEPTH)
    print(f"IMPEDANCE EQUATIONS ({GRAMMAR_NAME}, depth={TREE_DEPTH})\n")
    print(build_equation_listing(trees))


if __name__ == "__main__":
    main()
