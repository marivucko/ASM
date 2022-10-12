import json
import math
import os
from operator import itemgetter

import pandas as pd
import networkx as nx
from datetime import datetime

from prettytable import prettytable

from src.analysis.helper_analysis.basic_analysis import get_subreddit_id_by_subreddit_name, _12, NetType, _14, _7, _8, \
    _9, _10, classify_data_in_n_classes_and_calculate_mixing_matrix, get_subreddit_name_by_subreddit_id
from src.analysis.helper_analysis.centrality_analysis import centrality_analysis, _18, _19, _16, _17, \
    read_from_user_net_centrality_txt, _19_user_net
from src.analysis.helper_analysis.detection_of_communes import detection_of_communes
from src.analysis.s_net_analysis import read_s_net_graph
import numpy as np


S_NET_T_FILE_PATH = '../../results/nets/s_net_t.gml'


def return_subreddits_from_commune(ids):
    nodes = []
    for i in range(0, len(ids)):
        s = get_subreddit_name_by_subreddit_id(ids[i])
        nodes.append(s)
    return nodes


def make_s_net_t_graph(s_net):
    subreddit_name_list = ['reddit.com', 'pics', 'worldnews', 'programming', 'business', 'politics', 'obama', 'science',
                           'technology', 'WTF', 'AskReddit', 'netsec', 'philosophy', 'videos', 'offbeat', 'funny',
                           'entertainment', 'linux', 'geek', 'gaming', 'comics', 'gadgets', 'nsfw', 'news',
                           'environment', 'atheism', 'canada', 'math', 'Economics', 'scifi', 'bestof', 'cogsci', 'joel',
                           'Health', 'guns', 'photography', 'software', 'history', 'ideas']
    subreddit_id_list = []
    for subreddit_name in subreddit_name_list:
        subreddit_id_from_subreddit_name = get_subreddit_id_by_subreddit_name(subreddit_name)
        if subreddit_id_from_subreddit_name is not None:
            subreddit_id_list.append(subreddit_id_from_subreddit_name)
    print(subreddit_id_list)
    s_net_t = s_net.subgraph(subreddit_id_list)
    nx.write_gml(s_net_t, S_NET_T_FILE_PATH)
    return s_net_t


def _25():
    s_net_t = read_s_net_t_graph()
    s_net_t_nodes_list = list(nx.nodes(s_net_t))
    s_net = read_s_net_graph()
    node_core_number_dictionary = nx.core_number(s_net)
    max_core_number = max(node_core_number_dictionary.values())
    for k in range(max_core_number, 0, -1):
        k_core = nx.k_core(s_net, k)
        l_core_nodes_list = list(nx.nodes(k_core))
        check = all(item in l_core_nodes_list for item in s_net_t_nodes_list)
        if check:
            print(f'Mreža SNetT je podgraf k-jezgra mreže SNet, gde je k {k}.')
            return


def read_s_net_t_graph():
    if os.path.isfile(S_NET_T_FILE_PATH):
        s_net_t = nx.read_gml(S_NET_T_FILE_PATH)
    else:
        s_net = read_s_net_graph()
        s_net_t = make_s_net_t_graph(s_net)
    return s_net_t


def print_commune(ids):
    s = '{'
    for i in range(0, len(ids)):
        s += get_subreddit_name_by_subreddit_id(ids[i])
        if i != len(ids) - 1:
            s += ', '
    ids, weights = zip(*(nx.get_edge_attributes(nx.subgraph(s_net_t, ids), 'weight').items()))
    weights = sorted(weights)
    print(s + '} ' + str(weights))


def get_5_communes():
    print_commune(['t5_2cneq', 't5_2qh13', 't5_2qgzg', 't5_2qh0f', 't5_6'])
    print_commune(['t5_2qh33', 't5_2qh61', 't5_2qh0u'])
    print_commune(['t5_2qh16', 't5_mouw', 't5_3b8o', 't5_2fwo'])
    print_commune(['t5_vf2', 't5_2qh03'])
    print_commune(['t5_2qhc8', 't5_2qgzt', 't5_2qh2a', 't5_2qh1n', 't5_2qh9z',
                   't5_2qh0k', 't5_2qh1a', 't5_2qh2p', 't5_1a8ah', 't5_2qh53',
                   't5_2qh3l', 't5_2qh1i', 't5_2qh1s', 't5_2qh19', 't5_2qh11',
                   't5_2qh5b', 't5_2qh2z', 't5_2qh8x', 't5_1rqwi', 't5_2qh0s',
                   't5_2qh68', 't5_2qh17', 't5_2qh3v', 't5_2qh0n', 't5_2qh1e'])


def get_18_communes():
    print_commune(['t5_2qh68', 't5_2qh1e'])
    print_commune(['t5_2qh5b', 't5_2qh03'])
    print_commune(['t5_2qh17', 't5_vf2'])
    print_commune(['t5_2qh9z', 't5_3b8o', 't5_6'])
    print_commune(['t5_2qh2z', 't5_2qh0s'])
    print_commune(['t5_2qh1a', 't5_2fwo'])
    print_commune(['t5_1a8ah', 't5_2qh0u'])
    print_commune(['t5_2qh11', 't5_2qh0f'])
    print_commune(['t5_2qh1s', 't5_2qgzg'])
    print_commune(['t5_2qh1i', 't5_2qh61'])
    print_commune(['t5_2qh3l', 't5_2qh33'])
    print_commune(['t5_2qh53', 't5_2qh13', 't5_2qh8x'])
    print_commune(['t5_2qh2p', 't5_2cneq'])
    print_commune(['t5_2qh0k', 't5_mouw'])
    print_commune(['t5_2qh1n', 't5_2qh0n'])
    print_commune(['t5_2qhc8', 't5_2qh2a'])
    print_commune(['t5_2qgzt', 't5_1rqwi'])
    print_commune(['t5_2qh16', 't5_2qh19', 't5_2qh3v'])


def get_2_communes():
    print_commune(['t5_2qh16', 't5_mouw', 't5_2cneq', 't5_2qh13', 't5_2qh33', 't5_2qh61', 't5_2qgzg', 't5_2qh0f', 't5_2qh0u', 't5_2fwo', 't5_6'])
    print_commune(['t5_3b8o', 't5_vf2', 't5_2qh03', 't5_2qhc8', 't5_2qgzt', 't5_2qh2a', 't5_2qh1n', 't5_2qh9z',
                   't5_2qh0k', 't5_2qh1a', 't5_2qh2p', 't5_1a8ah', 't5_2qh53', 't5_2qh3l', 't5_2qh1i', 't5_2qh1s',
                   't5_2qh19', 't5_2qh11', 't5_2qh5b', 't5_2qh2z', 't5_2qh8x', 't5_1rqwi', 't5_2qh0s',
                   't5_2qh68', 't5_2qh17', 't5_2qh3v', 't5_2qh0n', 't5_2qh1e'])


def s_net_t_analysis():
    s_net_t = read_s_net_t_graph()
    s_net = read_s_net_graph()
    k_core = nx.k_core(s_net, 192)
    l_core_nodes_list = list(nx.nodes(k_core))
    print(l_core_nodes_list)
    # get_2_communes()


s_net_t = read_s_net_t_graph()
s_net = read_s_net_graph()
k_core = nx.k_core(s_net, 192)
l_core_nodes_list = list(nx.nodes(k_core))
print(return_subreddits_from_commune(l_core_nodes_list))