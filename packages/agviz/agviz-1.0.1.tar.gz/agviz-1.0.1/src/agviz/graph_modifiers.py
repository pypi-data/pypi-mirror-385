import networkx as nx

def remove_nodes(G, group):
    # merge all nodes of a certain group type in graph. group can be a single group or a list of groups.
    if isinstance(group, str):
        group = [group]

    def remove_node_and_keep_edges(node):
        preds = list(G.predecessors(node))
        succs = list(G.successors(node))
        for u in preds:
            for v in succs:
                if u != v:
                    G.add_edge(u, v)

    rm_list = []
    for node, attrs in G.nodes(data=True):
        if attrs['group'] in group:
            remove_node_and_keep_edges(node)
            rm_list.append(node)

    G.remove_nodes_from(rm_list)
    return G


def color_edges_on_any_path(G, sources, targets, color="red"):
    """
    Color all edges that lie on at least one path from any node in `sources`
    to any node in `targets` with edge attribute {'color': color}.
    Works for DiGraph and MultiDiGraph.
    """
    # Normalize inputs
    sources = [s for s in sources if s in G]
    targets = [t for t in targets if t in G]
    if not sources or not targets:
        return G  # nothing to do

    # 1) Forward reachability from sources
    forward = set()
    for s in sources:
        forward.add(s)
        forward |= nx.descendants(G, s)

    # 2) Backward reachability to targets (i.e., descendants in the reversed graph)
    R = G.reverse(copy=False)
    backward = set()
    for t in targets:
        backward.add(t)
        backward |= nx.descendants(R, t)

    # 3) Color every edge whose tail is forward-reachable and head can reach a target
    for u, v, data in G.edges(data=True):
        if u in forward and v in backward:
            data["color"] = color

    return G
