import math
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from enum import Enum
from collections import Counter
from operator import itemgetter
import prettytable
import collections
import os
import powerlaw
import pandas as pd
import pickle
from os.path import exists
import statistics
from itertools import chain
from scipy import stats
from matplotlib import pyplot
from scipy.stats import pearsonr

from src.analysis.statistical_analysis import read_submissions_and_comments


class NetType(Enum):
    S_NET = 'SNet'
    S_NET_F = 'SNetF'
    S_NET_T = 'SNetT'
    USER_NET = 'UserNet'


S_NET_GIANT_COMPONENT_FILE_PATH = '../../results/nets/giant_component/s_net_giant_component.gml'
S_NET_F_GIANT_COMPONENT_FILE_PATH = '../../results/nets/giant_component/s_net_f_giant_component.gml'
S_NET_T_FILE_PATH = '../../results/nets/s_net_t.gml'
# USER_NET_GIANT_COMPONENT_FILE_PATH = '../../results/nets/giant_component/user_net_giant_component.gml'
USER_NET_GIANT_COMPONENT_FILE_PATH = '../../results/nets/giant_component/user_net_giant_component.gml'
USER_NET_ERDOS_RENY_FILE_PATH = '../../results/nets/giant_component/user_net_erdos_reny.gml'
SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH = '../../results/output_data_cleaned/subreddit_id__subreddit_dictionary'

submissions = pd.DataFrame()
comments = pd.DataFrame()


def make_subreddit_id__subreddit_dictionary():
    global submissions, comments
    submissions, comments = read_submissions_and_comments()
    data = pd.concat([submissions, comments])[['subreddit', 'subreddit_id']]
    data = data.drop_duplicates()
    subreddit_id__subreddit_dictionary = dict(zip(data.subreddit_id, data.subreddit))
    with open(SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH, 'wb') as file:
        pickle.dump(subreddit_id__subreddit_dictionary, file)


def get_subreddit_name_by_subreddit_id(subreddit_id):
    if not os.path.isfile(SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH):
        make_subreddit_id__subreddit_dictionary()
    subreddit_id__subreddit_dictionary = pd.read_pickle(SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH)
    if subreddit_id in subreddit_id__subreddit_dictionary:
        return subreddit_id__subreddit_dictionary[subreddit_id]
    else:
        return 'There is no subreddit with this id in the whole of 2008.'


def get_subreddit_id_by_subreddit_name(subreddit_name):
    if not os.path.isfile(SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH):
        make_subreddit_id__subreddit_dictionary()
    subreddit_id__subreddit_dictionary = pd.read_pickle(SUBREDDIT_ID__SUBREDDIT_DICTIONARY_FILE_PATH)
    for subreddit_id, subreddit in subreddit_id__subreddit_dictionary.items():
        if subreddit == subreddit_name:
            return subreddit_id
    return None


def get_size_of_connected_components_distribution(connected_components):
    size_of_connected_components = Counter(connected_components)
    size_of_connected_components_distribution = collections.OrderedDict(
        sorted(size_of_connected_components.items(), reverse=True))
    s = ''
    for index, item in enumerate(size_of_connected_components_distribution):
        s = s + str(item) + 'x' + str(size_of_connected_components_distribution[item])
        if index != (len(size_of_connected_components_distribution) - 1):
            s = s + ', '
    return s


def get_sizes_of_connected_components(graph):
    if nx.is_directed(graph):
        components = list(nx.strongly_connected_components(graph))
    else:
        components = list(nx.connected_components(graph))
    x = []
    for i in range(0, len(components)):
        x.append(len(components[i]))
    x = sorted(x, reverse=True)
    return x


def get_giant_component(graph):
    print('1')
    if nx.is_directed(graph):
        print('2')
        gcc = sorted(nx.strongly_connected_components(graph), key=len, reverse=True)
    else:
        print('3')
        gcc = sorted(nx.connected_components(graph), key=len, reverse=True)
    print('4')
    giant_component = graph.subgraph(gcc[0])
    print('5')
    return giant_component


def component_is_a_giant_component_in_graph(component, graph):
    if graph.number_of_nodes() > 0:
        return component.number_of_nodes() / graph.number_of_nodes() > 0.45
    else:
        return False


