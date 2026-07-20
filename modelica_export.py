"""Export normalized NLTK circuit trees as connected Modelica models.

The generated package is deliberately self-contained.  It defines phasor pins
with real and imaginary voltage/current components, primitive impedance
elements, connected candidate circuits, and a unit-current experiment for each
candidate.  OpenModelica can then flatten those connections into equations.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import count
from pathlib import Path

import alt_parse


@dataclass(frozen=True)
class Element:
    """A primitive circuit element with a stable topology index."""

    kind: str
    index: int


Tree = str | Element | tuple[str, tuple["Tree", ...]]


MODELICA_PREAMBLE = """within ;
package GeneratedEISCircuits
  constant Real pi = 3.141592653589793;

  connector Pin
    Real v_re "Real part of phasor voltage";
    Real v_im "Imaginary part of phasor voltage";
    flow Real i_re "Real part of phasor current";
    flow Real i_im "Imaginary part of phasor current";
  end Pin;

  partial model OnePort
    Pin p;
    Pin n;
    Real v_re;
    Real v_im;
    Real i_re;
    Real i_im;
  equation
    v_re = p.v_re - n.v_re;
    v_im = p.v_im - n.v_im;
    i_re = p.i_re;
    i_im = p.i_im;
    p.i_re + n.i_re = 0;
    p.i_im + n.i_im = 0;
  end OnePort;

  model Resistor
    extends OnePort;
    parameter Real R(min=0) = 1;
  equation
    v_re = R*i_re;
    v_im = R*i_im;
  end Resistor;

  model Inductor
    extends OnePort;
    parameter Real omega(min=0) = 2*pi;
    parameter Real L(min=0) = 1e-3;
  equation
    v_re = -omega*L*i_im;
    v_im = omega*L*i_re;
  end Inductor;

  model CPE
    extends OnePort;
    parameter Real omega(min=0) = 2*pi;
    parameter Real Q(min=0) = 1e-2;
    parameter Real alpha(min=0, max=1) = 0.8;
    Real y_re;
    Real y_im;
  equation
    y_re = Q*omega^alpha*cos(pi*alpha/2);
    y_im = Q*omega^alpha*sin(pi*alpha/2);
    i_re = y_re*v_re - y_im*v_im;
    i_im = y_im*v_re + y_re*v_im;
  end CPE;

  model InfiniteWarburg
    extends OnePort;
    parameter Real omega(min=0) = 2*pi;
    parameter Real sigma(min=0) = 1;
    Real a;
  equation
    a = sigma/sqrt(2*omega);
    v_re = a*(i_re + i_im);
    v_im = a*(i_im - i_re);
  end InfiniteWarburg;

  model Gerischer
    extends OnePort;
    parameter Real omega(min=0) = 2*pi;
    parameter Real Rg(min=0) = 1;
    parameter Real tauG(min=0) = 1;
    Real rho;
    Real y_re;
    Real y_im;
  equation
    rho = sqrt(1 + (omega*tauG)^2);
    y_re = sqrt((rho + 1)/2)/Rg;
    y_im = sqrt((rho - 1)/2)/Rg;
    i_re = y_re*v_re - y_im*v_im;
    i_im = y_im*v_re + y_re*v_im;
  end Gerischer;

  model UnitCurrent
    Pin p;
    Pin n;
  equation
    p.i_re = -1;
    p.i_im = 0;
    p.i_re + n.i_re = 0;
    p.i_im + n.i_im = 0;
  end UnitCurrent;

  model Ground
    Pin p;
  equation
    p.v_re = 0;
    p.v_im = 0;
  end Ground;
