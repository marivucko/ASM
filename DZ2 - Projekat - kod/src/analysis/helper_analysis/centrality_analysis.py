import json
import networkx as nx
import pandas as pd
import collections
from operator import itemgetter
import prettytable
from numpy import array

from src.analysis.helper_analysis.basic_analysis import print_top_n_from_dictionary, NetType, \
    read_s_net_giant_component_graph, get_subreddit_name_by_subreddit_id, read_user_net_giant_component_graph, \
    read_s_net_f_giant_component_graph, print_top_n_authors_from_dictionary, \
    print_top_n_from_dictionary_without_subreddit_header

USER_NET_IN_DEGREE_CENTRALITY = '../../results/user_net_centrality/user_net_in_degree_centrality.txt'
USER_NET_OUT_DEGREE_CENTRALITY = '../../results/user_net_centrality/user_net_out_degree_centrality.txt'
USER_NET_IN_CLOSENESS_CENTRALITY = '../../results/user_net_centrality/user_net_in_closeness_centrality.txt'
USER_NET_OUT_CLOSENESS_CENTRALITY = '../../results/user_net_centrality/user_net_out_closeness_centrality.txt'
USER_NET_BETWEENNESS_CENTRALITY = '../../results/user_net_centrality/user_net_di_betweenness_centrality.txt'
USER_NET_IN_EIGEN_VECTOR_CENTRALITY = '../../results/user_net_centrality/user_net_in_eigenvector_centrality_weight.txt'
USER_NET_OUT_EIGEN_VECTOR_CENTRALITY = '../../results/user_net_centrality/user_net_out_eigenvector_centrality_weight.txt'


def save_user_net_centrality_to_file():
    user_net = nx.read_gml('../../../results/nets/giant_component/user_net_giant_component.gml')
    sorted_dictionary = dict(sorted(nx.in_degree_centrality(user_net).items(), key=itemgetter(1), reverse=True))
    with open('../' + USER_NET_IN_DEGREE_CENTRALITY, 'w') as file:
         file.write(json.dumps(sorted_dictionary))

    sorted_dictionary = dict(sorted(nx.out_degree_centrality(user_net).items(), key=itemgetter(1), reverse=True))
    with open('../' + USER_NET_OUT_DEGREE_CENTRALITY, 'w') as file:
         file.write(json.dumps(sorted_dictionary))

    sorted_dictionary = dict(sorted(nx.closeness_centrality(user_net).items(), key=itemgetter(1), reverse=True))
    with open('../' + USER_NET_IN_CLOSENESS_CENTRALITY, 'w') as file:
         file.write(json.dumps(sorted_dictionary))

    sorted_dictionary = dict(sorted(nx.closeness_centrality(user_net.reverse()).items(), key=itemgetter(1), reverse=True))
    with open('../' + USER_NET_OUT_CLOSENESS_CENTRALITY, 'w') as file:
         file.write(json.dumps(sorted_dictionary))

    sorted_dictionary = dict(sorted(nx.betweenness_centrality(nx.DiGraph(user_net)).items(), key=itemgetter(1), reverse=True))
    with open('../' + USER_NET_BETWEENNESS_CENTRALITY, 'w') as file:
         file.write(json.dumps(sorted_dictionary))

    sorted_dictionary = dict(sorted(nx.eigenvector_centrality(nx.DiGraph(user_net), weight='weight').items(), key=itemgetter(1), reverse=True))
    with open('../' + USER_NET_IN_EIGEN_VECTOR_CENTRALITY, 'w') as file:
        file.write(json.dumps(sorted_dictionary))

    sorted_dictionary = dict(sorted(nx.eigenvector_centrality(nx.DiGraph(user_net).reverse(), weight='weight').items(), key=itemgetter(1), reverse=True))
    with open('../' + USER_NET_OUT_EIGEN_VECTOR_CENTRALITY, 'w') as file:
        file.write(json.dumps(sorted_dictionary))


