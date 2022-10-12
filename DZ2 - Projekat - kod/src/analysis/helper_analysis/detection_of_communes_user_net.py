import math
from operator import itemgetter
import networkx as nx
import pandas as pd
from prettytable import prettytable
from src.analysis.helper_analysis.basic_analysis import NetType, _15
from networkx.algorithms.community import asyn_lpa_communities, label_propagation_communities, girvan_newman, modularity
from networkx.algorithms.bridges import bridges, has_bridges
from src.analysis.s_net_analysis import read_s_net_graph
from networkx.generators.ego import ego_graph

PATH_TO_COMMUNES = "../../../input_data/communes_from_gephi"
SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH = '../../../results/output_data_cleaned/subreddit_id__subreddit_dictionary'
S_NET_GIANT_COMPONENT_FILE_PATH = '../../../results/nets/giant_component/s_net_giant_component.gml'
S_NET_F_GIANT_COMPONENT_FILE_PATH = '../../../results/nets/giant_component/s_net_f_giant_component.gml'
S_NET_T_FILE_PATH = '../../../results/nets/s_net_t.gml'
USER_NET_GIANT_COMPONENT_FILE_PATH = '../../../results/nets/giant_component/user_net_giant_component.gml'


def get_subreddit_name_by_subreddit_id(subreddit_id):
    subreddit_id__subreddit_dictionary = pd.read_pickle(SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH)
    if subreddit_id in subreddit_id__subreddit_dictionary:
        return subreddit_id__subreddit_dictionary[subreddit_id]
    else:
        return 'There is no subreddit with this id in the whole of 2008.'


def from_s_net_type_value_to_path_format(net_type):
    if net_type == NetType.S_NET:
        return 's_net'
    elif net_type == NetType.S_NET_F:
        return 's_net_f'
    elif net_type == NetType.S_NET_T:
        return 's_net_t'
    elif net_type == NetType.USER_NET:
        return 'user_net'
    else:
        return ''


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


def get_bridge_edges(net_type):
    if net_type == NetType.S_NET:
        giant_component = nx.read_gml(S_NET_GIANT_COMPONENT_FILE_PATH)
    elif net_type == NetType.S_NET_F:
        giant_component = nx.read_gml(S_NET_F_GIANT_COMPONENT_FILE_PATH)
    elif net_type == NetType.USER_NET:
        giant_component = nx.read_gml(USER_NET_GIANT_COMPONENT_FILE_PATH)
    else:
        giant_component = nx.read_gml(S_NET_T_FILE_PATH)
    bridge_edges = list(bridges(giant_component))
    bridge_nodes = []
    for bridge_edge in bridge_edges:
        subreddit_bridge_node_0 = get_subreddit_name_by_subreddit_id(bridge_edge[0])
        subreddit_bridge_node_1 = get_subreddit_name_by_subreddit_id(bridge_edge[1])
        if subreddit_bridge_node_0 not in bridge_nodes:
            bridge_nodes.append(subreddit_bridge_node_0)
        if subreddit_bridge_node_1 not in bridge_nodes:
            bridge_nodes.append(subreddit_bridge_node_1)
        if (subreddit_bridge_node_0 != 'reddit.com') and (subreddit_bridge_node_1 != 'reddit.com'):
            print(subreddit_bridge_node_0, subreddit_bridge_node_1)
    print(len(bridge_edges))
    print(bridge_nodes)


def from_gml_with_ids_to_gml_with_names(input_file, output_file):
    giant_component = nx.read_gml(input_file)
    curr_nodes = list(nx.nodes(giant_component))
    mapping = {}
    for i in range(0, len(curr_nodes)):
        mapping[curr_nodes[i]] = get_subreddit_name_by_subreddit_id(curr_nodes[i])
    new_giant_component = nx.relabel_nodes(giant_component, mapping)
    nx.write_gml(new_giant_component, output_file)


