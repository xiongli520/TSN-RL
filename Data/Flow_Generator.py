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
        # self.pkt_len_min = args.pkt_len_min
        # self.pkt_len_max = args.pkt_len_max
        self.tt_flows = {}

        if os.path.exists('./resource/info/tt_flows.json'):
           self.read_from_file()
        else:
            self.generator_flow()
            self.write_to_file()

    def generator_flow(self):
        rt = Route(self.graph)
        for i in range(self.tt_num):
            self.tt_flows[str(i)] = {}
            src = random.choice(self.end_node_index_list)
            des = random.choice(self.end_node_index_list)
            while src == des:
                des = random.choice(self.end_node_index_list)
            cycle = random.choice(self.tt_flow_cycle_option)
            delay = random.randint(self.delay_min, self.delay_max)
            # pkt_len = random.randint(self.pkt_len_min, self.pkt_len_max)
            pkt_len_parameter = random.random()/3
            while pkt_len_parameter<0.06:
                pkt_len_parameter = random.random()/3
            pkt_len = round(cycle*pkt_len_parameter)
            # if pkt_len<10:
            #     pkt_len = pkt_len*2
            rt.get_path(src, des)
            path_id = random.randint(0, len(rt.paths)-1)
            self.tt_flows[str(i)]['src'] = src
            self.tt_flows[str(i)]['des'] = des
            self.tt_flows[str(i)]['cycle'] = cycle
            self.tt_flows[str(i)]['delay'] = delay
            self.tt_flows[str(i)]['pkt_len'] = pkt_len
            self.tt_flows[str(i)]['paths'] = rt.paths
            self.tt_flows[str(i)]['path_id'] = path_id


    def write_to_file(self):
        '''
        将网络结构信息写入文件中保存
        :param fileName:
        :return:
        '''
        if not os.path.exists('./resource/info'):
            os.makedirs('./resource/info')
        # if self.node_mat is not None:
            # np.save('../resource/{}/node_mat.npy'.format(fileName), self.node_mat)
        # if self.node_info:
        #     json.dump(self.node_info, open('../resource/{}/node_info.json'.format(fileName), "w"), indent=4)
        if self.tt_flows:
            json.dump(self.tt_flows, open('./resource/info/tt_flows.json', "w"), indent=4)
        # if self.paths_table:
        #     json.dump(self.paths_table, open('../resource/{}/paths_table.json'.format(fileName), "w"), indent=4)
        # if self.edges_info:
        #     json.dump(self.edges_info, open('../resource/{}/edges_info.json'.format(fileName), "w"), indent=4)

    def read_from_file(self):
        '''
        从文件中加载网络结构信息
        :param fileName:
        :return:
        '''
        # self.node_mat = np.load('../resource/{}/node_mat.npy'.format(fileName))
        # self.node_info = json.load(open('../resource/{}/node_info.json'.format(fileName)))
        self.tt_flows = json.load(open('./resource/info/tt_flows.json'))
        # self.paths_table = json.load(open('../resource/{}/paths_table.json'.format(fileName)))
        # self.edges_info = json.load(open('data/{}/edges_info.json'.format(fileName)))



if __name__ == '__main__':
    fo_network_info = open("./resource/info/network_info.txt", "r")
    fo_node_info = open("./resource/info/node_info.txt", "r")
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