def print_top_n_from_dictionary(dictionary, n, label_for_node_in_table_header):
    sorted_dictionary = dict(sorted(dictionary.items(), key=itemgetter(1), reverse=True)[:n])
    table = prettytable.PrettyTable(["Čvor", label_for_node_in_table_header, "Vrednost"])
    for item in sorted_dictionary:
        table.add_row([repr(item).strip("'"), get_subreddit_name_by_subreddit_id(repr(item).strip("'")), round(sorted_dictionary[item], 6)])
    print(table)
    print("\n")


def print_top_n_from_dictionary_without_subreddit_header(dictionary, n, label_for_node_in_table_header):
    sorted_dictionary = dict(sorted(dictionary.items(), key=itemgetter(1), reverse=True)[:n])
    table = prettytable.PrettyTable([label_for_node_in_table_header, "Vrednost"])
    for item in sorted_dictionary:
        table.add_row([repr(item).strip("'"), round(sorted_dictionary[item], 6)])
    print(table)
    print("\n")


def print_top_n_authors_from_dictionary(dictionary, n):
    sorted_dictionary = dict(sorted(dictionary.items(), key=itemgetter(1), reverse=True)[:n])
    table = prettytable.PrettyTable(["Čvor", "Vrednost"])
    for item in sorted_dictionary:
        table.add_row([repr(item).strip("'"), round(sorted_dictionary[item], 6)])
    print(table)
    print("\n")


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


def _7(graph, net_type_value):
    print(f'7) Gustina {net_type_value} mreže je {round(nx.density(graph), 6)}.')


def average_shortest_path_and_diameter_for_erdos_reny(graph):
    print('l1')
    n = graph.number_of_nodes()
    print('l2', n)
    m = graph.number_of_edges()
    print('l3', m)
    H = nx.erdos_renyi_graph(n, 2 * float(m) / (n * (n - 1)))
    print('ll')
    print(f'a dijametar je {nx.diameter(H)}.')
    print(f'Prosečna distanca u Erdos-Reny mreži istih dimenzija je {round(nx.average_shortest_path_length(H), 6)}, ')


def _8(graph, net_type_value):
    try:
        print(f'8) Prosečna distanca u {net_type_value} mreži je {nx.average_shortest_path_length(graph)}, dok je dijametar {nx.diameter(graph)}.')
        average_shortest_path_and_diameter_for_erdos_reny(graph)
    except nx.exception.NetworkXError:
        print('8) Mreža nije povezana, stoga su prosečna dužina i dijametar mreže beskonačni.')
        print('a')
        the_largest_component_in_graph = get_giant_component(graph)
        print('b')
        if component_is_a_giant_component_in_graph(the_largest_component_in_graph, graph):
            print(f'Gustina gigantske komponente mreže je {round(nx.density(the_largest_component_in_graph), 6)}.')
            print(f'Prosečna distanca u gigantskoj komponenti mreže je {round(nx.average_shortest_path_length(the_largest_component_in_graph), 3)}, dok je dijametar {nx.diameter(the_largest_component_in_graph)}.')
            average_shortest_path_and_diameter_for_erdos_reny(the_largest_component_in_graph)
        else:
            print('Ne postoji gigantska komponenta mreže, tako da je mreža podeljena na više nepovezanih komponenti male veličine.')


def _9(graph, net_type_value):
    connected_components = get_sizes_of_connected_components(graph)
    the_largest_component_in_graph = get_giant_component(graph)
    num_of_connected_components = len(connected_components)
    if num_of_connected_components == 1:
        print(f'9) {net_type_value} mreža je povezana, pa ona cela predstavlja i gigantsku komponentu mreže.')
        return
    print(f'9) Broj povezanih komponenti {net_type_value} mreže je {num_of_connected_components}.')
    print(f'Veličina komponenti je data kao niz gde je prvi član predstavlja veličinu komponente, a drugi broj komponenti koje su te veličine: {get_size_of_connected_components_distribution(connected_components)}.')
    num_of_nodes_in_the_largest_component = the_largest_component_in_graph.number_of_nodes()
    if component_is_a_giant_component_in_graph(the_largest_component_in_graph, graph):
        print(f'Postoji gigantska komponenta mreže jer postoji jezgro veličine {num_of_nodes_in_the_largest_component} čvorova i predstavlja najveći deo mreže tj. {round(num_of_nodes_in_the_largest_component / graph.number_of_nodes() * 100, 2)}% mreze.')
        if net_type_value == NetType.S_NET.value:
            nx.write_gml(the_largest_component_in_graph, S_NET_GIANT_COMPONENT_FILE_PATH)
        elif net_type_value == NetType.S_NET_F.value:
            nx.write_gml(the_largest_component_in_graph, S_NET_F_GIANT_COMPONENT_FILE_PATH)
        elif net_type_value == NetType.USER_NET.value:
            nx.write_gml(the_largest_component_in_graph, USER_NET_GIANT_COMPONENT_FILE_PATH)
    else:
        print(f'Ne postoji gigantska komponenta mreže jer je najveća povezana komponenta mreže veličine {num_of_nodes_in_the_largest_component} čvorova i predstavlja {round(num_of_nodes_in_the_largest_component / graph.number_of_nodes() * 100, 2)}% mreze, što je manje od 45% mreže.')