def read_from_user_net_centrality_txt(file, n=10):
    sorted_dictionary = json.load(open(file))
    sorted_dictionary = dict(sorted(sorted_dictionary.items(), key=itemgetter(1), reverse=True)[:n])
    table = prettytable.PrettyTable(["Čvor", "Vrednost"])
    for item in sorted_dictionary:
        table.add_row([repr(item).strip("'"), round(sorted_dictionary[item], 6)])
    print(table)
    print("\n")


def _16(graph, net_type_value):
    if net_type_value == NetType.USER_NET.value:
        # save_user_net_centrality_to_file()
        print('16) 10 čvorova sa najvećom vrednošću centralnosti po ulaznom stepenu:')
        read_from_user_net_centrality_txt(USER_NET_IN_DEGREE_CENTRALITY)
        print('10 čvorova sa najvećom vrednošću centralnosti po izlaznom stepenu:')
        read_from_user_net_centrality_txt(USER_NET_OUT_DEGREE_CENTRALITY)
        print('10 čvorova sa najvećom vrednošću centralnosti po bliskosti (dolazna udaljenost do čvora):')
        read_from_user_net_centrality_txt(USER_NET_IN_CLOSENESS_CENTRALITY)
        print('10 čvorova sa najvećom vrednošću centralnosti po bliskosti (izlazna udaljenost od čvora):')
        read_from_user_net_centrality_txt(USER_NET_OUT_CLOSENESS_CENTRALITY)
        print('10 čvorova sa najvećom vrednošću relacione centralnosti:')
        read_from_user_net_centrality_txt(USER_NET_BETWEENNESS_CENTRALITY)
    else:
        label_for_node_in_table_header = 'Sabredit'
        print('16) 10 čvorova sa najvećom vrednošću centralnosti po stepenu:')
        print_top_n_from_dictionary(nx.degree_centrality(graph), 10, label_for_node_in_table_header)
        print('10 čvorova sa najvećom vrednošću centralnosti po bliskosti:')
        print_top_n_from_dictionary(nx.closeness_centrality(graph), 10, label_for_node_in_table_header)
        print('10 čvorova sa najvećom vrednošću relacione centralnosti:')
        print_top_n_from_dictionary(nx.betweenness_centrality(graph), 10, label_for_node_in_table_header)


def get_degrees_of_node_neighbours(graph, node):
    ids, degrees = zip(*sorted(graph.degree, key=lambda x: x[1], reverse=True))
    neighbours = list(graph.neighbors(node))
    i = 0
    j = 0
    degrees_of_node_neighbours = []
    while j < 10:
        if ids[i] in neighbours:
            j = j + 1
            degrees_of_node_neighbours.append(degrees[i])
        i = i + 1
    return degrees_of_node_neighbours


def get_weights_of_neighbours(graph, node):
    neighbours = list(graph.neighbors(node))
    weights_of_neighbours = []
    for neighbour in neighbours:
        weights_of_neighbours.append(graph.edges[(node, neighbour)]['weight'])
    counter_weights_of_neighbours = collections.Counter(weights_of_neighbours)
    counter_weights_of_neighbours_distribution = collections.OrderedDict(sorted(counter_weights_of_neighbours.items(), reverse=True))
    s = ''
    for index, item in enumerate(counter_weights_of_neighbours_distribution):
        s = s + str(round(item, 5)) + 'x' + str(counter_weights_of_neighbours_distribution[item])
        if index != (len(counter_weights_of_neighbours_distribution) - 1):
            s = s + ', '
        if index == 6:
            s = s + '\n'
    return s


