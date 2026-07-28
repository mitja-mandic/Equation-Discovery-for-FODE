from nltk.parse.generate import generate
from nltk import CFG
import argparse

grammar = CFG.fromstring("""
CIRCUIT -> 'rs' | 'rs' BLOCK
BLOCK -> ELEMENT | ELEMENT BLOCK
ELEMENT -> 'zarc' | 'randles'
""")

grammar = CFG.fromstring("""
CIRCUIT -> 'rs' | 'rs' BLOCK
BLOCK -> ELEMENT | ELEMENT '+' BLOCK
ELEMENT -> 'zarc' | 'randles'
""")

grammar_saso = CFG.fromstring("""
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
""")
#for sentence in generate(grammar, depth = 6):
#    print(sentence)
#    print(' '.join(sentence))

def format_circuit(tokens: tuple[str, ...]) -> str:
    expression = " ".join(tokens)
    expression = expression.replace("( ", "(")
    expression = expression.replace(" )", ")")
    return expression


def possible_circuits(grammar, depth: int) -> set[str]:
    return {
        format_circuit(tuple(circuit))
        for circuit in generate(grammar, depth=depth)
    }

circs = possible_circuits(grammar_saso, 5)
print(circs)


def main() -> None:
    """Print circuits generated from a grammar and tree-depth limit."""
    parser = argparse.ArgumentParser(
        description="Generate circuits from an NLTK grammar."
    )
    #parser.add_argument(
    #    "grammar",
    #    type=Path,
    #    help="Path to the NLTK grammar file",
    #)
    parser.add_argument(
        "--depth",
        type=int,
        default=6,
        help="Maximum tree depth (default: 6)",
    )
    args = parser.parse_args()

    #grammar = CFG.fromstring(args.grammar.read_text(encoding="utf-8"))
    circuits = possible_circuits(grammar_saso, args.depth)

    for index, circuit in enumerate(circuits, start=1):
        print(f"{index}: {circuit}")


if __name__ == "__main__":
    main()