def get_global_clustering_coefficient(graph, num_of_decimals=10):
    if graph.is_directed():
        graph = nx.Graph(graph)
    n = graph.number_of_nodes()
    number_of_triangles = sum(nx.triangles(graph).values()) / 3
    max_number_of_triangles = n * (n - 1) * (n - 2) / 6
    global_clustering_coefficient = number_of_triangles / max_number_of_triangles
    # return round(global_clustering_coefficient, num_of_decimals)
    return global_clustering_coefficient


def draw_local_clustering_coefficient_distribution_include_weight(graph, include_weight):
    weight = ''
    if include_weight:
        weight = 'weight'
    if graph.is_directed():             # prepoznavanje da je UserNet jer je jedino on directed, narednom linijom prestaje da bude multigraph je f-ja nije podrzana za multigraph
        graph = nx.DiGraph(graph)
    ids, lcc = zip(*nx.clustering(graph, weight=weight).items())
    lcc_counts = Counter(lcc)
    x1, y1 = zip(*lcc_counts.items())
    for i in range(0, len(x1)):
        print('***', x1[i], y1[i])
    if include_weight:
        plt.title('Raspodela lokalnog koeficijenta klasterizacije čvorova\nuzimajući u obzir težine grana')
    else:
        plt.title('Raspodela lokalnog koeficijenta klasterizacije čvorova')
    plt.xlabel('Lokalni koeficijent klasterizacije')
    plt.ylabel('Broj čvorova')
    plt.scatter(x1, y1, marker='.')
    plt.show()
    # for i in range(0, len(x1)):
    #     print(i, x1[i], y1[i])
    return max(x1), max(y1)


def are_nodes_with_high_lcc_connected(graph, weight=''):
    if graph.is_directed():
        graph = nx.DiGraph(graph)
    lcc = nx.clustering(graph, weight=weight)
    nodes_with_high_lcc = []
    for key, value in lcc.items():
        if value >= 0.5:
            nodes_with_high_lcc.append(key)
            # neighbours = list(graph.neighbors(key))
            # s = ''
            # average_lcc_of_neighbours = 0
            # for j in range(0, len(neighbours)):
            #     s = s + ', ' + str(lcc[neighbours[j]])
            #     average_lcc_of_neighbours += lcc[neighbours[j]]
            # average_lcc_of_neighbours /= len(neighbours)
            # print(key, '*', str(average_lcc_of_neighbours), '###', s)
    sub_graph_with_high_lcc = nx.subgraph(graph, nodes_with_high_lcc)
    print(nx.info(sub_graph_with_high_lcc))


def erdos_renyi(graph, x_max=0, y_max=0):
    n = graph.number_of_nodes()
    m = graph.number_of_edges()
    H = nx.erdos_renyi_graph(n, 2 * float(m) / (n * (n - 1)), directed=graph.is_directed())
    print(
        f'Prosečni koeficijent klasterizacije Erdos-Reny mreže istih dimenzija je {round(nx.average_clustering(H), 3)},'
        f' dok je globalni koeficijent klasterizacije {get_global_clustering_coefficient(H, 6)}.')
    ids, lcc = zip(*nx.clustering(H).items())
    lcc_counts = Counter(lcc)
    x2, y2 = zip(*lcc_counts.items())
    if x_max > 0:
        plt.xlim(0, x_max)
    if y_max > 0:
        plt.ylim(0, y_max)
    plt.xlabel('Lokalni koeficijent klasterizacije')
    plt.ylabel('Broj čvorova')
    plt.title('Raspodela lokalnog koeficijenta klasterizacije čvorova\n Erods-Renyi mreže istih dimenzija')
    plt.scatter(x2, y2, marker='.')
    plt.show()


