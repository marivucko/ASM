import math
from operator import itemgetter
import networkx as nx
import pandas as pd
from prettytable import prettytable
from src.analysis.helper_analysis.basic_analysis import NetType, _15
from networkx.algorithms.community import asyn_lpa_communities, label_propagation_communities, girvan_newman, modularity

PATH_TO_COMMUNES = "../../../input_data/communes_from_gephi"
SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH = '../../../results/output_data_cleaned/subreddit_id__subreddit_dictionary'
S_NET_GIANT_COMPONENT_FILE_PATH = '../../../results/nets/giant_component/s_net_giant_component.gml'
S_NET_F_GIANT_COMPONENT_FILE_PATH = '../../../results/nets/giant_component/s_net_f_giant_component.gml'


def get_subreddit_name_by_subreddit_id(subreddit_id):
    subreddit_id__subreddit_dictionary = pd.read_pickle(SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH)
    if subreddit_id in subreddit_id__subreddit_dictionary:
        return subreddit_id__subreddit_dictionary[subreddit_id]
    else:
        return 'There is no subreddit with this id in the whole of 2008.'


def from_s_net_type_value_to_path_format(net_type_value):
    if net_type_value == NetType.S_NET.value:
        return 's_net'
    elif net_type_value == NetType.S_NET_F.value:
        return 's_net_f'
    elif net_type_value == NetType.S_NET_T.value:
        return 's_net_t'
    else:
        return 'user_net'


def print_commune(ids, graph):
    s = '{'
    for i in range(0, len(ids)):
        s += get_subreddit_name_by_subreddit_id(ids[i])
        if i != len(ids) - 1:
            s += ', '
    if len(ids) > 1:
        ids_, weights = zip(*(nx.get_edge_attributes(nx.subgraph(graph, ids), 'weight').items()))
        weights = sorted(weights)
        print(s + '}\n' + str(weights))
    else:
        print(s)


def print_commune_and_number_of_edges(ids, graph):
    s = '{'
    n = len(ids)
    for i in range(0, n):
        s += get_subreddit_name_by_subreddit_id(ids[i])
        if i != len(ids) - 1:
            s += ', '
    if n > 1:
        ids_, weights = zip(*(nx.get_edge_attributes(nx.subgraph(graph, ids), 'weight').items()))
        print('Sabrediti: ' + s + '}\n' + 'Broj grana/max broj grana ' + str(len(weights)) + '/' + str(math.trunc(n*(n-1)/2)))
    else:
        print('Sabrediti: ' + s + '}\n' + 'Broj grana/max broj grana 0/0')


def return_number_of_edges(ids, graph):
    n = len(ids)
    if n > 1:
        ids_, weights = zip(*(nx.get_edge_attributes(nx.subgraph(graph, ids), 'weight').items()))
        return str(len(weights)) + '/' + str(math.trunc(n*(n-1)/2))
    else:
        return '0/0'


def return_subreddits_from_commune(ids):
    nodes = []
    for i in range(0, len(ids)):
        s = get_subreddit_name_by_subreddit_id(ids[i])
        nodes.append(s)
    return nodes


def return_edge_weights_from_commune(ids, graph):
    if len(ids) > 1:
        ids_, weights = zip(*(nx.get_edge_attributes(nx.subgraph(graph, ids), 'weight').items()))
        weights = sorted(weights)
        return str(weights)
    else:
        return '[]'


def import_communes(net_type_value, num_of_communes, spectral=''):
    if net_type_value == NetType.S_NET.value:
        giant_component = nx.read_gml(S_NET_GIANT_COMPONENT_FILE_PATH)
    elif net_type_value == NetType.S_NET_F.value:
        giant_component = nx.read_gml(S_NET_F_GIANT_COMPONENT_FILE_PATH)
    else:
        giant_component = nx.read_gml(S_NET_F_GIANT_COMPONENT_FILE_PATH)
    net_type_value_path_format = from_s_net_type_value_to_path_format(net_type_value)
    data = [pd.read_csv(f'{PATH_TO_COMMUNES}/communes_{net_type_value_path_format}/{net_type_value_path_format}_{num_of_communes}_communes{spectral}.csv', low_memory=False, index_col=0, header=0)]
    all_communes = []
    for i in range(0, num_of_communes):
        all_communes.append([])
    all_communes_from_csv = pd.concat(data, axis=0, ignore_index=True)
    if spectral == '_spectral':
        column = 'color'
    else:
        column = 'modularity_class'
    all_communes_from_csv = all_communes_from_csv.loc[:, ['Label', column]]
    for i in range(0, len(all_communes_from_csv)):
        all_communes[all_communes_from_csv.loc[i, column]].append(all_communes_from_csv.loc[i, 'Label'])
    s = []
    for i in range(0, num_of_communes):
        s.append(f'{len(all_communes[i])}-{return_number_of_edges(all_communes[i], giant_component)}')
        # print(return_subreddits_from_commune(all_communes[i]))
        print_commune(all_communes[i], giant_component)
        # print_commune_and_number_of_edges(all_communes[i], giant_component)
    print(s)


