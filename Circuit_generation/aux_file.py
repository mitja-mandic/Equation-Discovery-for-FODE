from nltk import CFG
from nltk.parse.generate import generate


import argparse
from typing import Any, Sequence

from circuit_class import Resistor, SeriesResistance, CPE, Warburg, Inductor, Gerischer, Series, Parallel, CircuitNode

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

gramatika = CFG.fromstring(GRAMMAR_SOURCES['relaxed'])


with open('Circuit_generation/vezja.txt', 'w') as f:
    y = 1
    for x in generate(gramatika, depth=4):
        f.write(f"{y}: {x}\n")
        y += 1
#rezultat:
#['Rs']
#['Rs', '+', 'R']
#['Rs', '+', 'L']
#['Rs', '+', 'CPE']
#['Rs', '+', 'W']
#['Rs', '+', 'G']
#PATTERN = r'''(?<=\()[^()]*(?=\))'''

COLLAPSIBLE_PATTERNS = {'R+R':'R','(R+R)':'R','(L+L)':'L','Rs+R':'Rs','R||R':'R','(L||L)':'L'}

#circuit=['Rs', '+', '(', '(', 'L', '+', 'W', ')', '+', '(', 'G', '||', 'G', ')', ')']
#circuit = ['Rs', '+', '(', '(', 'R', '+', 'L', ')', '+', 'R', ')']


def get_grammar(name: str):
    """Build one of the configured NLTK grammars by name."""
    try:
        source = GRAMMAR_SOURCES[name]
    except KeyError as error:
        choices = ", ".join(sorted(GRAMMAR_SOURCES))
        raise ValueError(f"Unknown grammar {name!r}; choose from {choices}") from error

    from nltk import CFG

    return CFG.fromstring(source) #builds grammar



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

#def traverse_tree(tree_list):
#    circuit = []
#    for i, element in enumerate(tree_list):
#        if element == '(':
#            circuit.append(element)
            
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
circuit = ['Rs', '+', '(', '(', 'R', '+', 'L', ')', '+', 'R', ')']

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

    

    if isinstance(left, str):
        left = ELEMENT_TYPES[left]()

    if isinstance(right, str):
        right = ELEMENT_TYPES[right]()

    #return connection((element_left(), element_right())), position + 1
        #if operator == '+':
        #    return connection((element_left(), element_right())), position + 1
        #elif operator == '||':
        #    return connection((element_left(), element_right())), position + 1
    return connection((left,right)), position + 1
    #else:
    #    return connection((left,right)), position + 1
    #return (operator, left, right), position + 1

print(circuit_list_to_objects(tuple(circuit)))