def _10(graph, net_type_value):
    print(f'10) Prosečni koeficijent klasterizacije {net_type_value} mreže je {round(nx.average_clustering(graph), 4)}, ')
    print(f'dok je prosečni koeficijent klasterizacije uzimajući u obzir težine grana {round(nx.average_clustering(graph, weight="weight"), 4)}. ')
    print(f'Globalni koeficijent klasterizacije je {get_global_clustering_coefficient(graph)}.')
    draw_local_clustering_coefficient_distribution_include_weight(graph, True)
    # classify_data_in_n_classes_and_calculate_mixing_matrix(graph, 6)
    x_max, y_max = draw_local_clustering_coefficient_distribution_include_weight(graph, False)
    erdos_renyi(graph)
    erdos_renyi(graph, x_max, y_max)


def replace_elements_in_2_arrays_by_index(x, y, i1, i2):
    p = x[i1]
    x[i1] = x[i2]
    x[i2] = p
    p = y[i1]
    y[i1] = y[i2]
    y[i2] = p
    return x, y


def classify_data_in_n_classes_and_calculate_mixing_matrix(graph, num_of_classes, in_out_or_both=3):     # 1 - in_degree, 2 - out_degree, 3 - both
    graph_with_labels = graph
    n = nx.number_of_nodes(graph)
    classes = []
    mapping = {}
    degree_range = []
    size_of_class = round(n / num_of_classes, 0)
    for i in range(0, num_of_classes):
        classes.append(f'c{i}')
        mapping.update({f'c{i}': i})
    if graph.is_directed():             # ako je direktan znaci da je UserNet, pretvaramo ga u samo direktan da ne bi vise bio muligraph, jer funkcija nije implementirana za multigraph
        graph = nx.DiGraph(graph)
    if in_out_or_both == 1:
        ids, num_of_neighbours = zip(*sorted(graph.in_degree(), key=lambda x: x[1], reverse=True)) #koristiti ovu liniju ako se zeli ispitati da li se covorovi slicnog stepena cvora medjusobno povezuju
    elif in_out_or_both == 2:
        ids, num_of_neighbours = zip(*sorted(graph.out_degree(), key=lambda x: x[1], reverse=True)) #koristiti ovu liniju ako se zeli ispitati da li se covorovi slicnog stepena cvora medjusobno povezuju
    else:
        ids, num_of_neighbours = zip(*sorted(graph.degree(), key=lambda x: x[1], reverse=True)) #koristiti ovu liniju ako se zeli ispitati da li se covorovi slicnog stepena cvora medjusobno povezuju
    # ids, num_of_neighbours = zip(*sorted(nx.clustering(graph).items(), key=lambda x: x[1], reverse=True)) #koristiti ovu liniju ako se zeli ispitati da li se covorovi slicnog lokalno stepena klasterizacije medjusobno povezuju
    j = 0
    degree_range_max = num_of_neighbours[0]
    for i in range(0, len(ids)):
        graph_with_labels.nodes[ids[i]]['class'] = f'c{j}'
        if (i != 0) and (i % size_of_class == 0):
            j = j + 1
            degree_range_min = num_of_neighbours[i]
            degree_range.append(tuple((degree_range_min, degree_range_max)))
        if (i != 1) and (i % size_of_class == 1):
            degree_range_max = num_of_neighbours[i]
    degree_range.append(tuple((num_of_neighbours[n - 1], degree_range_max)))
    mix_mat = nx.attribute_mixing_matrix(graph_with_labels, attribute='class', mapping=mapping)
    classes_and_degree_ranges = []
    for i in range(0, num_of_classes):
        classes_and_degree_ranges.append(classes[i] + ' ' + str(degree_range[i]))
    table = prettytable.PrettyTable([' '] + classes_and_degree_ranges)
    print(f'Čvorovi grafa su kategorički grupisani u skupove c0-c{ num_of_classes - 1 } jednakih veličina. ' 
          f'Preračunata je matrica asortativnog mešanja koja je prikazana u narednoj tabeli. U tabeli su pored imena skupova prikazani i opsezi stepene čvorova koji pripadaju toj grupi.')
    probability = 0
    y = []
    print('**', classes)
    for i in range(0, num_of_classes):
        s = [classes[i]]
        for j in range(0, num_of_classes):
            s.append(str(round(mix_mat[mapping[f'c{i}'], mapping[f'c{j}']], 7)))
            if i == j:
                probability = probability + mix_mat[mapping[f'c{i}'], mapping[f'c{j}']]
                y.append(round(mix_mat[mapping[f'c{i}'], mapping[f'c{j}']], 4))
        table.add_row(s)
    print(table)
    print(f'Koeficijent asortativnosti za kategorički podeljene čvorova prema njihovim stepenima čvora je { round(nx.attribute_assortativity_coefficient(graph_with_labels, attribute="class"), 4) }.')
    xy_iter = nx.node_attribute_xy(graph_with_labels, attribute="class")
    x, y = zip(*xy_iter)
    xa = []
    ya = []
    x_ = []
    y_ = []
    for i in range(0, num_of_classes):
        for j in range(0, num_of_classes):
            if mix_mat[mapping[f'c{i}'], mapping[f'c{j}']] > 0.001:
                x_.append(f'c{i}')
                y_.append(f'c{j}')
    for i in range(0, len(x)):
        xa.append(int(x[i][1]))
        ya.append(int(y[i][1]))
    gradient, intercept, r_value, p_value, std_err = stats.linregress(xa, ya)
    mn = np.min(xa)
    mx = np.max(xa)
    x1 = np.linspace(mn, mx, 500)
    y1 = gradient * x1 + intercept
    # pyplot.scatter(x, y, color="blue")    #ako zelimo da prikazemo sve tacke oblika ci,cj
    pyplot.scatter(x_, y_, color="blue")    #ako odbacujemo one ci,cj kod kojih je mala verovatnoca da postoje
    pyplot.plot(x1, y1, '-r')
    pyplot.show()
    # xy = nx.node_degree_xy(graph_with_labels)
    # x, y = zip(*xy)
    # print(pearsonr(x, y)[0])
    # pyplot.scatter(x, y, color="blue")
    # pyplot.show()
    print(f'Sabiranjem elementa glave dijagonale matrice dobijamo da je verovatnoća { round(probability, 4) } da su čvorovi istih grupa međusobno povezani.')
    # plt.bar(classes_and_degree_ranges, y)
    # plt.xticks(classes_and_degree_ranges)
    # plt.yticks(y)
    # plt.xlabel('Kategoričke grupe')
    # plt.ylabel('Verovatnoća da je svaka od grupa povezana sa čvorovima svoje grupe')
    # plt.show()


