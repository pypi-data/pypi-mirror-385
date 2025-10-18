# Convert autograd tree to a generic network with metadata for nodes/edges.
# I chose to use networkx for the "generic network" model instead of building it 
# by hand since it supports things like removing nodes, finding paths, etc.
# autograd tree can be specified in common languages like Jax, Pytorch, etc.
# SUPPORT NOW: only pytorch. 

from networkx import DiGraph

def traverse_torch(out, named_tensors):
    # Traverse the pytorch AD tree and create a graph.
    # Nodes have meta data, including:
    # - id: a raw identifier for the node.
    # - label: visible name to use when visualizing.
    # - group: one of 'state', 'param', 'none' or 'func'. none represents leaves that are not specified by user or stored tensors for functions.
    #
    # named_tensors should be a dict with entries like 'state_10': (tensor, 'state') specifying maps from names to tuple of tensor and group (one of 'state' or 'param')
    
    G = DiGraph()
    tensor_name = {id(t): name for name, (t, _) in named_tensors.items()}

    new_node = lambda x, label, group: G.add_node(str(id(x)), label=label, group=group)
    new_edge = lambda x1, x2: G.add_edge(str(id(x1)), str(id(x2)))

    # Add explicit nodes for all named tensors that the user specified.
    for name, (t, group) in named_tensors.items():
        new_node(t, f"{name}\n{tuple(t.shape)}", group)

    seen = set()
    def dfs_call(fn): # Recursively called to traverse tree (Depth-First-Search)
        if fn is None or fn in seen:
            return
        seen.add(fn)

        new_node(fn, type(fn).__name__, 'func')

        # Connect saved tensors (optional, dashed)
        for t in getattr(fn, "saved_tensors", []):
            if id(t) not in tensor_name:
                new_node(t, f"saved{tuple(t.shape)}", 'none')
            new_edge(t, fn)

        # Upstream edges
        for nxt, _ in getattr(fn, "next_functions", []):
            if nxt is None:
                continue
            if hasattr(nxt, "variable"):  # AccumulateGrad for a leaf variable
                v = nxt.variable
                # ensure the leaf shows up (named if we have it)
                if id(v) not in tensor_name:
                    new_node(v, f"leaf{tuple(v.shape)}", 'none')
                new_edge(v, fn)
            else:
                new_edge(nxt, fn)
                dfs_call(nxt)

    dfs_call(out.grad_fn)

    # Also connect each named non-leaf tensor to its producing function so labels are obvious
    for (t, _) in named_tensors.values():
        if t.grad_fn is not None:
            new_edge(t.grad_fn, t)

    return G