def get_degree_centrality_of_neighbours(graph, node, call_function=0): # 0 - nx.degree_centrality, 1 - nx.in_degree_centrality, 2 - nx.out_degree_centrality
    neighbours = list(graph.neighbors(node))
    if call_function == 0:
        dcs = nx.degree_centrality(graph)
    elif call_function == 1:
        dcs = nx.in_degree_centrality(graph)
    else:
        dcs = nx.out_degree_centrality(graph)
    degrees = []
    for node, dc_value in dcs.items():
        if node in neighbours:
            degrees.append(round(dc_value, 1))
    counter_dc_of_neighbours = collections.Counter(degrees)
    counter_dc_of_neighbours_distribution = collections.OrderedDict(sorted(counter_dc_of_neighbours.items(), reverse=True))
    s = ''
    new_line = False
    item0 = 0
    for index, item in enumerate(counter_dc_of_neighbours_distribution):
        s = s + str(item) + 'x' + str(counter_dc_of_neighbours_distribution[item])
        if index != (len(counter_dc_of_neighbours_distribution) - 1):
            s = s + ', '
        if index == 0:
            item0 = item
        if (item <= 0.5) and not new_line and (item0 > 0.5):
            new_line = True
            s = s + '\n'
    return s


def get_weight_distribution(graph):
    weights = []
    for u, v, data in graph.edges(data=True):
        weights.append(data['weight'])
    counter_weights = collections.Counter(weights)
    counter_weights_distribution = collections.OrderedDict(sorted(counter_weights.items(), reverse=True))
    s = ''
    for index, item in enumerate(counter_weights_distribution):
        s = s + str(round(item, 5)) + 'x' + str(counter_weights_distribution[item])
        if index != (len(counter_weights_distribution) - 1):
            s = s + ', '
        if index == 6:
            s = s + '\n'
    return s


def _17(graph, net_type_value):
    if net_type_value == NetType.USER_NET.value:
        print('17) 10 čvorova sa najvećom vrednošću centralnosti po sopstvenom vektoru koji odgovaraju ulaznim granama:')
        sorted_dictionary = json.load(open(USER_NET_IN_EIGEN_VECTOR_CENTRALITY))
        sorted_dictionary = dict(sorted(sorted_dictionary.items(), key=itemgetter(1), reverse=True)[:10])
        table = prettytable.PrettyTable(["Autor", "EVC Vrednost", "Raspodela suseda čvora po centralnosti po izl. stepenu", "DC"])
        nodes = []
        degree_centrality = nx.degree_centrality(graph)
        for item in sorted_dictionary:
            node = repr(item).strip("'")
            nodes.append(node)
            table.add_row([node, round(sorted_dictionary[item], 6), get_degree_centrality_of_neighbours(graph, node, call_function=2), round(degree_centrality[item], 6)])
        print(table)

        print('17) 10 čvorova sa najvećom vrednošću centralnosti po sopstvenom vektoru koji odgovaraju izlaznim granama:')
        sorted_dictionary = json.load(open(USER_NET_OUT_EIGEN_VECTOR_CENTRALITY))
        sorted_dictionary = dict(sorted(sorted_dictionary.items(), key=itemgetter(1), reverse=True)[:10])
        table = prettytable.PrettyTable(["Autor", "EVC Vrednost", "Raspodela suseda čvora po centralnosti po ul. stepenu", "DC"])
        nodes = []
        degree_centrality = nx.degree_centrality(graph)
        for item in sorted_dictionary:
            node = repr(item).strip("'")
            nodes.append(node)
            table.add_row([node, round(sorted_dictionary[item], 6), get_degree_centrality_of_neighbours(graph, node, call_function=1), round(degree_centrality[item], 6)])
        print(table)
    else:
        sorted_dictionary = nx.eigenvector_centrality(graph, max_iter=1000, weight='weight')
        print('17) 10 čvorova sa najvećom vrednošću centralnosti po sopstvenom vektoru:')
        sorted_dictionary = dict(sorted(sorted_dictionary.items(), key=itemgetter(1), reverse=True)[:10])
        table = prettytable.PrettyTable(["Čvor", 'Sabredit', "EVC Vrednost", "Raspodela suseda čvora po centralnosti po stepenu", "DC"])
        nodes = []
        degree_centrality = nx.degree_centrality(graph)
        for item in sorted_dictionary:
            node = repr(item).strip("'")
            nodes.append(node)
            label_for_node = get_subreddit_name_by_subreddit_id(node)
            table.add_row([node, label_for_node, round(sorted_dictionary[item], 6), get_degree_centrality_of_neighbours(graph, node), round(degree_centrality[item], 6)])
        print(table)