def make_havel_hakimi_graph(graph):
    ids, num_of_neighbours = zip(*sorted(graph.degree(), key=lambda x: x[1], reverse=True))
    g1 = nx.havel_hakimi_graph(num_of_neighbours)
    print(f'Za Havel-Hakimi mrežu sa istom raspodelom čvorova po stepenu kao kod posmatrane mreže dobijamo koeficijent asortativnosti {round(nx.degree_assortativity_coefficient(g1, weight="weight"), 4)}.')


def _12(graph, net_type_value, num_of_classes):
    if net_type_value == NetType.USER_NET.value:
        # print(f"Koeficijent asortativnosti {net_type_value} mreže na osnovu ulaznog težinskog stepena čvora je {round(nx.degree_assortativity_coefficient(graph, x='out', y = 'in', weight='weight'), 10)}.")
        # print(f"Koeficijent asortativnosti {net_type_value} mreže na osnovu izlaznog težinskog stepena čvora je {round(nx.degree_assortativity_coefficient(graph, x='in', y = 'out', weight='weight'), 10)}.")
        # print(f"Koeficijent asortativnosti {net_type_value} mreže na osnovu ulaznog stepena čvora je {round(nx.degree_assortativity_coefficient(graph, x='out', y = 'in'), 10)}.")
        # print(f"Koeficijent asortativnosti {net_type_value} mreže na osnovu izlaznog stepena čvora je {round(nx.degree_assortativity_coefficient(graph, x='in', y = 'out'), 10)}.")
        classify_data_in_n_classes_and_calculate_mixing_matrix(graph, num_of_classes, in_out_or_both=1)
        classify_data_in_n_classes_and_calculate_mixing_matrix(graph, num_of_classes, in_out_or_both=2)
        return
    r = nx.degree_assortativity_coefficient(graph, weight='weight')
    print(f'Koeficijent asortativnosti {net_type_value} mreže na osnovu težinskog stepena čvora je {round(r, 4)}.')
    n = nx.number_of_nodes(graph)
    if nx.number_of_edges(graph) != n * (n-1) / 2:                      # nema potrebe kod kompletnog grafa traziti matricu asortativnosti, a koef asortati ce biti nan jer se deli sa 0 jer je devijacija stepena cvora od srednje vrednosti jednaka 0
        r = nx.degree_assortativity_coefficient(graph)
        print(f'Koeficijent asortativnosti {net_type_value} mreže na osnovu stepena čvora je {r}.')
        classify_data_in_n_classes_and_calculate_mixing_matrix(graph, num_of_classes)
        make_havel_hakimi_graph(graph)


