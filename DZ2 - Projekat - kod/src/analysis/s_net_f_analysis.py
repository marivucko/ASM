import math
import networkx as nx
import pandas as pd
from datetime import datetime
from os.path import exists
import os
import collections

from src.analysis.helper_analysis.basic_analysis import basic_characterization_of_modeled_networks, \
    read_user_net_erdos_renyi_graph, read_s_net_f_giant_component_graph, _14, _7, _8, _9, _10, \
    are_nodes_with_high_lcc_connected, classify_data_in_n_classes_and_calculate_mixing_matrix, _12, _15
from src.analysis.helper_analysis.centrality_analysis import _19, _18, _16, _17
from src.analysis.helper_analysis.detection_of_communes import detection_of_communes
from src.analysis.net_analysis import NetType, net_analysis
from src.analysis.s_net_analysis import read_s_net_graph
from src.analysis.statistical_analysis import read_submissions_and_comments
import matplotlib.pyplot as plt
from collections import Counter


S_NET_F_FILE_PATH = '../../results/nets/s_net_f.gml'


def plot_edge_weight_distribution_and_find_w_threshold(graph):
    edges, weights = zip(*nx.get_edge_attributes(graph, 'weight').items())
    weight_counts = Counter(weights)
    x, y = zip(*weight_counts.items())
    plt.xlabel('Težina grane')
    plt.ylabel('Broj pojavljivanja')
    plt.title('Raspodela težina grana')
    plt.figure(1)
    plt.scatter(x, y, marker='.')
    plt.show()
    num_of_edges = graph.number_of_edges()
    weight_counts = collections.OrderedDict(sorted(weight_counts.items(), reverse=True))
    print('Broj grana SNet mreže:', num_of_edges)
    sum_of_weights = 0
    w_threshold = 1
    print('Težine grana SNet mreže date su kao niz gde je prvi član predstavlja težinu grane, a drugi broj grana koje su te težine:', str(weight_counts).split("OrderedDict", 1)[1][1:-1]) # substring od ovoga OrderedDict([(1.0, 31), (0.5, 25955), (0.25, 21584), (0.125, 19737), (0.0625, 21454), (0.03125, 12610), (0.015625, 13543), (0.0078125, 12255), (0.00390625, 8593), (0.001953125, 7150), (0.0009765625, 9006), (0.00048828125, 2990), (0.000244140625, 2058)])
    for item in weight_counts:
        if sum_of_weights + weight_counts[item] <= 0.2 * num_of_edges:
            sum_of_weights = sum_of_weights + weight_counts[item]
            w_threshold = item
        else:
            return w_threshold
        print(item, weight_counts[item])


def make_s_net_f_graph(s_net):
    w_threshold = plot_edge_weight_distribution_and_find_w_threshold(s_net)
    G = nx.Graph(((source, target, attr) for source, target, attr in s_net.edges(data=True) if attr['weight'] >= w_threshold))
    print(nx.info(G))
    print(f'SNetF mreža je modelovana od SNet mreže tako što je odabran w_threshold vrednosti { w_threshold }. Biće odbačene sve grane čija je težina ispod te vrednost. W_threshold je odabran tako da grane koje preostanu čine do 20% ukupnog broja grana SNet mreže. ')
    nx.write_gml(G, S_NET_F_FILE_PATH)
    return G


def read_s_net_f_graph():
    if os.path.isfile(S_NET_F_FILE_PATH):
        s_net_f = nx.read_gml(S_NET_F_FILE_PATH)
    else:
        s_net = read_s_net_graph()
        s_net_f = make_s_net_f_graph(s_net)
    return s_net_f


def s_net_f_analysis():
    # print('1')
    # read_user_net_erdos_renyi_graph()
    # print('2')
    # n = 97532
    # m = 2895955
    # H = nx.erdos_renyi_graph(n, 2 * float(m) / (n * (n - 1)))
    s_net_f = read_s_net_f_graph()
    # _7(s_net_f, NetType.S_NET_F.value)
    # _8(s_net_f, NetType.S_NET_F.value)
    # _9(s_net_f, NetType.S_NET_F.value)
    print(f'Za SNetF mrežu se nadalje ispituje njena gigantska komponenta.')
    s_net_f = read_s_net_f_giant_component_graph(s_net_f)
    # _10(s_net_f, NetType.S_NET_F.value)
    # are_nodes_with_high_lcc_connected(s_net_f)
    # classify_data_in_n_classes_and_calculate_mixing_matrix(s_net_f, 9) # liniju 10 funckije zakomentarisati, a otkomentarisati 11
    # _12(s_net_f, NetType.S_NET_F.value, 6)
    # classify_data_in_n_classes_and_calculate_mixing_matrix(s_net_f, 6)
    # _14(s_net_f)
    # _16(s_net_f, NetType.S_NET_F.value)
    # _17(s_net_f, NetType.S_NET_F.value)
    # _18(s_net_f, NetType.S_NET_F.value)
    # _19(s_net_f, NetType.S_NET_F.value)
    detection_of_communes(s_net_f, NetType.S_NET_F.value)


# s_net_f_analysis()
print('1')
user_net = nx.read_gml('../../results/nets/giant_component/user_net_giant_component.gml')
# s_net = nx.read_gml('../../results/nets/giant_component/s_net_giant_component.gml')
# s_net_f = nx.read_gml('../../results/nets/giant_component/s_net_f_giant_component.gml')
print('2 gigantska komponenta')
_14(user_net)
# _14(user_net)