def import_communes(net_type, num_of_communes, spectral=''):                # spectral='/spectral' za spektralno, spectral='' za csv iz gephia tj. Louvian
    if net_type == NetType.S_NET:
        giant_component = nx.read_gml(S_NET_GIANT_COMPONENT_FILE_PATH)
    elif net_type == NetType.S_NET_F:
        giant_component = nx.read_gml(S_NET_F_GIANT_COMPONENT_FILE_PATH)
    elif net_type == NetType.USER_NET:
        giant_component = nx.read_gml(USER_NET_GIANT_COMPONENT_FILE_PATH)
    else:
        giant_component = nx.read_gml(S_NET_T_FILE_PATH)
    net_type_value_path_format = from_s_net_type_value_to_path_format(net_type)
    s = '_spectral' if spectral == 'spectral/' else ''
    data = [pd.read_csv(f'H:/Serije/ASM/ASM Projekat/DZ2/input_data/communes_from_gephi/communes_{net_type_value_path_format}/{spectral}{net_type_value_path_format}_{num_of_communes}_communes{s}.csv', low_memory=False, index_col=0, header=0)]
    all_communes = []
    for i in range(0, num_of_communes):
        all_communes.append([])
    all_communes_from_csv = pd.concat(data, axis=0, ignore_index=True)
    if spectral == 'spectral/':
        column = 'color'
    else:
        column = 'modularity_class'
    all_communes_from_csv = all_communes_from_csv.loc[:, ['Label', column]]
    for i in range(0, len(all_communes_from_csv)):
        all_communes[all_communes_from_csv.loc[i, column]].append(all_communes_from_csv.loc[i, 'Label'])
    size_of_communes = []
    for i in range(0, num_of_communes):
        c_list = all_communes[i]
        # print(len(c_list), ':')
        # print(c_list)
        if len(c_list) <= 30:
            print(c_list)
            if net_type != NetType.USER_NET:
                print(return_subreddits_from_commune(c_list))
            # ids_, weights = zip(*(nx.get_edge_attributes(nx.subgraph(giant_component, c_list), 'weight').items()))
            # print(len(weights))
            # weights = sorted(weights)
            # print(ids_, str(weights))
            size_of_communes.append(len(c_list))
    print(size_of_communes)
    # print('Da li postoje mostovi u mreži:', has_bridges(giant_component))
    # print('Nađeni mostovi:', len(list(bridges(giant_component))))
    # print('Nađeni mostovi:', list(bridges(giant_component)))
    print(f'Modularnost {net_type} {num_of_communes} {spectral}:', modularity(giant_component, all_communes))





# import_communes(NetType.USER_NET, 6, spectral='')
# import_communes(NetType.USER_NET, 39, spectral='')
# import_communes(NetType.USER_NET, 39, spectral='') #======================================== ovo za user_net

user_net = nx.read_gml(USER_NET_GIANT_COMPONENT_FILE_PATH)
nodes_with_max_bcc = ['rmuser', 'alllie', '7oby', 'qgyh2', 'NoMoreNicksLeft', 'nixonrichard', 'malcontent', 'Poromenos', 'swampsparrow', 'mutatron']
for i in range(0, len(nodes_with_max_bcc)):
    nx.write_gml(ego_graph(user_net, nodes_with_max_bcc[i]), f'H:/Serije/ASM/ASM Projekat/DZ2/results/nets/user_net_ego_nets_{nodes_with_max_bcc[i]}.gml')



# import_communes(NetType.S_NET_F, 2, spectral='')
# import_communes(NetType.S_NET_F, 5, spectral='')
# import_communes(NetType.S_NET_F, 39, spectral='')
# import_communes(NetType.S_NET_F, 2, spectral='spectral/')
# import_communes(NetType.S_NET_F, 5, spectral='spectral/')
# import_communes(NetType.S_NET_F, 6, spectral='spectral/')
# import_communes(NetType.S_NET_F, 7, spectral='spectral/')
# import_communes(NetType.S_NET_F, 31, spectral='spectral/')
# import_communes(NetType.S_NET_F, 31, spectral='spectral/')  #======================================== ovo i naredne 2 linije za s_net_f 21,22,23
# from_gml_with_ids_to_gml_with_names('H:/Serije/ASM/ASM Projekat/DZ2/results/spectral/s_net_f/spectral31.gml',
#                                     'H:/Serije/ASM/ASM Projekat/DZ2/input_data/communes_from_gephi/communes_s_net_f/spectral/s_net_f_31_communes_spectral_subreddit_names.gml')
# get_bridge_edges(NetType.S_NET_F)

# import_communes(NetType.S_NET, 2, spectral='spectral/')
# import_communes(NetType.S_NET, 3, spectral='spectral/')
# import_communes(NetType.S_NET, 4, spectral='spectral/')
# import_communes(NetType.S_NET, 5, spectral='spectral/')
# import_communes(NetType.S_NET, 8, spectral='spectral/')
# import_communes(NetType.S_NET, 12, spectral='spectral/')

# import_communes(NetType.S_NET, 3, spectral='')
# import_communes(NetType.S_NET, 32, spectral='')
# import_communes(NetType.S_NET, 12, spectral='') #========================================
# from_gml_with_ids_to_gml_with_names('H:/Serije/ASM/ASM Projekat/DZ2/results/spectral/s_net/spectral12.gml',ovo i naredne 2 linije za s_net 21,22,23
#                                     'H:/Serije/ASM/ASM Projekat/DZ2/input_data/communes_from_gephi/communes_s_net/spectral/s_net_12_communes_spectral_subreddit_names.gml')
# get_bridge_edges(NetType.S_NET)