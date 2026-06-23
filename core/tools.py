# core/tools.py
import networkx as nx
from database.vector_db import vector_collection
from database.graph_db import org_graph


def search_company_documents(query: str) -> str:
    """
    Searches the Vector Database for company policies and technical standards.
    """
    print(f"   [TOOL EXECUTION] Searching company documents for: '{query}'...")
    try:
        results = vector_collection.query(
            query_texts=[query], n_results=2  # Get top 2 most relevant paragraphs
        )
        if results["documents"] and results["documents"][0]:
            retrieved_docs = results["documents"][0]
            return "\n\n".join(retrieved_docs)
        return "No relevant documents found."
    except Exception as e:
        return f"Error searching documents: {str(e)}"


def search_org_chart(target_entity: str) -> str:
    """
    Searches the Directed Graph Database to find relationships between employees, skills, and departments.
    """
    print(f"   [TOOL EXECUTION] Traversing org chart for: '{target_entity}'...")
    if target_entity not in org_graph:
        return f"Entity '{target_entity}' not found in the org chart."

    try:
        undirected_G = org_graph.to_undirected()
        relevant_nodes = list(
            nx.single_source_shortest_path_length(
                undirected_G, target_entity, cutoff=2
            ).keys()
        )
        subgraph = org_graph.subgraph(relevant_nodes)

        context = []

        # EXTRACT NODE METADATA (Like Emails)
        for node, data in subgraph.nodes(data=True):
            if data.get("type") == "Employee" and "email" in data:
                context.append(f"[INFO] {node}'s email is {data['email']}")

        # EXTRACT RELATIONSHIPS
        for source, target, data in subgraph.edges(data=True):
            rel = data["relation"]
            context.append(f"- {source} {rel} {target}")

        return "\n".join(sorted(list(set(context))))
    except Exception as e:
        return f"Error traversing graph: {str(e)}"


# The schema definition that tells the LLM how to use these tools
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_company_documents",
            "description": "Use this tool to look up company policies, coding standards, and handbook information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query, e.g., 'PTO policy' or 'Rust standards'",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_org_chart",
            "description": "Use this tool to find employees, their skills, or what department they work in.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_entity": {
                        "type": "string",
                        "description": "The exact name of a skill (e.g., 'Rust', 'Python') or employee (e.g., 'Sarah').",
                    }
                },
                "required": ["target_entity"],
            },
        },
    },
]
