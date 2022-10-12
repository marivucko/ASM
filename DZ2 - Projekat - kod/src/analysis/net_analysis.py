import os

import networkx as nx

from src.analysis.helper_analysis.basic_analysis import basic_characterization_of_modeled_networks, NetType, \
    read_s_net_giant_component_graph
from src.analysis.helper_analysis.centrality_analysis import centrality_analysis
from src.analysis.helper_analysis.detection_of_communes import detection_of_communes


def net_analysis(graph, net_type_value):
    # basic_characterization_of_modeled_networks(graph, net_type_value)
    centrality_analysis(graph, net_type_value)
    # detection_of_communes(graph, net_type_value)
    print('aa')
