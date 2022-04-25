import json
from Data.Flow_Generator import *

class DoC_Node:
    def __init__(self, id):
        self.id = id
        self.connection_list = []

class DoC_Graph:
    def __init__(self, fg):
        self.fg = fg
        self.tt_num = fg.tt_num
        self.tt_flows = fg.tt_flows
        self.doc_nodes = []
        for i in range(self.tt_num):
            node = DoC_Node(i)
            self.doc_nodes.append(node)
        self.get_stream_graph()

    def get_stream_graph(self):
        for i in range(self.tt_num):
            for j in range(i+1, self.tt_num):
                if i == j:
                    continue
                else:
                    flow1 = self.tt_flows[str(i)]
                    flow2 = self.tt_flows[str(j)]
                    doc = self.doc_cal(flow1, flow2)
                    if doc != 0:
                        self.doc_nodes[i].connection_list.append((j, doc))
                        self.doc_nodes[j].connection_list.append((i, doc))


    def doc_cal(self, flow1, flow2):
        '''
        计算两条流的DoC
        :param flow1:
        :param flow2:
        :return:
        '''

        path1_id = flow1['path_id']
        path1 = flow1['paths'][path1_id]
        pkt_len1 = flow1['pkt_len']
        period1 = flow1['cycle']

        path2_id = flow2['path_id']
        path2 = flow2['paths'][path2_id]
        pkt_len2 = flow2['pkt_len']
        period2 = flow2['cycle']

        path_overlap_num = self.doc_path_overlap(path1, path2)
        return path_overlap_num * (pkt_len1*pkt_len2)/(period1*period2)


    def doc_path_overlap(self, path1, path2):
        '''
        计算两条路径重复节点的数目
        :param path1:
        :param path2:
        :return:
        '''
        return len(set(path1)&set(path2))


if __name__ == '__main__':
    fo_network_info = open("../info/network_info.txt", "r")
    fo_node_info = open("../info/node_info.txt", "r")
    node_num = int(fo_network_info.readline())
    node_num_ = int(fo_node_info.readline())
    edge_num = int(fo_network_info.readline())
    graph = Graph(node_num)
    for i in range(edge_num):
        ss = fo_network_info.readline()
        node1_index, node2_index = map(int, ss.split())
        graph.add_edge(node1_index, node2_index)
    for i in range(node_num_):
        index, is_end_node, is_switch_node = map(int, fo_node_info.readline().split())
        if is_end_node == 1:
            graph.nodes[index].set_end_node()
        if is_switch_node == 1:
            graph.nodes[index].set_switch_node()

    fo_node_info.close()
    fo_network_info.close()

    flow_generator = Flow_Generator(graph)
    flow_generator.generator_flow()
    doc_graph = DoC_Graph(flow_generator)
    for node in doc_graph.doc_nodes:
        print(node.connection_list)