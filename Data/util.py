import json
from Data.Graph_new import *

def read_tt_flows_from_file():
    '''
    从文件中加载网络结构信息
    :param fileName:
    :return:
    '''
    # self.node_mat = np.load('../resource/{}/node_mat.npy'.format(fileName))
    # self.node_info = json.load(open('../resource/{}/node_info.json'.format(fileName)))
    tt_flows = json.load(open('/Data/resource/unprocess_flow/tt_flows.json'))
    # tt_flows_new = json.load(open('D:\\MyRL\\TSN-RL\\Data\\resource\\info\\tt_flows_new.json'))
    # self.paths_table = json.load(open('../resource/{}/paths_table.json'.format(fileName)))
    # self.edges_info = json.load(open('data/{}/edges_info.json'.format(fileName)))
    return tt_flows

def get_edge_index(edges_info, src, des):
    '''
    根据源节点和下一节点索引找到对应边的index
    :param edges_info: 边的所有信息
    :param src: 源点
    :param des: 下一节点
    :return:
    '''
    res = -1
    for index, edge in edges_info.items():
        if edge['src'] == src and edge['des'] == des:
            res = int(index)

    return res

def get_max_hop(tt_flows):
    '''
    获得tt流最大跳数
    :return:
    '''
    max_hop = -1
    for flow in tt_flows.values():
        path_id = flow['path_id']
        hop = len(flow['paths'][path_id]) - 1
        if max_hop < hop:
            max_hop = hop
    return max_hop

def generate_graph(network_info_file_name, node_info_file_name):
    '''
    通过网络信息和节点信息生成graph图
    :param network_info_file_name:网络信息文件名字，需要带上后缀
    :param node_info_file_name: 节点信息文件名字，需要带上后缀
    :return:
    '''
    fo_network_info = open("../Data/resource/info/{}".format(network_info_file_name), "r")
    fo_node_info = open("../Data/resource/info/{}".format(node_info_file_name), "r")
    node_num = int(fo_network_info.readline())
    # print(type(node_num))
    # print(node_num)
    node_num_ = int(fo_node_info.readline())
    edge_num = int(fo_network_info.readline())
    # print(edge_num)
    connection_info = []
    nodes_info = []
    for i in range(edge_num):
        ss = fo_network_info.readline()
        node1_index, node2_index = map(int, ss.split())
        connection_info.append((node1_index, node2_index))
    for i in range(node_num_):
        index, is_end_node, is_switch_node = map(int, fo_node_info.readline().split())
        nodes_info.append((index, is_end_node, is_switch_node))

    fo_node_info.close()
    fo_network_info.close()

    graph = Graph_new(node_num, edge_num, connection_info, nodes_info)
    return graph

if __name__ == '__main__':
    print(__file__)