def _13(graph):
    rc = nx.richclub.rich_club_coefficient(graph)
    print(f'{ rc }')


def plot_degree_distribution(graph, weight='', p=0):    # p=1 za racunjanje in_degree, -1 za out_degree, 0 za neusmere mreze
    if p == 1:
        _, degree_list = zip(*graph.in_degree(weight=weight))
    elif p == -1:
        _, degree_list = zip(*graph.out_degree(weight=weight))
    else:
        _, degree_list = zip(*graph.degree(weight=weight))
    degree_counts = Counter(degree_list)
    x, y = zip(*degree_counts.items())
    x_label = 'Stepen čvora'
    if weight == 'weight':
        x_label = 'Težinski stepen čvora'
    plt.xlabel(x_label)
    plt.ylabel('Broj čvorova')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(1, 1000)
    plt.ylim(1, max(y))
    plt.figure(1)
    plt.scatter(x, y, marker='.')
    plt.show()
    # degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
    # degree_count = Counter(degree_sequence)
    # deg, cnt = zip(*degree_count.items())
    # for i in range(0, len(deg)):
    #     print(deg[i], cnt[i])


def cumulative_degree_distribution(graph, p=0):         # p=1 za in_degree, p=-1 za out_degre, p=0 za unidirectrd
    if p == 1:
        degree_sequence = sorted([d for n, d in graph.in_degree()], reverse=True)
    elif p == -1:
        degree_sequence = sorted([d for n, d in graph.out_degree()], reverse=True)
    else:
        degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
    degree_count = Counter(degree_sequence)
    deg, cnt = zip(*degree_count.items())
    max_deg = max(deg)
    values, base = np.histogram(deg, bins=max_deg)
    cumulative = np.cumsum(values)
    n = nx.number_of_nodes(graph)
    plt.plot(base[:-1], [float(x)/n for x in n-cumulative], c='blue')
    plt.show()


def power_law(graph, p=0):          # p=1 za in_degree, p=-1 za out_degre, p=0 za unidirectrd
    if p == 1:
        degree_sequence = sorted([d for n, d in graph.in_degree()], reverse=True)
    elif p == -1:
        degree_sequence = sorted([d for n, d in graph.out_degree()], reverse=True)
    else:
        degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
    results = powerlaw.Fit(degree_sequence)
    print(results.supported_distributions)
    print('Alfa', results.power_law.alpha)
    print('x_min', results.power_law.xmin)
    print('sigma', results.power_law.sigma)
    # print(results.distribution_compare('power_law', 'lognormal'))

    # fig4 = results.plot_ccdf(linewidth=3)
    # results.power_law.plot_ccdf(ax=fig4, color='r', linestyle='--', linewidth=1, label='power_law')
    # results.lognormal.plot_ccdf(ax=fig4, color='g', linestyle='-', linewidth=2, label='lognormal')
    # results.exponential.plot_ccdf(ax=fig4, color='k', linestyle='-.', linewidth=1, label='exponential')
    # results.truncated_power_law.plot_ccdf(ax=fig4, color='y', linestyle='dotted', linewidth=2, label='truncated_power_law')
    # results.stretched_exponential.plot_ccdf(ax=fig4, color='m', linewidth=1, label='stretched_exponential')
    # plt.legend()
    # plt.show()

    print('==')
    funcs = ['truncated_power_law', 'exponential', 'lognormal', 'stretched_exponential']
    for i in range(0, len(funcs)):
        print(f'Poređenje power_law i {funcs[i]} modela:')
        R, p = results.distribution_compare('power_law', funcs[i])
        print(f'Loglikelihood ratio: {R}')
        print(f'Statistical significance: {p}\n')
    print('==')
    print('==')
    funcs = ['power_law', 'exponential', 'lognormal', 'stretched_exponential']
    for i in range(0, len(funcs)):
        print(f'Poređenje truncated_power_law i {funcs[i]} modela:')
        R, p = results.distribution_compare('truncated_power_law', funcs[i])
        print(f'Loglikelihood ratio: {R}')
        print(f'Statistical significance: {p}\n')
    print('==')
    print(f'Poređenje stretched_exponential i exponential modela:')
    R, p = results.distribution_compare('stretched_exponential', 'exponential')
    print(f'Loglikelihoo ratio: {R}')
    print(f'Statistical significance: {p}')
    print('stretched_exponential beta', results.stretched_exponential.beta)
    print('stretched_exponential xmin', results.stretched_exponential.xmin)
    print('**truncated_power_law xmin', results.truncated_power_law.xmin)
    print('truncated_power_law alfa', results.truncated_power_law.alpha)


