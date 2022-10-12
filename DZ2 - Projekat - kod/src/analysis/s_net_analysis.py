import math
import networkx as nx
import pandas as pd
from datetime import datetime
import os
import seaborn as sns
from matplotlib import pyplot
from scipy.stats import pearsonr

from src.analysis.helper_analysis.basic_analysis import NetType, read_s_net_giant_component_graph, _14, _12, \
    plot_degree_distribution, _7, _8, _9, _10, are_nodes_with_high_lcc_connected, \
    draw_local_clustering_coefficient_distribution_include_weight, \
    classify_data_in_n_classes_and_calculate_mixing_matrix, make_havel_hakimi_graph, get_subreddit_name_by_subreddit_id, \
    _13
from src.analysis.helper_analysis.centrality_analysis import _19, _16, _17, _18
from src.analysis.helper_analysis.detection_of_communes import _20_graph_laplacian, spectral, detection_of_communes
from src.analysis.net_analysis import net_analysis
from src.analysis.statistical_analysis import read_submissions_and_comments


S_NET_FILE_PATH = '../../results/nets/s_net.gml'
# S_NET_FILE_PATH = 'H:/Serije/ASM/ASM Projekat/DZ2/reddit_data_cleaned/graph.gml'
submissions = pd.DataFrame()
comments = pd.DataFrame()
# date_to_compare = date.today()
date_to_compare = datetime.strptime('2009-1-1', '%Y-%m-%d')
alpha = 0.5


def make_s_net_graph():
    global submissions, comments
    submissions, comments = read_submissions_and_comments()
    G = nx.Graph()
    data = pd.concat([submissions, comments])[['subreddit', 'subreddit_id', 'author', 'created_utc']]
    data = data.groupby(['subreddit', 'subreddit_id', 'author'])['created_utc'].agg('min').reset_index()
    data = data[data.author != '[deleted]'].reset_index() # izbaceni cvorovi (sabrediti) koji imaju samo deleted kao authora, mozda je jedan autor kreirao jednu obajvu i posle se obrisao
    subreddits = data['subreddit_id'].unique()
    G.add_nodes_from(subreddits)
    all_authors = data['author'].unique()
    l = 0
    for author in all_authors:
        d = data.loc[data['author'] == author]
        print(l, '/', len(all_authors), '   ---   ', len(d))
        l = l + 1
        for i in range(0, len(d) - 1):
            for j in range(i + 1, len(d)):
                if d.iloc[i]['subreddit_id'] != d.iloc[j]['subreddit_id']:            #################### dopisala da izbegnemo self loops
                    # later_utc = max(d.iloc[i]['created_utc'], d.iloc[j]['created_utc'])
                    # later_date = datetime.fromtimestamp(later_utc)
                    # n = (date_to_compare.year - later_date.year) * 12 + date_to_compare.month - later_date.month
                    if (d.iloc[i]['subreddit_id'], d.iloc[j]['subreddit_id']) in G.edges:
                        # if G.edges[d.iloc[i]['subreddit_id'], d.iloc[j]['subreddit_id']]['weight'] > math.pow(alpha, n):
                        #     G.edges[d.iloc[i]['subreddit_id'], d.iloc[j]['subreddit_id']]['weight'] = math.pow(alpha, n)
                        G.edges[d.iloc[i]['subreddit_id'], d.iloc[j]['subreddit_id']]['weight'] += 1
                    else:
                        G.add_edge(d.iloc[i]['subreddit_id'], d.iloc[j]['subreddit_id'], weight=1)
    nx.write_gml(G, S_NET_FILE_PATH)
    return G


def read_s_net_graph():
    if os.path.isfile(S_NET_FILE_PATH):
        s_net = nx.read_gml(S_NET_FILE_PATH)
    else:
        s_net = make_s_net_graph()
    return s_net


def s_net_analysis():
    s_net = read_s_net_graph()
    # print(nx.edges(s_net))
    # print(nx.get_edge_attributes(s_net, 'weight'))
    # detection_of_communes(s_net, NetType.S_NET.value)
    # net_analysis(s_net, NetType.S_NET.value)
    # basic_characterization_of_modeled_networks(s_net, NetType.S_NET.value)
    # _7(s_net, NetType.S_NET.value)
    # _8(s_net, NetType.S_NET.value)
    # _9(s_net, NetType.S_NET.value)
    print(f'Za SNet mrežu se nadalje ispituje njena gigantska komponenta.')
    s_net = read_s_net_giant_component_graph(s_net)
    # _16(s_net, NetType.S_NET.value)
    # _18(s_net, NetType.S_NET.value)
    # _16(s_net, NetType.S_NET.value)
    # _16(s_net, NetType.S_NET.value)
    detection_of_communes(s_net, NetType.S_NET.value)
    # classify_data_in_n_classes_and_calculate_mixing_matrix(s_net, 6)

    # ids, degrees = zip(*sorted(s_net.degree, key=lambda x: x[1], reverse=True))
    # for i in range(0, 39):
    #     print(get_subreddit_name_by_subreddit_id(ids[i]))


    ###########################################
    # xy = nx.node_degree_xy(s_net)
    # x, y = zip(*xy)
    # print(pearsonr(x, y)[0])
    # pyplot.scatter(x, y, color="blue")
    # pyplot.show()
    ############################################

    # pyplot.scatter(union[NUMBER_OF_SUBMISSIONS_TEXT], union[NUMBER_OF_COMMENTS_TEXT], color="blue")
    # pyplot.savefig(f'../results/statistical_analysis/linear_correlation.jpg')
    # pyplot.show()
    # classify_data_in_n_classes_and_calculate_mixing_matrix(s_net, 6)
    # are_nodes_with_high_lcc_connected(s_net)
    # ids, num_of_neighbours = zip(*sorted(graph.degree, key=lambda x: x[1], reverse=True))
    # ids, lcc = zip(*sorted(nx.clustering(s_net).items(), key=lambda x: x[1], reverse=True))
    # for i in range(0, len(ids)):
    #     print(ids[i], lcc[i])
    # _12(s_net, NetType.S_NET.value, 6)
    # plot_degree_distribution(s_net, 'weight')


# s_net_analysis()
# s_net_f = nx.read_gml('../../results/nets/s_net_f.gml')
# s_net_f_nodes_list = list(nx.nodes(s_net_f))
# s_net = nx.read_gml('../../results/nets/giant_component/s_net_giant_component.gml')
# node_core_number_dictionary = nx.core_number(s_net)
# max_core_number = max(node_core_number_dictionary.values())
# print(node_core_number_dictionary.values())
# for k in range(max_core_number, 0, -1):
#     k_core = nx.k_core(s_net, k)
#     l_core_nodes_list = list(nx.nodes(k_core))
#     check = all(item in l_core_nodes_list for item in s_net_f_nodes_list)
#     if check:
#         print(f'Mreža SNetF je podgraf k-jezgra mreže SNet, gde je k {k}.')
#         nx.write_gml(k_core, '../../results/nets/giant_component/k_core_s_net_f.gml')
#         print(k)
#         break
print('1')

