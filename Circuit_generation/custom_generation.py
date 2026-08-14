"""Generate circuit topologies with a strict element-count limit."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations_with_replacement, product

if __package__:
    from .circuit_class import (
        CPE,
        CircuitNode,
        Element,
        Gerischer,
        Inductor,
        Parallel,
        Resistor,
        Series,
        SeriesResistance,
        Warburg,
    )
    from .circuit_from_grammar import (
        add_indexes,
        circuit_sort_key,
        normalize,
        simplify,
    )
else:
    # Allows this file to be executed directly.
    from circuit_class import (
        CPE,
        CircuitNode,
        Element,
        Gerischer,
        Inductor,
        Parallel,
        Resistor,
        Series,
        SeriesResistance,
        Warburg,
    )
    from circuit_from_grammar import add_indexes, circuit_sort_key, normalize, simplify


# These aliases make the later type hints easier to read.
ElementType = type[Element]
ConnectionType = type[Series] | type[Parallel]
NetworkBuckets = dict[int, set[CircuitNode]]


def grammar_base_networks(grammar_name: str) -> tuple[CircuitNode, ...]:
    """Return the primitive networks allowed by one of the active grammars.

    Compact grammars use complete motifs as their primitive network choices.
    The generator may connect those motifs, but it does not invent primitive
    elements that the grammar does not permit on their own.
    """
    randles = Parallel((CPE(), Series((Resistor(), Warburg()))))
    zarc = Parallel((CPE(), Resistor()))

    grammar_networks = {
        "relaxed": (
            Resistor(),
            CPE(),
            Warburg(),
            Inductor(),
            Gerischer(),
        ),
        "compact_hybrid": (
            randles,
            zarc,
            Inductor(),
            Warburg(),
        ),
        "compact_only_blocks": (
            randles,
            zarc,
            Series((Resistor(), Warburg())),
            Series((Resistor(), Inductor())),
        ),
    }

    try:
        return grammar_networks[grammar_name]
    except KeyError as error:
        choices = ", ".join(sorted(grammar_networks))
        raise ValueError(
            f"Unknown bounded-generation grammar {grammar_name!r}; "
            f"choose from {choices}"
        ) from error


@dataclass(frozen=True)
class GeneratorConfig:
    """Settings controlling which circuits may be generated."""

    # Maximum number of physical elements in the complete circuit.
    #
    # The mandatory series resistance Rs is included in this number.
    # For example:
    #
    #   max_elements = 1  -> Rs
    #   max_elements = 2  -> Rs plus one network element
    #   max_elements = 4  -> Rs plus at most three network elements
    max_elements: int

    # Element classes that may appear after Rs.
    #
    # These are classes rather than instances because the generator creates
    # fresh, unnumbered objects while constructing candidate topologies.
    element_types: tuple[ElementType, ...] = (
        Resistor,
        CPE,
        Warburg,
        Inductor,
        Gerischer,
    )

    # Connection classes that the generator may use when joining two networks.
    connection_types: tuple[ConnectionType, ...] = (
        Series,
        Parallel,
    )

    # Optional complete network motifs used as the generator's starting
    # points. This is how compact grammars keep blocks such as Zarc and
    # Randles intact during initial generation.
    base_networks: tuple[CircuitNode, ...] | None = None

    # Metadata only; it does not change generation after base_networks have
    # been selected.
    grammar_name: str | None = None

    @classmethod
    def for_grammar(
        cls,
        max_elements: int,
        grammar_name: str,
    ) -> "GeneratorConfig":
        """Create a bounded configuration matching an existing grammar."""
        return cls(
            max_elements=max_elements,
            element_types=(),
            base_networks=grammar_base_networks(grammar_name),
            grammar_name=grammar_name,
        )

    def __post_init__(self) -> None:
        """Reject configurations that cannot generate valid circuits."""

        # At least one slot is required for the mandatory Rs.
        if self.max_elements < 1:
            raise ValueError("max_elements must be at least 1")

        if not self.element_types and not self.base_networks:
            raise ValueError("element_types or base_networks must be provided")

        if not self.connection_types:
            raise ValueError("connection_types cannot be empty")


class LimitedCircuitGenerator:
    """Generate normalized circuits without exceeding an element limit."""

    def __init__(self, config: GeneratorConfig) -> None:
        self.config = config

    def generate(self) -> set[CircuitNode]:
        """Generate all accepted circuit topologies up to the size limit."""

        return {add_indexes(circuit) for circuit in self.generate_unnumbered()}

    def generate_unnumbered(self) -> set[CircuitNode]:
        """Generate normalized topologies while preserving shared subtrees."""

        # Rs by itself is always the smallest valid circuit.
        #
        # We first work with unnumbered elements such as R, CPE, and W.
        # Parameter indices are assigned only after generation is finished.
        circuits: set[CircuitNode] = {SeriesResistance()}

        # Dynamic-programming storage:
        #
        #   networks_by_size[1] contains one-element networks
        #   networks_by_size[2] contains two-element networks
        #   networks_by_size[3] contains three-element networks
        #
        # Larger networks can therefore be assembled from smaller networks
        # that have already been generated.
        networks_by_size: NetworkBuckets = {}

        # One position in the complete circuit is reserved for Rs.
        #
        # If max_elements is 4, the generated network after Rs may therefore
        # contain at most 3 elements.
        maximum_network_size = self.config.max_elements - 1

        # Seed the size buckets with either primitive element instances or
        # complete motifs supplied by a compact grammar.
        node_sizes: dict[int, int] = {}

        for base_network in self._build_base_networks():
            normalized_network = normalize(base_network)
            size = self.count_elements(normalized_network)
            _record_node_sizes(normalized_network, node_sizes)
            if size <= maximum_network_size:
                networks_by_size.setdefault(size, set()).add(normalized_network)

        for network_size in range(1, maximum_network_size + 1):
            networks = self._build_networks_with_exact_size(
                size=network_size,
                networks_by_size=networks_by_size,
                node_sizes=node_sizes,
            )

            # Store this bucket so that it can be reused to construct larger
            # networks during later iterations.
            networks_by_size[network_size] = networks

            for network in networks:
                complete_circuit = self._attach_series_resistance(network)

                if self._is_allowed(complete_circuit):
                    circuits.add(complete_circuit)

        return circuits

    def _build_networks_with_exact_size(
        self,
        size: int,
        networks_by_size: NetworkBuckets,
        node_sizes: dict[int, int],
    ) -> set[CircuitNode]:
        """Build normalized network fragments with exactly `size` elements."""

        # A bucket may already contain primitive elements or compact motifs.
        candidates = set(networks_by_size.get(size, set()))

        # Construct a network of the requested size by splitting its elements
        # between a left and a right branch.
        #
        # Example for size = 4:
        #
        #   left size 1 + right size 3
        #   left size 2 + right size 2
        #   left size 3 + right size 1
        #
        # Repeating this process allows networks of arbitrary nested shape to
        # be constructed from the same Series and Parallel circuit classes.
        # Series and Parallel are commutative after normalization. Only visit
        # each unordered size split and network pair once.
        for left_size in range(1, size // 2 + 1):
            right_size = size - left_size

            left_networks = networks_by_size.get(left_size, set())
            right_networks = networks_by_size.get(right_size, set())

            if left_size == right_size:
                network_pairs = combinations_with_replacement(left_networks, 2)
            else:
                network_pairs = product(left_networks, right_networks)

            for left, right in network_pairs:
                candidates.update(
                    self._connect_networks(
                        left=left,
                            right=right,
                            expected_size=size,
                            node_sizes=node_sizes,
                    )
                )

        return candidates

    def _build_base_networks(self) -> set[CircuitNode]:
        """Create the unnumbered elements or motifs that seed generation."""
        if self.config.base_networks is not None:
            return set(self.config.base_networks)

        return {element_type() for element_type in self.config.element_types}

    def _connect_networks(
        self,
        left: CircuitNode,
        right: CircuitNode,
        expected_size: int,
        node_sizes: dict[int, int],
    ) -> set[CircuitNode]:
        """Join two networks using every allowed connection type."""

        connected_networks: set[CircuitNode] = set()

        for connection_type in self.config.connection_types:
            # Examples:
            #
            #   Series((left, right))
            #   Parallel((left, right))
            # Both inputs are already normalized. Combining only their roots
            # preserves shared subtrees, which greatly reduces memory use for
            # large generation runs. The result is equivalent to calling the
            # existing recursive normalize() function on the complete tree.
            candidate = _connect_normalized(connection_type, left, right)

            # Canonicalization performs the same operations as the existing
            # normalizer. Among other things, it:
            #
            # - flattens nested connections of the same type;
            # - sorts children deterministically;
            # - removes certain redundant R and L elements.
            # Normalization can reduce the number of elements. Consequently,
            # an object assembled from three elements might normalize into a
            # two-element network.
            #
            # Keep it in this bucket only if its final size is still correct.
            candidate_children = (
                candidate.children
                if not isinstance(candidate, Element)
                else (candidate,)
            )
            candidate_size = sum(node_sizes[id(child)] for child in candidate_children)
            node_sizes[id(candidate)] = candidate_size

            if candidate_size == expected_size:
                connected_networks.add(candidate)

        return connected_networks

    @staticmethod
    def _attach_series_resistance(network: CircuitNode) -> CircuitNode:
        """Place the generated network after the mandatory Rs."""
        return _connect_normalized(Series, SeriesResistance(), network)

    def _is_allowed(self, circuit: CircuitNode) -> bool:
        """Apply final constraints to a complete circuit."""

        # Later, additional custom rules can be added here, such as:
        #
        # - allow at most one Warburg element;
        # - require at least one CPE;
        # - disallow inductors inside parallel connections;
        # - limit the number of parallel branches.
        return self.count_elements(circuit) <= self.config.max_elements

    @staticmethod
    def count_elements(node: CircuitNode) -> int:
        """Count physical elements recursively.

        Series and Parallel objects describe connections, so they are not
        counted as elements.
        """

        # Every primitive component, including SeriesResistance, contributes
        # exactly one to the element count.
        if isinstance(node, Element):
            return 1

        # A connection's element count is the total count of all its children.
        return sum(
            LimitedCircuitGenerator.count_elements(child)
            for child in node.children
        )


def _connect_normalized(
    connection_type: ConnectionType,
    left: CircuitNode,
    right: CircuitNode,
) -> CircuitNode:
    """Connect normalized nodes without rebuilding their complete subtrees."""
    children: list[CircuitNode] = []

    for child in (left, right):
        if type(child) is connection_type:
            children.extend(child.children)  # type: ignore[attr-defined]
        else:
            children.append(child)

    children = simplify(connection_type, children)
    children.sort(key=circuit_sort_key)

    if len(children) == 1:
        return children[0]

    return connection_type(tuple(children))


def _record_node_sizes(node: CircuitNode, node_sizes: dict[int, int]) -> int:
    """Record element counts for a seed motif and all of its descendants."""
    if isinstance(node, Element):
        size = 1
    else:
        size = sum(_record_node_sizes(child, node_sizes) for child in node.children)

    node_sizes[id(node)] = size
    return size


if __name__ == "__main__":
    # Generate circuits containing no more than n physical elements.
    config = GeneratorConfig(max_elements=7)
    generator = LimitedCircuitGenerator(config)

    circuits = generator.generate()

    print(f"Generated {len(circuits)} circuits:\n")

    # Sorting by the string representation makes printed output deterministic.
    #for circuit in sorted(circuits, key=str):
    #    element_count = generator.count_elements(circuit)
    #    print(f"{element_count} elements: {circuit}")
