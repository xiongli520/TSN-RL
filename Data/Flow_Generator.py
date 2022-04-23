import json
import os
from Data.Graph import *
import random
from Data.Route import *
from main.param import *

class Flow_Generator:
    def __init__(self, graph):
        self.graph = graph
        self.node_num = graph.node_num
        self.end_num = 0
        self.switch_num = 0
        self.end_node_index_list = []
        self.switch_node_index_list = []
        for node in graph.nodes:
            if node.isEndNode==1:
                self.end_num+=1
                self.end_node_index_list.append(node.id)
            elif node.isSwitchNode==1:
                self.switch_num+=1
                self.switch_node_index_list.append(node.id)
            else:
                print('error in flow generator init....')


        self.tt_flow_cycle_option = args.tt_flow_cycles
        self.tt_num = args.tt_num
        self.delay_min = args.delay_min
        self.delay_max = args.delay_max
        self.pkt_len_min = args.pkt_len_min
        self.pkt_len_max = args.pkt_len_max
        self.tt_flows = {}


    def generator_flow(self):
        for i in range(self.tt_num):
            self.tt_flow[str(i)] = {}
            src = random.choice(self.end_node_index_list)
            des = random.choice(self.end_node_index_list)
            while src == des:
                des = random.choice(self.end_node_index_list)
            cycle = random.choice(self.tt_flow_cycle_option)
            delay = random.randint(self.delay_min, self.delay_max)
            pkt_len = random.randint(self.pkt_len_min, self.pkt_len_max)

            self.tt_flow[str(i)]['src'] = src
            self.tt_flow[str(i)]['des'] = des
            self.tt_flow[str(i)]['cycle'] = cycle
            self.tt_flow[str(i)]['delay'] = delay
            self.tt_flow[str(i)]['pkt_len'] = pkt_len

    def writeToFile(self, fileName):
        '''
        将网络结构信息写入文件中保存
        :param fileName:
        :return:
        '''
        if not os.path.exists('./resource/{}'.format(fileName)):
            os.makedirs('./resource/{}'.format(fileName))
        # if self.node_mat is not None:
            # np.save('../resource/{}/node_mat.npy'.format(fileName), self.node_mat)
        # if self.node_info:
        #     json.dump(self.node_info, open('../resource/{}/node_info.json'.format(fileName), "w"), indent=4)
        if self.tt_flow:
            json.dump(self.tt_flow, open('../resource/{}/tt_flow.json'.format(fileName), "w"), indent=4)
        # if self.paths_table:
        #     json.dump(self.paths_table, open('../resource/{}/paths_table.json'.format(fileName), "w"), indent=4)
        # if self.edges_info:
        #     json.dump(self.edges_info, open('../resource/{}/edges_info.json'.format(fileName), "w"), indent=4)

    def readFromFile(self, fileName):
        '''
        从文件中加载网络结构信息
        :param fileName:
        :return:
        '''
        # self.node_mat = np.load('../resource/{}/node_mat.npy'.format(fileName))
        # self.node_info = json.load(open('../resource/{}/node_info.json'.format(fileName)))
        self.tt_flow = json.load(open('../resource/{}/tt_flow.json'.format(fileName)))
        # self.paths_table = json.load(open('../resource/{}/paths_table.json'.format(fileName)))
        # self.edges_info = json.load(open('data/{}/edges_info.json'.format(fileName)))

if __name__ == '__main__':
    fo_network_info = open("./network_info.txt", "r")
    fo_node_info = open("./node_info.txt", "r")
    node_num = int(fo_network_info.readline())
    # print(type(node_num))
    # print(node_num)
    node_num_ = int(fo_node_info.readline())
    edge_num = int(fo_network_info.readline())
    # print(edge_num)
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
    print(graph.get_all_connection_list())
    print(graph.adj_mat)
    rt = Route(graph)
    print(rt.get_path(0, 7))