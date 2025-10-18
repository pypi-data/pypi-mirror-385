from . import drawing

def render(out, named_tensors, filename, cull = [], draw_fn = drawing.draw_all, fmt = 'pdf', **draw_kwargs):
    G = None
    if 'torch' in str(type(out)):
        from .make_graph import traverse_torch
        G = traverse_torch(out, named_tensors)
    else:
        print('Unsupported type. Supported AG libraries: [pytorch, ]')

    if G is None:
        raise Exception('Failed to produce networkx graph from autograd data. See errors above.')

    if len(cull) > 0:
        from .graph_modifiers import remove_nodes
        G = remove_nodes(G, cull)

#    if color_special:
#        from .graph_modifiers import color_edges_on_any_path
#        sources = [n for n, attr in G.nodes(data=True) if attr['group'] == 'param']
#        targets = [n for n, attr in G.nodes(data=True) if attr['group'] == 'state']
#        G = color_edges_on_any_path(G, sources, targets)

    dot = draw_fn(G, **draw_kwargs)
    dot.format = fmt 
    dot.render(filename, cleanup=True)
