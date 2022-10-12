import math
import networkx as nx
import pandas as pd
from datetime import datetime
import os

from src.analysis.helper_analysis.basic_analysis import read_user_net_giant_component_graph, \
    USER_NET_GIANT_COMPONENT_FILE_PATH, _15, _10, _7, _8, _9, average_shortest_path_and_diameter_for_erdos_reny, \
    are_nodes_with_high_lcc_connected, classify_data_in_n_classes_and_calculate_mixing_matrix, _12, _14
from src.analysis.helper_analysis.centrality_analysis import _16
from src.analysis.net_analysis import NetType, net_analysis
from src.analysis.statistical_analysis import read_submissions_and_comments, Type

USER_NET_FILE_PATH_WITH_SELF_LOOPS = '../../results/nets/user_net_with_self_loops.gml'
# USER_NET_FILE_PATH = '../../results/nets/user_net.gml'
USER_NET_FILE_PATH = '../../results/nets/user_net_with_self_loops.gml'
date_to_compare = datetime.strptime('2009-1-1', '%Y-%m-%d')
alpha = 0.5

submissions = pd.DataFrame()
comments = pd.DataFrame()
added_nodes = set()


def add_or_update_edge_in_user_net(user_net, p_type, parent_author_name, c_author_name):
    if c_author_name == '[deleted]':
        return
    if (parent_author_name is not None) and (parent_author_name != '[deleted]') and (c_author_name != parent_author_name): # zakomentarisatio poslenji uslov ako zelimo da ima self loops
        if user_net.get_edge_data(c_author_name, parent_author_name, key=p_type) is not None:
            curr_weight = user_net.get_edge_data(c_author_name, parent_author_name, key=p_type)['weight']
            user_net.add_edge(c_author_name, parent_author_name, key=p_type, weight=curr_weight+1)
        else:
            user_net.add_edge(c_author_name, parent_author_name, key=p_type, weight=1)
    else:
        if c_author_name not in user_net:
            user_net.add_node(c_author_name)


def make_user_net_graph():
    global submissions, comments
    submissions, comments = read_submissions_and_comments()
    s = submissions[submissions.author != '[deleted]'][['id', 'author']].drop_duplicates().reset_index()
    s_id = s.id
    s_author_names = dict(zip(s_id, s.author))
    c = comments[comments.author != '[deleted]'][['id', 'parent_id', 'author']].drop_duplicates().reset_index()
    c_id = c.id
    c_parent_ids = dict(zip(c_id, c.parent_id))
    c_author_names = dict(zip(c_id, c.author))

    user_net = nx.MultiDiGraph()
    for i in range(0, len(c_id)):
        c_id_curr = c_id[i]
        c_parent_id = c_parent_ids[c_id_curr]
        c_author_name = c_author_names[c_id_curr]
        parent_type = c_parent_id[:2]
        parent_id = c_parent_id[3:]
        if parent_type == 't1':     # ako je parent komentar stvaramo vezu ka komentaru i sabreditu gde je taj komentar postavljen
            parent_author_name = c_author_names.get(parent_id)
            add_or_update_edge_in_user_net(user_net, Type.COMMENT.value, parent_author_name, c_author_name)
            print(i, Type.COMMENT.value, c_parent_ids[c_id_curr], parent_id, parent_author_name, c_author_name)
        else:
            # print('&3')             # ako je parent sabredit stvaramo vezu ka sabreditu gde je taj komentar postavljen
            parent_author_name = s_author_names.get(parent_id)
            add_or_update_edge_in_user_net(user_net, Type.SUBMISSION.value, parent_author_name, c_author_name)
            print(i, Type.SUBMISSION.value, c_parent_ids[c_id_curr], parent_id, parent_author_name, c_author_name)
        print(i, '/', len(c_id))
    print(user_net.edges.data())
    print(nx.info(user_net))
    nx.write_gml(user_net, USER_NET_FILE_PATH)
    return user_net


def read_user_net_graph():
    if os.path.isfile(USER_NET_FILE_PATH):
        user_net = nx.read_gml(USER_NET_FILE_PATH)
    else:
        user_net = make_user_net_graph()
    return user_net


def user_net_analysis():
    print('123')
    user_net = read_user_net_graph()
    # print(nx.get_edge_attributes(user_net, 'weight'))
    # print(nx.info(user_net))
    # print(nx.get_edge_attributes(user_net, 'key'))
    # _7(user_net, NetType.USER_NET.value)
    # _8(user_net, NetType.USER_NET.value)
    the_largest_component_in_graph = nx.read_gml('../../results/nets/giant_component/user_net_giant_component.gml')
    print('1')
    print(f'Gustina gigantske komponente mreže je {round(nx.density(the_largest_component_in_graph), 6)}.')
    print(f'Prosečna distanca u gigantskoj komponenti mreže je {round(nx.average_shortest_path_length(the_largest_component_in_graph), 3)},')
    print(f'dok je dijametar {nx.diameter(the_largest_component_in_graph)}.')
    average_shortest_path_and_diameter_for_erdos_reny(the_largest_component_in_graph)
    # _9(user_net, NetType.USER_NET.value)
    # print(user_net.get_edge_data('fathafiga', 'collegepill', key=Type.COMMENT.value))
    # print(user_net.get_edge_data('fathafiga', 'collegepill', key=Type.SUBMISSION.value))
    # print("All edges with key 2:", [(i, j, k) for i, j, k in user_net.edges if k == Type.COMMENT.value])

    # net_analysis(user_net, NetType.USER_NET.value)

    # if os.path.isfile(USER_NET_GIANT_COMPONENT_FILE_PATH):
    #     graph = nx.read_gml(USER_NET_GIANT_COMPONENT_FILE_PATH)
    #     print(nx.info(graph))
    #     _15(graph, NetType.USER_NET.value)

    # global submissions, comments
    # submissions, comments = read_submissions_and_comments()
    # submissions_num_of_users = submissions.loc[:, ['author']]
    # comments_num_of_users = comments.loc[:, ['author']]
    # t = pd.concat([submissions_num_of_users, comments_num_of_users])
    # # t = comments_num_of_users
    # t = t.loc[t['author'] != '[deleted]']
    # t = t.drop_duplicates()
    # print('*', len(t))

    # _7(user_net, NetType.USER_NET.value)
    # _8(user_net, NetType.USER_NET.value)
    # _9(user_net, NetType.USER_NET.value)
    # * 88570 su razliciti autori komentara


# user_net_analysis()
user_net = nx.read_gml('../../results/nets/giant_component/user_net_giant_component.gml')
# _10(user_net, NetType.USER_NET.value)
_14(user_net)
# classify_data_in_n_classes_and_calculate_mixing_matrix(user_net, num_of_classes=6)