def _14(graph):
    if nx.is_directed(graph):
        print('Ispitivanje ulaznog stepena čvora')
        plot_degree_distribution(graph, p=1)
        n = graph.number_of_nodes()
        m = graph.number_of_edges()
        H = nx.erdos_renyi_graph(n, 2 * float(m) / (n * (n - 1)), directed=True)
        plot_degree_distribution(H, p=1)
        cumulative_degree_distribution(graph, p=1)
        power_law(graph, p=1)
        print('Ispitivanje izlaznog stepena čvora')
        plot_degree_distribution(graph, p=-1)
        plot_degree_distribution(H, p=-1)
        cumulative_degree_distribution(graph, p=-1)
        power_law(graph, p=-1)
    else:
        plot_degree_distribution(graph)
        # plot_degree_distribution(graph, weight='weight')
        # n = graph.number_of_nodes()
        # m = graph.number_of_edges()
        # Gnm = nx.gnm_random_graph(n, m)
        # plot_degree_distribution(Gnm)
        # H = nx.erdos_renyi_graph(n, 2 * float(m) / (n * (n - 1)))
        # plot_degree_distribution(H)
        # cumulative_degree_distribution(graph)
        power_law(graph)
        # plot_degree_distribution(graph, 'weight')
        # plot_degree_distribution(graph)
        # degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
        # fit_alpha, fit_loc, fit_beta = stats.gamma.fit(degree_sequence)
        # print(fit_alpha, fit_loc, fit_beta)


# def get_neighbours_from_the_hub_to_other_hubs(graph, node, hubs):
#     neighbours = []
#     for hub in hubs:
#         if nx.edge[node, hub]:
#             neighbours.append(hub)
#     return neighbours
#
#
# def get_neighbours_from_other_hubs_to_the_hub(graph, hub, hubs):
#     neighbours = []
#     for hub in hubs:
#         if nx.edge[node, hub]:
#             neighbours.append(hub)
#     return neighbours


def _15(graph, net_type_value):
    # if net_type_value != NetType.USER_NET.value:
    #     print(f'Autoriteti i habovi su karakteristični za usmerene mreže. Stoga ih nema potrebe ispitivati kod { net_type_value } mreže jer je ona neusmerena.')
    #     return
    # # kod neusmerenog grafa hub i authorities su isti
    # print('0')
    hubs, authorities = nx.hits(graph)
    print('10 čvorova koji predstavljaju najznačajnije habove:')
    print_top_n_authors_from_dictionary(hubs, 10)
    print('10 čvorova koji predstavljaju najznačajnije autoritete:')
    print_top_n_authors_from_dictionary(authorities, 10)
    #
    # # provera da li su habovi povezani - gledamo podgraf ciji su cvorovi samo habovi i ko je povezan
    sorted_dictionary = dict(sorted(hubs.items(), key=itemgetter(1), reverse=True)[:10])
    top_10_hub_nodes = []
    for item in sorted_dictionary:
        top_10_hub_nodes.append(repr(item).strip("'"))
    subgraph_hubs = nx.subgraph(graph, top_10_hub_nodes)
    print('*', top_10_hub_nodes)
    print('1')
    print(nx.info(subgraph_hubs))
    print('2')
    print(nx.edges(subgraph_hubs))
    print('3')
    for hub in top_10_hub_nodes:
        neighbours = list(subgraph_hubs.neighbors(hub))
        print(hub, len(neighbours), neighbours)
    # # provera da li su autoriteti povezani - gledamo podgraf ciji su cvorovi samo habovi i ko je povezan
    sorted_dictionary = dict(sorted(authorities.items(), key=itemgetter(1), reverse=True)[:10])
    top_10_hub_authorities = []
    for item in sorted_dictionary:
        top_10_hub_authorities.append(repr(item).strip("'"))
    subgraph_top_10_hub_authorities = nx.subgraph(graph, top_10_hub_authorities)
    print('*', top_10_hub_nodes)
    print('1')
    print(nx.info(subgraph_hubs))
    print('2')
    print(nx.edges(subgraph_hubs))
    print('3')
    for auth in top_10_hub_authorities:
        neighbours = list(subgraph_hubs.neighbors(auth))
        print(hub, len(neighbours), neighbours)
    #
    # # provera da li habovi pripadaju periferiji
    # top_10_hub_nodes = ['FokkeNews', 'yehauma', 'MercurialMadnessMan', 'neuromonkey', 'ContentWithOurDecay', 'BritishEnglishPolice', 'MrDanger', 'movzx', 'Sutibu', 'krispykrackers']
    periphery = nx.periphery(graph)
    for hub in top_10_hub_nodes:
        if hub in periphery:
            print(f'Hab {hub} pripada periferiji')
        else:
            print(f'Hab {hub} ne pripada periferiji')
    k_core = nx.k_core(graph)
    for hub in top_10_hub_nodes:
        if hub in k_core:
            print(f'Hab {hub} pripada k_core')
        else:
            print(f'Hab {hub} ne pripada k_core')