def print_katz(graph, alfa, beta, label_for_node_in_table_header, node_diff_beta):
    beta_for_reddit_com = beta[node_diff_beta]
    if node_diff_beta == 't5_6':
        print(f'Katzova centralnost za alfa = {round(alfa, 9)} i beta za subredit reddit.com = {beta_for_reddit_com}, dok je za ostale 1')
        katz_dict = nx.katz_centrality(graph, alpha=alfa, beta=beta, tol=1e-06, max_iter=5000, nstart=None, normalized=True, weight='weight')
        print_top_n_from_dictionary(katz_dict, 5, label_for_node_in_table_header)
    else:
        print(f'Katzova centralnost za alfa = { round(alfa, 9) } i beta za autora {node_diff_beta} = { beta_for_reddit_com }, dok je za ostale 1')
        katz_dict = nx.katz_centrality(nx.DiGraph(graph), alpha=alfa, beta=beta, tol=1e-06, max_iter=500000, nstart=None, normalized=True, weight='weight')
        print_top_n_from_dictionary_without_subreddit_header(katz_dict, 5, label_for_node_in_table_header)


def katz_centrality(graph, label_for_node_in_table_header, node_diff_beta='t5_6'):
    if graph.is_directed():                     # ako je UserNet, prevelika je mreza za funkciju nx.adjacency_spectrum(graph)
        alfa_max = 5.452e-06
    else:
        lambda_max = max(nx.adjacency_spectrum(graph))
        alfa_max = (1 / lambda_max)
    print(f'Alfa max: { round(alfa_max, 9) }')
    alfa_max = (alfa_max * 0.99).real
    alfa_step = alfa_max / 3
    nodes = graph.nodes()
    beta_nodes_dictionary = dict.fromkeys(nodes, 1)
    alfa = alfa_step
    beta = [1, 2, 10, 100]
    while alfa < alfa_max:
        for i in range(0, len(beta)):
            beta_nodes_dictionary[node_diff_beta] = beta[i]
            print_katz(graph, alfa, beta_nodes_dictionary, label_for_node_in_table_header, node_diff_beta)
        alfa = alfa + alfa_step


def _18(graph, net_type_value):
    if net_type_value == NetType.USER_NET.value:
        katz_centrality(graph, 'Autor', node_diff_beta='RugerRedhawk')     # korisi se taj autor iz funkcija _top_10_most_active_users_on_reddit_com() iz statistical analysis
    else:
        katz_centrality(graph, 'Sabredit')


def _19(graph, net_type_value):
    if net_type_value == NetType.USER_NET.value:
        _19_user_net()
        return
    degree_centrality = nx.degree_centrality(graph)
    closeness_centrality = nx.closeness_centrality(graph)
    betweenness_centrality = nx.betweenness_centrality(graph)
    eigenvector_centrality = nx.eigenvector_centrality(graph, max_iter=1000, weight='weight')

    df1 = pd.DataFrame.from_dict(degree_centrality, orient='index', columns=['DC'])
    df2 = pd.DataFrame.from_dict(closeness_centrality, orient='index', columns=['CC'])
    df3 = pd.DataFrame.from_dict(betweenness_centrality, orient='index', columns=['BC'])
    df4 = pd.DataFrame.from_dict(eigenvector_centrality, orient='index', columns=['EVC'])
    df = pd.concat([df1, df2, df3, df4], axis=1)
    df_ = df

    labels = ['DC', 'CC', 'BC', 'EVC']
    for metric in labels:
        df_[f'{metric}_rank'] = df[f'{metric}'].rank(ascending=False)

    df_['Composite_rank'] = df_['DC_rank'] * df_['CC_rank'] * df_['BC_rank'] * df_['EVC_rank']
    dd = df_[['DC_rank', 'CC_rank', 'BC_rank', 'EVC_rank', 'Composite_rank']].sort_values(['Composite_rank'], ascending=True)

    giant_component = ''
    if (net_type_value == NetType.S_NET.value) or (net_type_value == NetType.S_NET_F.value):
        giant_component = ' gigantske komponente '
    print(f'19) 10 čvorova{giant_component}{net_type_value} mreže sa najvećom vrednošću kompozitnog ranga:')
    table = prettytable.PrettyTable(['Čvor', 'Sabredit', 'DC rang', 'CC rang', 'BC rang', 'EVC rang', 'Kompozitni rang'])
    dd = dd.reset_index()  # make sure indexes pair with number of rows
    for index, row in dd[:10].iterrows():
        table.add_row([row['index'], get_subreddit_name_by_subreddit_id(row['index']), row['DC_rank'], row['CC_rank'], row['BC_rank'], row['EVC_rank'], row['Composite_rank']])
    print(table)