def detect_communes_user_net():
    user_net = nx.read_gml('../../../results/nets/giant_component/user_net_giant_component.gml')
    # s_net_f = nx.read_gml('../../../results/nets/giant_component/s_net_f_giant_component.gml')
    # s_net_f = nx.read_gml('../../../results/nets/s_net_t.gml')
    user_net = nx.DiGraph(user_net)
    communities = asyn_lpa_communities(user_net, weight='weight')
    print(communities)
    size_of_communes = []
    for c in communities:
        c_list = list(c)
        print(c_list)
        ids_, weights = zip(*(nx.get_edge_attributes(nx.subgraph(user_net, c_list), 'weight').items()))
        weights = sorted(weights)
        print(str(weights))
        size_of_communes.append(len(c_list))
        # print_commune(list(c), s_net_f)
    # for i in range(0, len(communities)):
    #     print(str(communities[i].values()))
    print('br', len(list(communities)))
    print(size_of_communes)


def detect_communes_s_net_s_lpa():
    user_net = nx.read_gml('../../../results/nets/giant_component/user_net_giant_component.gml')
    # s_net_f = nx.read_gml('../../../results/nets/giant_component/s_net_f_giant_component.gml')
    # s_net_f = nx.read_gml('../../../results/nets/s_net_t.gml')
    user_net = nx.DiGraph(user_net)
    communities = asyn_lpa_communities(user_net, weight='weight')
    print(communities)
    size_of_communes = []
    for c in communities:
        c_list = list(c)
        print(c_list)
        ids_, weights = zip(*(nx.get_edge_attributes(nx.subgraph(user_net, c_list), 'weight').items()))
        weights = sorted(weights)
        print(str(weights))
        size_of_communes.append(len(c_list))
        # print_commune(list(c), s_net_f)
    # for i in range(0, len(communities)):
    #     print(str(communities[i].values()))
    print('br', len(list(communities)))
    print(size_of_communes)


def read_net(net_type):
    if net_type == NetType.S_NET:
        return nx.read_gml('../../../results/nets/giant_component/s_net_giant_component.gml')
    elif net_type == NetType.S_NET_F:
        return nx.read_gml('../../../results/nets/giant_component/s_net_f_giant_component.gml')
    elif net_type == NetType.S_NET_T:
        return nx.read_gml('../../../results/nets/s_net_t.gml')
    elif net_type == NetType.USER_NET:
        graph = nx.read_gml('../../../results/nets/giant_component/user_net_giant_component.gml')
        return nx.DiGraph(graph)
    else:
        return None


def detect_communes_girvan_newman(net_type):
    graph = read_net(net_type)
    if graph is None:
        return
    comp = girvan_newman(graph)
    max_modularity = 0
    communes = tuple({node} for node in graph.nodes())
    print(communes)
    for index, curr_communes in enumerate(comp):
        print(index, curr_communes)
        curr_modularity = modularity(graph, curr_communes)
        if curr_modularity > max_modularity:
            max_modularity = curr_modularity
            communes = curr_communes
    print(communes)
    size_of_communes = []
    for index, curr_communes in enumerate(communes):
        curr_communes = list(curr_communes)
        print(return_subreddits_from_commune(curr_communes))
        print(return_edge_weights_from_commune(curr_communes, graph))
        size_of_communes.append(len(curr_communes))
    print('Broj komuna:', len(size_of_communes))
    print(size_of_communes)
    print('Modularnost:', max_modularity)


def detect_communes_lp_or_lpa(net_type, lp=True):         # lp = True for label propagation, False for async label propagation
    graph = read_net(net_type)
    if graph is None:
        return
    if lp:
        communities = label_propagation_communities(graph)
    else:
        communities = asyn_lpa_communities(graph, weight='weight')
    print(communities)
    size_of_communes = []
    for c in communities:
        c_list = list(c)
        # print(c_list)
        # if net_type != NetType.USER_NET:
        #     print(return_subreddits_from_commune(c_list))
        # ids_, weights = zip(*(nx.get_edge_attributes(nx.subgraph(graph, c_list), 'weight').items()))
        # weights = sorted(weights)
        # print(ids_, str(weights))
        size_of_communes.append(len(c_list))
    print('Broj komuna:', len(size_of_communes))
    print(size_of_communes)
    if lp:
        print('Modularnost sync lpa:', modularity(graph, label_propagation_communities(graph)))
    else:
        print('Modularnost async lpa:', modularity(graph, asyn_lpa_communities(graph, weight='weight')))


# import_communes(NetType.S_NET_F.value, 39, '_spectral')
# detect_communes_lp_or_lpa(NetType.USER_NET, lp=False)
# detect_communes_lp_or_lpa(NetType.S_NET_F, lp=True)

detect_communes_lp_or_lpa(NetType.S_NET_F, lp=True)
detect_communes_lp_or_lpa(NetType.S_NET_F, lp=False)
