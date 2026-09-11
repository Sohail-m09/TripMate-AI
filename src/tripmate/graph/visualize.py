from tripmate.graph.builder import (
    compile_travel_graph,
)


def main() -> None:

    graph = compile_travel_graph()

    mermaid_graph = (
        graph.get_graph().draw_mermaid()
    )

    print(mermaid_graph)


if __name__ == "__main__":
    main()