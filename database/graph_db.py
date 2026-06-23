# database/graph_db.py
import networkx as nx


def build_org_chart_graph():
    """
    Builds a directed Knowledge Graph of employees, skills, and departments.
    """
    print("🕸️ Initializing Company Org Chart Graph...")
    G = nx.DiGraph()

    # Entities with Metadata
    employees = [
        ("Sarah", "sarah@acme.com"),
        ("David", "david@acme.com"),
        ("Aisha", "aisha@acme.com"),
    ]
    skills = ["Rust", "Python", "React", "Cloud Architecture"]
    departments = ["Backend", "Frontend", "DevOps"]

    # Add Nodes (Now with email attributes)
    for name, email in employees:
        G.add_node(name, type="Employee", email=email)
    for skill in skills:
        G.add_node(skill, type="Skill")
    for dept in departments:
        G.add_node(dept, type="Department")

    # Add Relationships (Edges)
    relationships = [
        ("Sarah", "KNOWS", "Rust"),
        ("Sarah", "KNOWS", "Python"),
        ("Sarah", "WORKS_IN", "Backend"),
        ("David", "KNOWS", "React"),
        ("David", "WORKS_IN", "Frontend"),
        ("Aisha", "KNOWS", "Cloud Architecture"),
        ("Aisha", "KNOWS", "Python"),
        ("Aisha", "WORKS_IN", "DevOps"),
    ]

    for source, rel, target in relationships:
        G.add_edge(source, target, relation=rel)

    return G


org_graph = build_org_chart_graph()
