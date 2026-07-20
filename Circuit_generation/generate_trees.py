"""Generate normalized circuit trees from NLTK grammars.

The public tree representation is independent of NLTK:

* an element is a string such as ``"R"`` or ``"CPE"``;
* a connection is ``(operator, children)``, where ``operator`` is ``"+"``
  for series or ``"||"`` for parallel and ``children`` is a tuple of trees.

NLTK is used only to generate token sequences from the grammar. Downstream
modules can consume the returned trees without importing NLTK.
"""

from __future__ import annotations

import argparse
from typing import Any, Sequence


Tree = str | tuple[str, tuple["Tree", ...]]
ParsedTree = str | tuple[str, "ParsedTree", "ParsedTree"]


GRAMMAR_SOURCES = {
    "redone": """
        Circuit -> 'Rs' | 'Rs' '+' Block

        Block -> Element | '(' Element '+' Block ')'

        Element -> 'zarc'
        Element -> 'randles'
    """,
    "relaxed": """
        Circuit -> 'Rs'
        Circuit -> 'Rs' '+' Network

        Network -> Element
        Network -> '(' Network '+' Network ')'
        Network -> '(' Network '||' Network ')'

        Element -> 'R'
        Element -> 'L'
        Element -> 'CPE'
        Element -> 'W'
        Element -> 'G'
    """,
}

COLLAPSIBLE_ELEMENTS = {"R", "L"}


def parse_expression(
    tokens: Sequence[str],
    position: int = 0,
) -> tuple[ParsedTree, int]:
    """Convert a fully parenthesized token sequence into a binary tree."""
    if position >= len(tokens):
        raise ValueError("Unexpected end of circuit expression")

    token = tokens[position]
    if token != "(":
        return token, position + 1

    left, position = parse_expression(tokens, position + 1)
    if position >= len(tokens):
        raise ValueError("Expected an operator after the left branch")

    operator = tokens[position]
    if operator not in {"+", "||"}:
        raise ValueError(f"Unexpected operator: {operator}")

    right, position = parse_expression(tokens, position + 1)
    if position >= len(tokens) or tokens[position] != ")":
        raise ValueError("Expected closing parenthesis")

    return (operator, left, right), position + 1


def normalize(node: ParsedTree) -> Tree:
    """Flatten, simplify, and deterministically order a parsed circuit tree."""
    if isinstance(node, str):
        return node

    operator, left, right = node
    children: list[Tree] = []
    for child in (normalize(left), normalize(right)):
        if isinstance(child, tuple) and child[0] == operator:
            children.extend(child[1])
        else:
            children.append(child)

    seen: set[str] = set()
    simplified_children: list[Tree] = []
    for child in children:
        if isinstance(child, str) and child in COLLAPSIBLE_ELEMENTS:
            if child in seen:
                continue
            seen.add(child)
        simplified_children.append(child)

    # A free series R is topologically redundant with the existing Rs.
    if operator == "+" and "Rs" in simplified_children:
        try:
            simplified_children.remove("R")
        except ValueError:
            pass

    simplified_children.sort(
        key=lambda child: (
            child != "Rs",
            repr(child),
        )
    )
    return operator, tuple(simplified_children)


def canonical_circuit_tree(tokens: Sequence[str]) -> Tree:
    """Convert one generated token sequence into a normalized circuit tree."""
    if tuple(tokens) == ("Rs",):
        return "Rs"

    if tuple(tokens[:2]) != ("Rs", "+"):
        raise ValueError(f"Invalid circuit: {tuple(tokens)}")

    network, final_position = parse_expression(tokens, position=2)
    if final_position != len(tokens):
        raise ValueError("Unexpected tokens after the circuit expression")

    complete_tree: ParsedTree = ("+", "Rs", network)
    return normalize(complete_tree)


def format_tree(tree: Tree, parent_operator: str | None = None) -> str:
    """Return a compact, unnumbered circuit description for a tree."""
    if isinstance(tree, str):
        return tree

    operator, children = tree
    expression = f" {operator} ".join(
        format_tree(child, operator) for child in children
    )
    if parent_operator is not None and operator != parent_operator:
        return f"({expression})"
    return expression


def get_grammar(name: str) -> Any:
    """Build one of the configured NLTK grammars by name."""
    try:
        source = GRAMMAR_SOURCES[name]
    except KeyError as error:
        choices = ", ".join(sorted(GRAMMAR_SOURCES))
        raise ValueError(f"Unknown grammar {name!r}; choose from {choices}") from error

    from nltk import CFG

    return CFG.fromstring(source)


def possible_circuit_trees(grammar: Any, depth: int) -> set[Tree]:
    """Generate all unique normalized trees up to an NLTK depth limit."""
    if depth < 1:
        raise ValueError("depth must be at least 1")

    from nltk.parse.generate import generate

    return {
        canonical_circuit_tree(tuple(tokens))
        for tokens in generate(grammar, depth=depth)
    }


def generate_trees(grammar_name: str = "relaxed", depth: int = 5) -> set[Tree]:
    """Generate normalized trees from a named grammar."""
    return possible_circuit_trees(get_grammar(grammar_name), depth)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate normalized Python circuit trees with NLTK."
    )
    parser.add_argument(
        "--grammar",
        choices=tuple(GRAMMAR_SOURCES),
        default="relaxed",
        help="grammar to use (default: relaxed)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=5,
        help="maximum NLTK derivation depth (default: 5)",
    )
    args = parser.parse_args()

    try:
        trees = generate_trees(args.grammar, args.depth)
    except ValueError as error:
        parser.error(str(error))

    for index, tree in enumerate(sorted(trees, key=format_tree), start=1):
        print(f"{index}: {tree!r}")


if __name__ == "__main__":
    main()
