import os
from .graph import DependencyGraph
from .edge import DependencyEdge
from .node import DependencyNode


def print_orphan(graph: DependencyGraph):
    orphans = []
    for node in graph.nodes.values():
        node: DependencyNode
        if node.is_orphan:
            orphans.append(node)

    orphans.sort(key=lambda n: n.path.lower())
    if orphans:
        print("🧩 Orphan DLLs:")
        for node in orphans:
            print(f"  🧩 {os.path.basename(node.path)}")
    else:
        print("🧩 No orphan DLLs.")


def print_missing(graph: DependencyGraph):
    missing = []
    for edge in graph.edges.values():
        edge: DependencyEdge
        if edge.is_missing:
            missing.append(edge.child)

    missing.sort(key=lambda x: x.path.lower())
    if not missing:
        print("✅ No missing dependencies.")
        return
    print("❌ Missing dependencies:")
    for node in missing:
        print(f"  ❌ {os.path.basename(node.path)}")
        for p in getattr(graph, "parents", {}).get(node, []):
            print(f"    ↳ Required by: {os.path.basename(p.path)}")


def print_invalid(graph: DependencyGraph):
    invalid = []
    for edge in graph.edges.values():
        edge: DependencyEdge
        if edge.is_valid is False and edge.is_missing is False:
            invalid.append(edge)

    if not invalid:
        print("✅ No invalid files.")
        return
    print("❗ Invalid files (failed to parse):")
    for edge in invalid:
        edge: DependencyEdge
        parent_name = os.path.basename(edge.parent.path)
        child_name = os.path.basename(edge.child.path)
        print(f"  ❗ {parent_name} -> {child_name}")