def _19_user_net():
    in_degree_centrality = json.load(open(USER_NET_IN_DEGREE_CENTRALITY))
    out_degree_centrality = json.load(open(USER_NET_OUT_DEGREE_CENTRALITY))
    in_closeness_centrality = json.load(open(USER_NET_IN_CLOSENESS_CENTRALITY))
    out_closeness_centrality = json.load(open(USER_NET_OUT_CLOSENESS_CENTRALITY))
    betweenness_centrality = json.load(open(USER_NET_BETWEENNESS_CENTRALITY))

    df1 = pd.DataFrame.from_dict(in_degree_centrality, orient='index', columns=['IN DC'])
    df2 = pd.DataFrame.from_dict(out_degree_centrality, orient='index', columns=['OUT DC'])
    df3 = pd.DataFrame.from_dict(in_closeness_centrality, orient='index', columns=['IN CC'])
    df4 = pd.DataFrame.from_dict(out_closeness_centrality, orient='index', columns=['OUT CC'])
    df5 = pd.DataFrame.from_dict(betweenness_centrality, orient='index', columns=['BC'])
    df = pd.concat([df1, df2, df3, df4, df5], axis=1)
    df_ = df

    labels = ['IN DC', 'OUT DC', 'IN CC', 'OUT CC', 'BC']
    for metric in labels:
        print(metric)
        df_[f'{metric}_rank'] = df[f'{metric}'].rank(ascending=False)
    print('1')
    df_['Composite_rank'] = df_['IN DC_rank'] * df_['OUT DC_rank'] * df_['IN CC_rank'] * df_['OUT CC_rank'] * df_['BC_rank']
    print('2')
    dd = df_[['IN DC_rank', 'OUT DC_rank', 'IN CC_rank', 'OUT CC_rank', 'BC_rank', 'Composite_rank']].sort_values(['Composite_rank'], ascending=True)

    print(f'19) 10 čvorova gigantske komponente UserNet mreže sa najvećom vrednošću kompozitnog ranga:')
    table = prettytable.PrettyTable(['Autor', 'IN DC rang', 'OUT DC rang', 'IN CC rang', 'OUT CC rang', 'BC rang', 'Kompozitni rang'])
    dd = dd.reset_index()  # make sure indexes pair with number of rows
    for index, row in dd[:10].iterrows():
        table.add_row([row['index'], row['IN DC_rank'], row['OUT DC_rank'], row['IN CC_rank'], row['OUT CC_rank'], row['BC_rank'], row['Composite_rank']])
    print(table)


def centrality_analysis(graph, net_type_value):
    if net_type_value == NetType.S_NET.value:
        graph = read_s_net_giant_component_graph(graph)
    if net_type_value == NetType.S_NET_F.value:
        graph = read_s_net_f_giant_component_graph(graph)
    if net_type_value == NetType.USER_NET.value:
        graph = read_user_net_giant_component_graph(graph)
    print(nx.info(graph))
    _16(graph, net_type_value)
    _17(graph, net_type_value)
    _18(graph, net_type_value)
    _19(graph, net_type_value)
