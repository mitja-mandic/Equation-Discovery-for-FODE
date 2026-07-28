import argparse
import re
from collections.abc import Mapping, Sequence


grammar = {
    "Circuit": [
        "Rs",
        "Series(Rs, Block)"
    ],
    "Block": [
        "Element",
        "Series(Element, Block)"
    ],
    "Element": [
        "Parallel(R, Series(CPE, W))",
        "Parallel(R, CPE)"
    ]
}

nonterminals = set(grammar.keys())


def generate_from_grammar(
    rules: Mapping[str, Sequence[str]],
    start_symbol: str,
    max_expansions: int,
) -> list[str]:
    """Generate all terminal strings reachable within an expansion limit.

    The leftmost nonterminal is expanded at every step.  The limit is required
    because a recursive grammar can otherwise produce infinitely many strings.

    Args:
        rules: Mapping of nonterminal names to their possible productions.
        start_symbol: Nonterminal from which generation starts.
        max_expansions: Maximum number of production applications per result.

    Returns:
        Unique terminal strings in grammar-production order.

    Raises:
        ValueError: If the start symbol is unknown, the limit is not positive,
            or the grammar contains a nonterminal without productions.
    """
    if start_symbol not in rules:
        raise ValueError(f"Unknown start symbol: {start_symbol!r}")
    if max_expansions < 1:
        raise ValueError("max_expansions must be at least 1")

    empty_nonterminals = [
        symbol for symbol, productions in rules.items() if not productions
    ]
    if empty_nonterminals:
        names = ", ".join(sorted(empty_nonterminals))
        raise ValueError(f"Nonterminals without productions: {names}")

    # Longer names go first so one name cannot match inside another name.
    alternatives = "|".join(
        re.escape(symbol) for symbol in sorted(rules, key=len, reverse=True)
    )
    nonterminal_pattern = re.compile(rf"\b(?:{alternatives})\b")

    generated: list[str] = []
    seen: set[str] = set()

    def expand(expression: str, expansions_left: int) -> None:
        match = nonterminal_pattern.search(expression)
        if match is None:
            if expression not in seen:
                seen.add(expression)
                generated.append(expression)
            return
        if expansions_left == 0:
            return

        symbol = match.group()
        for production in rules[symbol]:
            next_expression = (
                expression[: match.start()]
                + production
                + expression[match.end() :]
            )
            expand(next_expression, expansions_left - 1)

    expand(start_symbol, max_expansions)
    return generated


def generate_circuits(max_elements: int = 3) -> list[str]:
    """Generate circuits containing at most ``max_elements`` parallel blocks.

    A value of zero returns only ``Rs``.  With the current grammar, a circuit
    with ``n`` elements needs ``1 + 2*n`` expansions: one ``Circuit`` expansion
    and one ``Block`` plus one ``Element`` expansion per element.
    """
    if max_elements < 0:
        raise ValueError("max_elements cannot be negative")

    max_expansions = 1 + 2 * max_elements
    return generate_from_grammar(grammar, "Circuit", max_expansions)


def main() -> None:
    """Print circuits generated from the command-line element limit."""
    parser = argparse.ArgumentParser(description="Generate circuits from the grammar.")
    parser.add_argument(
        "--max-elements",
        type=int,
        default=3,
        help="maximum number of circuit elements after Rs (default: 3)",
    )
    args = parser.parse_args()

    circuits = generate_circuits(args.max_elements)
    for index, circuit in enumerate(circuits, start=1):
        print(f"{index}: {circuit}")


if __name__ == "__main__":
    main()