def read_s_net_giant_component_graph(graph):
    if os.path.isfile(S_NET_GIANT_COMPONENT_FILE_PATH):
        giant_component = nx.read_gml(S_NET_GIANT_COMPONENT_FILE_PATH)
    else:
        giant_component = get_giant_component(graph)
        nx.write_gml(giant_component, S_NET_GIANT_COMPONENT_FILE_PATH)
    return giant_component


def read_s_net_f_giant_component_graph(graph):
    if os.path.isfile(S_NET_F_GIANT_COMPONENT_FILE_PATH):
        giant_component = nx.read_gml(S_NET_F_GIANT_COMPONENT_FILE_PATH)
    else:
        giant_component = get_giant_component(graph)
        nx.write_gml(giant_component, S_NET_F_GIANT_COMPONENT_FILE_PATH)
    return giant_component


def read_user_net_giant_component_graph(graph):
    if os.path.isfile(USER_NET_GIANT_COMPONENT_FILE_PATH):
        giant_component = nx.read_gml(USER_NET_GIANT_COMPONENT_FILE_PATH)
    else:
        giant_component = get_giant_component(graph)
        nx.write_gml(giant_component, USER_NET_GIANT_COMPONENT_FILE_PATH)
    return giant_component


def read_user_net_erdos_renyi_graph():
    if os.path.isfile(USER_NET_ERDOS_RENY_FILE_PATH):
        H = nx.read_gml(USER_NET_ERDOS_RENY_FILE_PATH)
    else:
        n = 97532
        m = 2895955
        print('3')
        H = nx.erdos_renyi_graph(n, 2 * float(m) / (n * (n - 1)))
        print('4')
        nx.write_gml(H, USER_NET_ERDOS_RENY_FILE_PATH)
        print('5')
    return H


def basic_characterization_of_modeled_networks(graph, net_type_value):
    print('abc')
    print(f'Osnovna karakterizacija modelovane {net_type_value} mreže ')
    # _7(graph, net_type_value)
    # _8(graph, net_type_value)
    # _9(graph, net_type_value)
    if net_type_value == NetType.S_NET.value:
        print(f'Za { net_type_value } mrežu se nadalje ispituje njena gigantska komponenta.')
        graph = read_s_net_giant_component_graph(graph)
    elif net_type_value == NetType.S_NET_F.value:
        print(f'Za { net_type_value } mrežu se nadalje ispituje njena gigantska komponenta.')
        graph = read_s_net_f_giant_component_graph(graph)
    elif net_type_value == NetType.USER_NET.value:
        print(f'Za {net_type_value} mrežu se nadalje ispituje njena gigantska komponenta.')
        graph = read_user_net_giant_component_graph(graph)
    # _10(graph, net_type_value)
    # # _12(graph)
    # _13(graph)
    # # _14(graph)
    _15(graph, net_type_value)
    # print('lala')
