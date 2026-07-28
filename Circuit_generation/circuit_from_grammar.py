from nltk import CFG
from nltk.parse.generate import generate
from circuit_class import Resistor, SeriesResistance, CPE, Warburg, Inductor, Series, Parallel, CircuitNode

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

#PART 1: Generate the NLTK grammar and all productions up to certain depth:

def generate_trees(grammar_name: str = "relaxed", depth: int = 5):# -> set[Tree]:
    """Generate normalized trees from a named grammar. Function to call to generate all trees"""
    return possible_circuit_trees(get_grammar(grammar_name), depth)


def get_grammar(name: str):# -> Any:
    """Build one of the configured NLTK grammars by name."""
    try:
        source = GRAMMAR_SOURCES[name]
    except KeyError as error:
        choices = ", ".join(sorted(GRAMMAR_SOURCES))
        raise ValueError(f"Unknown grammar {name!r}; choose from {choices}") from error

    return CFG.fromstring(source) #builds grammar


def possible_circuit_trees(grammar: Any, depth: int):# -> set[Tree]:
    """Generate all unique normalized trees up to an NLTK depth limit."""
    if depth < 1:
        raise ValueError("depth must be at least 1")
    return {parse_circuit_list(tuple(generated_list)) for generated_list in generate(grammar, depth=depth)
    }


#PART 2: translate the lists to python structures defined in circuit_class.py

def parse_circuit_list(circuit_list):
    initial_resistance = SeriesResistance("Rs")
    circuit_list = circuit_list[2:]
    

