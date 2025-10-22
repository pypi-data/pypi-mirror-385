from functools import partial

from kimina_client import KiminaClient
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send

from goedels_poetry.agents.state import DecomposedFormalTheoremState, DecomposedFormalTheoremStates
from goedels_poetry.agents.util.common import add_default_imports, remove_default_imports_from_ast
from goedels_poetry.agents.util.debug import log_kimina_response
from goedels_poetry.agents.util.kimina_server import parse_kimina_ast_code_response
from goedels_poetry.parsers.ast import AST


class SketchParserAgentFactory:
    """
    Factory class for creating instances of the SketchParserAgent.
    """

    @staticmethod
    def create_agent(server_url: str, server_max_retries: int) -> CompiledStateGraph:
        """
        Creates a SketchParserAgent instance that employs the server at the passed URL.

        Parameters
        ----------
        server_url: str
            The URL of the Kimina server.
        server_max_retries: int
            The maximum number of retries for the Kimina server.

        Returns
        -------
        CompiledStateGraph
            An CompiledStateGraph instance of the sketch parser agent.
        """
        return _build_agent(server_url=server_url, server_max_retries=server_max_retries)


def _build_agent(server_url: str, server_max_retries: int) -> CompiledStateGraph:
    """
    Builds a compiled state graph for the specified Kimina server.

    Parameters
    ----------
    server_url: str
        The URL of the Kimina server.
    server_max_retries: int
        The maximum number of retries for the Kimina server.

    Returns
    -------
    CompiledStateGraph
        The compiled state graph for the sketch parser agent.
    """
    # Create the sketch parser agent state graph
    graph_builder = StateGraph(DecomposedFormalTheoremStates)

    # Bind the server related arguments of _parse_sketch
    bound_parse_sketch = partial(_parse_sketch, server_url, server_max_retries)

    # Add the nodes
    graph_builder.add_node("parser_agent", bound_parse_sketch)

    # Add the edges
    graph_builder.add_conditional_edges(START, _map_edge, ["parser_agent"])
    graph_builder.add_edge("parser_agent", END)

    return graph_builder.compile()


def _map_edge(states: DecomposedFormalTheoremStates) -> list[Send]:
    """
    Map edge that takes the members of the states["inputs"] list and dispers them to the
    parser_agent nodes.

    Parameters
    ----------
    states: DecomposedFormalTheoremStates
        The DecomposedFormalTheoremStates containing in the "inputs" member the
        DecomposedFormalTheoremState instances to parse the proof sketches of.

    Returns
    -------
    list[Send]
        List of Send objects each indicating the their target node and its input, singular.
    """
    return [Send("parser_agent", state) for state in states["inputs"]]


def _parse_sketch(
    server_url: str, server_max_retries: int, state: DecomposedFormalTheoremState
) -> DecomposedFormalTheoremStates:
    """
    Parses the proof sketch in the passed DecomposedFormalTheoremState.

    Parameters
    ----------
    server_url: str
        The URL of the server.
    server_max_retries: int
        The maximum number of retries for the server.
    state: DecomposedFormalTheoremState
        The decomposed formal theorem proof state with the formal proof sketch to be parsed.

    Returns
    -------
    DecomposedFormalTheoremStates
        A DecomposedFormalTheoremStates with the DecomposedFormalTheoremState with the parsed proof
        sketch added to the DecomposedFormalTheoremStates "outputs" member.
    """
    # Create a client to access the Kimina Server
    kimina_client = KiminaClient(api_url=server_url, http_timeout=36000, n_retries=server_max_retries)

    # Parse formal proof sketch of the passed state with DEFAULT_IMPORTS prefix
    sketch_with_imports = add_default_imports(str(state["proof_sketch"]))
    ast_code_response = kimina_client.ast_code(sketch_with_imports)

    # Parse ast_code_response
    parsed_response = parse_kimina_ast_code_response(ast_code_response)

    # Log debug response
    log_kimina_response("ast_code", parsed_response)

    # Remove DEFAULT_IMPORTS from the parsed AST
    ast_without_imports = remove_default_imports_from_ast(parsed_response["ast"])

    # Set state["ast"] with the parsed_response (without DEFAULT_IMPORTS)
    state["ast"] = AST(ast_without_imports)

    # Return a DecomposedFormalTheoremStates with state added to its outputs
    return {"outputs": [state]}  # type: ignore[typeddict-item]
