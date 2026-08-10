from nltk import CFG
from nltk.parse.generate import generate
if __package__:
    from .circuit_class import CircuitNode, Element, Resistor, SeriesResistance, CPE, Warburg, Inductor, Series, Parallel, Gerischer
else:
    from circuit_class import CircuitNode, Element, Resistor, SeriesResistance, CPE, Warburg, Inductor, Series, Parallel, Gerischer

from typing import Any, Sequence
from itertools import count

GRAMMAR_SOURCES = {
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

ELEMENT_TYPES = {
    "Rs": SeriesResistance,
    "R": Resistor,
    "L": Inductor,
    "CPE": CPE,
    "W": Warburg,
    "G": Gerischer,
}

CONNECTION_TYPES = {
    "+": Series,
    "||": Parallel
    }

SORT_RANK = {
    SeriesResistance: 0,
    Resistor: 10,
    Inductor: 20,
    CPE: 30,
    Warburg: 40,
    Gerischer: 50,
    Series: 100,
    Parallel: 110,
}


def circuit_sort_key(node: CircuitNode):
    return SORT_RANK[type(node)], repr(node)


#PART 1: Generate the NLTK grammar and all productions up to certain depth:

def generate_trees(grammar_name: str = "relaxed", depth: int = 5):# -> set[Tree]:
    """Generate normalized trees from a named grammar. Function to call to generate all trees"""
    return {normalize(tree) for tree in possible_circuit_trees(get_grammar(grammar_name), depth)}


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
    return {circuit_list_to_objects(generated_list) for generated_list in generate(grammar, depth=depth)
    }

###
def circuit_list_to_string(circuit: list, already_done = ''):
    '''String representation of a circuit'''
    if not circuit:
        return already_done

    for index, element in enumerate(circuit):
        if element == '(':
            already_done += element
            remainder = circuit[index+1:]
            return circuit_list_to_string(remainder, already_done)
        else:
            already_done += element

    return already_done


#PART 2: translate the lists to python structures defined in circuit_class.py

def circuit_list_to_objects(tokens):
    if tokens == ["Rs"]:
        return SeriesResistance()

    if tuple(tokens[:2]) != ("Rs", "+") and len(tokens) > 2:
        raise ValueError(f"Invalid circuit: {tuple(tokens)}")

    operator = CONNECTION_TYPES[tokens[1]]
    if len(tokens) == 3:
        left = SeriesResistance()
        right = ELEMENT_TYPES[tokens[2]]()
        return operator((left,right))

    inner_circuit, final_position = parse_inner_expression(tokens, 2)

    if final_position != len(tokens):
        raise ValueError(
            f"Unexpected trailing tokens: {tokens[final_position:]}"
        )

    return operator((SeriesResistance(),inner_circuit))
    
        #return operator((SeriesResistance(),parse_inner_expression(tokens, 2)))

def parse_inner_expression(tokens: Sequence[str],position: int = 0):# -> tuple[ParsedTree, int]:
    """Convert a fully parenthesized token sequence into a binary tree."""
    if position >= len(tokens):
        raise ValueError("Unexpected end of circuit expression")

    token = tokens[position]
    if token != "(":
        return token, position + 1

    left, position = parse_inner_expression(tokens, position + 1)

    
    if position >= len(tokens):
        raise ValueError("Expected an operator after the left branch")
    #print(left)
    operator = tokens[position]
    if operator not in {"+", "||"}:
        raise ValueError(f"Unexpected operator: {operator}")

    right, position = parse_inner_expression(tokens, position + 1)
    
    if position >= len(tokens) or tokens[position] != ")":
        raise ValueError("Expected closing parenthesis")

    connection = CONNECTION_TYPES[operator]

    
    #check if element needs to be converted to object (is still string) or not
    if isinstance(left, str):
        left = ELEMENT_TYPES[left]()

    if isinstance(right, str):
        right = ELEMENT_TYPES[right]()

    return connection((left,right)), position + 1

# STEP 3: NORMALIZE THE TREE, REMOVE UNNECESSARY ELEMENTS AND CONNECTIONS

def is_connection(node: CircuitNode):
    return type(node).__name__ in ['Parallel', 'Series']

def normalize(node):
    """Flatten, simplify, and deterministically order a parsed circuit tree."""
    if isinstance(node, Element):
        return node
    
    operator, node_children = type(node), node.children
    children = []
    
    for child in node_children:
        x = normalize(child)
        
        if type(x) is operator:
            #children += x
            children.extend(x.children) # type: ignore
        else:
            children.append(x)

    simplified_children = simplify(operator, children)
    simplified_children.sort(key=circuit_sort_key)

    if len(simplified_children) == 1:
        return simplified_children[0]

    return operator(tuple(simplified_children))

def find_series_resistance(connection_type, lst):
    if connection_type is Series:
        for index, x in enumerate(lst):
            if type(x) is SeriesResistance:
                return index, True
    return -1, False


def simplify(connection_type: type[Series] | type[Parallel], children: list[CircuitNode]) -> list[CircuitNode]:
    #has_series_resistance = any(type(x) is SeriesResistance for x in children) and connection_type is Series
    loc, has_series_resistance = find_series_resistance(connection_type, children)
    collapsible_types = [Inductor, Resistor]
    seen = set()
    simplified_list = []

    if has_series_resistance:
        simplified_list.append(children[loc])
        children.pop(loc)
        seen.add(Resistor)
    for element in children:
        if type(element) not in collapsible_types:
            simplified_list.append(element)
        elif type(element) not in seen:
            simplified_list.append(element)
            seen.add(element.__class__)
            
    return simplified_list


            
def add_indexes(circuit: CircuitNode) -> CircuitNode:
    i = count(start=1)
    def visit(node):
        if isinstance(node, SeriesResistance):
            return node

        if isinstance(node, Element):
            return node.number_parameters(next(i)) #type: ignore

        return type(node)(
            tuple(visit(child) for child in node.children)
        )
    return visit(circuit)

#tokens = ["Rs", "+", "(", "R", "||", "CPE", ")"]
#
#topology = circuit_list_to_objects(tokens)
#normalized = normalize(topology)
#circuit = add_indexes(normalized)
#
#parameters = {
#    "Rs": 0.1,
#    "R1": 2.5,
#    "Q2": 0.03,
#    "alpha2": 0.87,
#}
#
#print(circuit.impedance(3,parameters))