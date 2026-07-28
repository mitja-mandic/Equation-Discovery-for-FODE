from itertools import count

from nltk import CFG
from nltk.parse.generate import generate


grammar = CFG.fromstring("""
CIRCUIT -> 'Rs' | '(' 'Rs' '+' BLOCK ')'
BLOCK -> ELEMENT | '(' ELEMENT '+' BLOCK ')'
ELEMENT -> 'zarc' | 'randles'
""")

grammar_redone = CFG.fromstring("""
    Circuit -> 'Rs' | 'Rs' '+' Block

    Block -> Element | '(' Element '+' Block ')'

    Element -> 'zarc'
    Element -> 'randles'
    """)

grammar_relaxed = CFG.fromstring("""
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

def parse_expression(tokens, position=0):
    """Convert a fully parenthesized token sequence into a binary tree."""
    token = tokens[position]

    if token != "(":
        return token, position + 1

    left, position = parse_expression(tokens, position + 1)

    operator = tokens[position]
    if operator not in {"+", "||"}:
        raise ValueError(f"Unexpected operator: {operator}")

    right, position = parse_expression(tokens, position + 1)

    if tokens[position] != ")":
        raise ValueError("Expected closing parenthesis")

    return (operator, left, right), position + 1

COLLAPSIBLE_ELEMENTS = {"R", "L"}

# Parameters belonging to the already-expanded composite elements:
#   zarc    = R || CPE
#   randles = R || (CPE + W)
# The element number is shared by all parameters in the same block, so, for
# example, zarc(R1, Q1, alpha1) cannot accidentally mix parameters from two
# different ZARC blocks.
ELEMENT_PARAMETERS = {
    "zarc": ("R", "Q", "alpha"),
    "randles": ("R", "Q", "alpha", "sigma"),
    "R": ("R",),
    "L": ("L",),
    "CPE": ("Q", "alpha"),
    "W": ("sigma",),
    "G": ("Rg", "tauG"),
}


def normalize(node):
    if isinstance(node, str):
        return node

    operator, left, right = node
    children = []

    for child in (normalize(left), normalize(right)):
        if isinstance(child, tuple) and child[0] == operator:
            children.extend(child[1])
        else:
            children.append(child)

    # Collapse repeated ideal elements under the same operator.
    seen = set()
    simplified_children = []

    for child in children:
        if child in COLLAPSIBLE_ELEMENTS:
            if child in seen:
                continue
            seen.add(child)

        simplified_children.append(child)

    children = simplified_children

    # Standalone series resistors are indistinguishable from Rs.
    if operator == "+" and "Rs" in children and "R" in children:
        children.remove("R")

    children.sort(
        key=lambda child: (
            child != "Rs",
            repr(child),
        )
    )

    return operator, tuple(children)


def format_expression(node, parent_operator=None):
    """Add parentheses only when the composition operator changes."""
    if isinstance(node, str):
        return node

    operator, children = node

    expression = f" {operator} ".join(format_expression(child, operator) for child in children)

    if parent_operator is not None and operator != parent_operator:
        return f"({expression})"

    return expression


def number_parameters(node, indices=None):
    """Attach consistently numbered parameters to composite circuit elements.

    Numbering follows the left-to-right order of elements in the normalized
    circuit. ``Rs`` is kept as the name of the series-resistance parameter.

    Examples:
        zarc -> zarc(R1, Q1, alpha1)
        randles -> randles(R1, Q1, alpha1, sigma1)
        randles + zarc ->
            randles(R1, Q1, alpha1, sigma1) + zarc(R2, Q2, alpha2)
        CPE || R -> CPE(Q1, alpha1) || R(R2)
    """
    if indices is None:
        indices = count(start=1)

    if isinstance(node, str):
        parameter_names = ELEMENT_PARAMETERS.get(node)
        if parameter_names is None:
            return node

        index = next(indices)
        parameters = ", ".join(f"{name}{index}" for name in parameter_names)
        return f"{node}({parameters})"

    operator, children = node
    return operator, tuple(number_parameters(child, indices) for child in children)


def canonical_circuit_tree(tokens):
    """Return the normalized tree used by formatters and exporters."""
    if tokens == ("Rs",):
        return "Rs"

    if tokens[:2] != ("Rs", "+"):
        raise ValueError(f"Invalid circuit: {tokens}")

    network, final_position = parse_expression(tokens, position=2)

    if final_position != len(tokens):
        raise ValueError("Unexpected tokens after the circuit expression")

    complete_tree = ("+", "Rs", network)
    return normalize(complete_tree)


def canonical_circuit(tokens):
    normalized_tree = canonical_circuit_tree(tokens)
    return format_expression(number_parameters(normalized_tree))


def possible_circuit_trees(grammar, depth: int) -> set:
    """Generate unique normalized trees suitable for downstream exporters."""
    return {
        canonical_circuit_tree(tuple(circuit))
        for circuit in generate(grammar, depth=depth)
    }


def possible_circuits(grammar, depth: int) -> set[str]:
    return {
        format_expression(number_parameters(tree))
        for tree in possible_circuit_trees(grammar, depth)
    }


if __name__ == "__main__":
    circuits = possible_circuits(grammar_relaxed, depth=5)

    for index, circuit in enumerate(sorted(circuits), start=1):
        print(f"{index}: {circuit}")
