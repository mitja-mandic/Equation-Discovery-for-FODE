from collections import defaultdict
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