"""


PARAMETER_DEFAULTS = {
    "Rs": "0.1",
    "R": "1",
    "L": "1e-3",
    "Q": "1e-2",
    "alpha": "0.8",
    "sigma": "1",
    "Rg": "1",
    "tauG": "1",
}

PARAMETERS_BY_KIND = {
    "Rs": ("Rs",),
    "R": ("R",),
    "L": ("L",),
    "CPE": ("Q", "alpha"),
    "W": ("sigma",),
    "G": ("Rg", "tauG"),
}


def expand_and_number(node, indices=None) -> Tree:
    """Number primitive elements and expand ZARC/Randles macros."""
    if indices is None:
        indices = count(start=1)

    if isinstance(node, str):
        if node == "Rs":
            return Element("Rs", 0)

        index = next(indices)
        if node == "zarc":
            return (
                "||",
                (Element("R", index), Element("CPE", index)),
            )
        if node == "randles":
            return (
                "||",
                (
                    Element("R", index),
                    (
                        "+",
                        (Element("CPE", index), Element("W", index)),
                    ),
                ),
            )
        if node not in PARAMETERS_BY_KIND:
            raise ValueError(f"Unsupported circuit element: {node!r}")
        return Element(node, index)

    operator, children = node
    return operator, tuple(expand_and_number(child, indices) for child in children)


def parameter_name(base: str, element: Element) -> str:
    if element.kind == "Rs":
        return "Rs"
    return f"{base}{element.index}"


def collect_parameters(node: Tree) -> list[tuple[str, str]]:
    """Return unique Modelica parameter names and default values in tree order."""
    collected: list[tuple[str, str]] = []
    seen: set[str] = set()

    def visit(current: Tree) -> None:
        if isinstance(current, Element):
            for base in PARAMETERS_BY_KIND[current.kind]:
                name = parameter_name(base, current)
                if name not in seen:
                    seen.add(name)
                    collected.append((name, PARAMETER_DEFAULTS[base]))
            return
        if isinstance(current, str):
            raise ValueError(f"Unexpanded element: {current!r}")
        _, children = current
        for child in children:
            visit(child)

    visit(node)
    return collected


class CircuitModelBuilder:
    """Translate a numbered tree into declarations and connect equations."""

    MODELS = {
        "Rs": "Resistor",
        "R": "Resistor",
        "L": "Inductor",
        "CPE": "CPE",
        "W": "InfiniteWarburg",
        "G": "Gerischer",
    }

    INSTANCE_PREFIXES = {
        "Rs": "rs",
        "R": "r",
        "L": "l",
        "CPE": "cpe",
        "W": "w",
        "G": "g",
    }

    def __init__(self) -> None:
        self.declarations: list[str] = []
        self.connections: list[str] = []
        self.node_indices = count(start=1)

    def emit(self, node: Tree, p: str, n: str) -> None:
        if isinstance(node, Element):
            self._emit_element(node, p, n)
            return
        if isinstance(node, str):
            raise ValueError(f"Unexpanded element: {node!r}")

        operator, children = node
        if operator == "+":
            self._emit_series(children, p, n)
        elif operator == "||":
            for child in children:
                self.emit(child, p, n)
        else:
            raise ValueError(f"Unsupported composition operator: {operator!r}")

    def _emit_series(self, children: tuple[Tree, ...], p: str, n: str) -> None:
        left_pin = p
        for child_index, child in enumerate(children):
            is_last = child_index == len(children) - 1
            if is_last:
                right_pin = n
            else:
                right_pin = f"node{next(self.node_indices)}"
                self.declarations.append(f"Pin {right_pin};")
            self.emit(child, left_pin, right_pin)
            left_pin = right_pin

    def _emit_element(self, element: Element, p: str, n: str) -> None:
        model = self.MODELS[element.kind]
        prefix = self.INSTANCE_PREFIXES[element.kind]
        instance = prefix if element.kind == "Rs" else f"{prefix}{element.index}"

        modifiers = []
        if element.kind in {"L", "CPE", "W", "G"}:
            modifiers.append("omega=omega")
        for base in PARAMETERS_BY_KIND[element.kind]:
            component_parameter = "R" if element.kind == "Rs" else base
            modifiers.append(
                f"{component_parameter}={parameter_name(base, element)}"
            )

        self.declarations.append(f"{model} {instance}({', '.join(modifiers)});")
        self.connections.append(f"connect({p}, {instance}.p);")
        self.connections.append(f"connect({instance}.n, {n});")


def parameter_declaration(name: str, default: str) -> str:
    if name.startswith("alpha"):
        return f"parameter Real {name}(min=0, max=1) = {default};"
    return f"parameter Real {name}(min=0) = {default};"


def render_candidate(model_name: str, normalized_tree) -> str:
    numbered_tree = expand_and_number(normalized_tree)
    builder = CircuitModelBuilder()
    builder.emit(numbered_tree, "p", "n")

    lines = [f"  model {model_name}", "    parameter Real omega(min=0) = 2*pi;"]
    for name, default in collect_parameters(numbered_tree):
        lines.append(f"    {parameter_declaration(name, default)}")
    lines.extend(("    Pin p;", "    Pin n;"))
    lines.extend(f"    {declaration}" for declaration in builder.declarations)
    lines.append("  equation")
    lines.extend(f"    {connection}" for connection in builder.connections)
    lines.append(f"  end {model_name};")
    return "\n".join(lines)


def render_experiment(model_name: str) -> str:
    experiment_name = f"{model_name}Impedance"
    return f"""  model {experiment_name}
    parameter Real omega(min=0) = 2*pi;
    {model_name} circuit(omega=omega);
    UnitCurrent source;
    Ground ground;
    Real Z_re;
    Real Z_im;
  equation
    connect(source.p, circuit.p);
    connect(source.n, circuit.n);
    connect(ground.p, circuit.n);
    Z_re = circuit.p.v_re - circuit.n.v_re;
    Z_im = circuit.p.v_im - circuit.n.v_im;
  end {experiment_name};"""


def render_package(normalized_trees: list) -> tuple[str, list[tuple[str, str]]]:
    descriptions_and_trees = sorted(
        (
            alt_parse.format_expression(alt_parse.number_parameters(tree)),
            tree,
        )
        for tree in normalized_trees
    )

    sections = [MODELICA_PREAMBLE.rstrip()]
    manifest: list[tuple[str, str]] = []
    for index, (description, tree) in enumerate(descriptions_and_trees, start=1):
        model_name = f"Candidate{index:03d}"
        manifest.append((model_name, description))
        sections.append(f"  // {description}")
        sections.append(render_candidate(model_name, tree))
        sections.append(render_experiment(model_name))

    sections.append("end GeneratedEISCircuits;")
    return "\n\n".join(sections) + "\n", manifest


def render_openmodelica_script(manifest: list[tuple[str, str]]) -> str:
    lines = ['loadFile("GeneratedEISCircuits.mo");']
    for model_name, _ in manifest:
        experiment_name = f"GeneratedEISCircuits.{model_name}Impedance"
        lines.extend(
            (
                f"flatModel := instantiateModel({experiment_name});",
                f'writeFile("{model_name}_flat.mo", flatModel);',
            )
        )
    lines.append("getErrorString();")
    return "\n".join(lines) + "\n"


def select_grammar(name: str):
    grammars = {
        "redone": alt_parse.grammar_redone,
        "relaxed": alt_parse.grammar_relaxed,
    }
    return grammars[name]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate connected Modelica circuits from the NLTK grammar."
    )
    parser.add_argument(
        "--grammar",
        choices=("redone", "relaxed"),
        default="relaxed",
        help="circuit grammar to export (default: relaxed)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=5,
        help="maximum NLTK derivation depth (default: 5)",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=None,
        help="optionally export only the first N canonical candidates",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated_modelica"),
        help="directory for .mo and .mos files",
    )
    args = parser.parse_args()

    trees = list(alt_parse.possible_circuit_trees(select_grammar(args.grammar), args.depth))
    trees.sort(
        key=lambda tree: alt_parse.format_expression(
            alt_parse.number_parameters(tree)
        )
    )
    if args.max_candidates is not None:
        if args.max_candidates < 1:
            parser.error("--max-candidates must be at least 1")
        trees = trees[: args.max_candidates]

    package_text, manifest = render_package(trees)
    script_text = render_openmodelica_script(manifest)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    package_path = args.output_dir / "GeneratedEISCircuits.mo"
    script_path = args.output_dir / "check_candidates.mos"
    manifest_path = args.output_dir / "candidates.txt"

    package_path.write_text(package_text, encoding="utf-8")
    script_path.write_text(script_text, encoding="utf-8")
    manifest_path.write_text(
        "".join(f"{name}: {description}\n" for name, description in manifest),
        encoding="utf-8",
    )

    print(f"Generated {len(manifest)} Modelica candidate(s) in {args.output_dir}")
    print(f"Modelica package: {package_path}")
    print(f"OpenModelica script: {script_path}")
    print(f"Run: cd {args.output_dir}; omc check_candidates.mos")


if __name__ == "__main__":
    main()
