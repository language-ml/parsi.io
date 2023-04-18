# Importing required libraries
import networkx as nx
import arabic_reshaper
import matplotlib.pyplot as plt
from bidi.algorithm import get_display


def plot_graph(input_dict):
    text_dict = input_dict.copy()
    nodes = sorted(text_dict.keys())
    pre = None
    edges = []
    pre_same = []
    for node in nodes:
        if pre == None:
            pre = node
        elif '_' in node:
            edges.append((pre, node))
            pre_same.append(node)
        elif node == 'goal':
            edges.append((pre, node))
            break
        elif '_' not in node:
            edges.append((pre, node))
            pre = node
        else:
            for nd in pre_same:
                edges.append((nd, node))
            pre = node
            pre_same = []

    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    coord = nx.spring_layout(graph)
    for key in text_dict:
        text_dict[key] = get_display(arabic_reshaper.reshape(text_dict[key]))

    node_label_coords = {}
    for node, coords in coord.items():
        node_label_coords[node] = (coords[0], coords[1] + 0.04)

    fig = plt.figure(figsize=(9, 9))
    nodes_g = nx.draw_networkx_nodes(graph, pos=coord)
    edges_g = nx.draw_networkx_edges(graph, pos=coord)
    edge_labels = nx.draw_networkx_edge_labels(graph, pos=coord)
    node_labels = nx.draw_networkx_labels(
        graph, pos=node_label_coords, labels=text_dict, font_family='sans-serif')
    return fig
