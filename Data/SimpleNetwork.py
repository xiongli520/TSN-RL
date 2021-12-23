import json
import numpy as np
import random
import os
from Data.Edge import *
from Data.Node import *
import copy
import sys
from main.param import *


class SimpleNetwork:
    def __init__(self):
        self.node_num = 0
        self.end_num = 0
        self.switch_num = 0
        self.node_mat = None
        self.node_info = {}
        self.tt_flow = {}
        self.tt_num = 0
        self.edge_num = 0
        self.max_hop = 0

        self.tt_flow_cycle_option = args.tt_flow_cycles
        self.nodes = {}
        self.edges = {}
        self.edges_info = {}

    def generateAll(self, fileName, node_num = 10, end_num = 8, switch_num = 2, rand_min = 30, rand_max = 100, tt_num = 10,
                     delay_min = 2048, delay_max = 4096, pkt_min = 72, pkt_max = 1526, dynamic = False):

        print('SimpleNetwork is generating...')
        self.node_num = node_num
        self.end_num = end_num
        self.switch_num = switch_num
        self.tt_num = tt_num

        if dynamic:
            self.ttFlowGenerate(tt_num=tt_num, delay_min=delay_min, delay_max=delay_max,
                                pkt_min=pkt_min, pkt_max=pkt_max, dynamic=dynamic)
            self.nodeInforGenerate(rand_min=rand_min, rand_max=rand_max, dynamic=dynamic)
            self.nodeMatGenerate(node_num=node_num, end_num=end_num, switch_num=switch_num, dynamic=dynamic)
            self.dijkstra()
            self.get_nodes()
            self.get_edges()
            self.tt_flow_with_route()
            self.get_max_hop()
            self.writeToFile(fileName=fileName)
        else:
            self.readFromFile(fileName)
            self.get_nodes()
            self.get_edges()
            self.get_max_hop()

        print('function generateAll finished!!!')

    def nodeMatGenerate(self, node_num, end_num, switch_num, dynamic):
        '''
        因为SimpleNetwork是确定的，所以它的节点连接矩阵也是确定
        :return: 
        '''
        assert node_num > 1, '节点数太少了!!!'
        self.node_num = node_num
        self.end_num = end_num
        self.switch_num = switch_num
        if dynamic:
            self.node_mat = [[0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                             [1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1, 1, 1, 1, 1, 0]]

    def ttFlowGenerate(self, tt_num, delay_min, delay_max, pkt_min, pkt_max, dynamic):
        '''
        产生随机TT流信息
        :param tt_num: 
        :param delay_min: 
        :param delay_max: 
        :param pkt_min: 
        :param pkt_max: 
        :param dynamic: 
        :return: 
        '''
        if dynamic:
            for i in range(self.tt_num):
                self.tt_flow[str(i)] = {}
                src = random.randint(0, self.end_num)
                des = random.randint(0, self.end_num)
                while src == des:
                    des = random.randint(0, self.end_num)
                cycle = random.choice(self.tt_flow_cycle_option)
                delay = random.randint(delay_min, delay_max)
                pkt_len = random.randint(pkt_min, pkt_max)

                self.tt_flow[str(i)]['src'] = src
                self.tt_flow[str(i)]['des'] = des
                self.tt_flow[str(i)]['cycle'] = cycle
                self.tt_flow[str(i)]['delay'] = delay
                self.tt_flow[str(i)]['pkt_len'] = pkt_len

    def nodeInforGenerate(self, rand_min, rand_max, dynamic):
        '''
        随机产生各个节点的buffer数目
        :param rand_min: 
        :param rand_max: 
        :param dynamic: 
        :return: 
        '''
        self.rand_min = rand_min
        self.rand_max = rand_max
        if dynamic:
            self.node_info = {}
            for i in range(self.node_num):
                self.node_info[str(i)] = random.randint(rand_min, rand_max)

    def writeToFile(self, fileName):
        '''
        将网络结构信息写入文件中保存
        :param fileName: 
        :return: 
        '''
        if not os.path.exists('../resource/{}'.format(fileName)):
            os.makedirs('../resource/{}'.format(fileName))
        if self.node_mat is not None:
            np.save('../resource/{}/node_mat.npy'.format(fileName), self.node_mat)
        if self.node_info:
            json.dump(self.node_info, open('../resource/{}/node_info.json'.format(fileName), "w"), indent=4)
        if self.tt_flow:
            json.dump(self.tt_flow, open('../resource/{}/tt_flow.json'.format(fileName), "w"), indent=4)
        if self.paths_table:
            json.dump(self.paths_table, open('../resource/{}/paths_table.json'.format(fileName), "w"), indent=4)
        if self.edges_info:
            json.dump(self.edges_info, open('../resource/{}/edges_info.json'.format(fileName), "w"), indent=4)

    def readFromFile(self, fileName):
        '''
        从文件中加载网络结构信息
        :param fileName: 
        :return: 
        '''
        self.node_mat = np.load('../resource/{}/node_mat.npy'.format(fileName))
        self.node_info = json.load(open('../resource/{}/node_info.json'.format(fileName)))
        self.tt_flow = json.load(open('../resource/{}/tt_flow.json'.format(fileName)))
        self.paths_table = json.load(open('../resource/{}/paths_table.json'.format(fileName)))
        # self.edges_info = json.load(open('data/{}/edges_info.json'.format(fileName)))


    def dijkstra(self):
        '''
        得到所有节点的路由信息表
        :return: 
        '''
        self.paths_table = []
        self.paths_distance_table = []
        for i in range(len(self.node_mat)):
            path_distance_table, path_table = self.dijkstra_single(src=i)
            self.paths_table.append(path_table)
            self.paths_distance_table.append(path_distance_table)


    def dijkstra_single(self, src):
        '''
        通过源节点编号，得到该节点到所有的目的节点的路由
        :param src: 源节点index
        :return: 
        '''
        length = len(self.node_mat)
        node_mat_temp = copy.deepcopy(self.node_mat)
        for i in range(length):
            for j in range(length):
                if node_mat_temp[i][j] == 0 and j != i:
                    node_mat_temp[i][j] = 999

        nodes = [i for i in range(length)]

        visited = [src]
        path = {str(src): {str(src): []}}
        nodes.remove(src)
        distance_node_mat = {str(src): 0}
        pre = next = src

        while nodes:
            distance = float('inf')
            for v in visited:
                for d in nodes:
                    new_dist = node_mat_temp[src][v] + node_mat_temp[v][d]
                    if new_dist <= distance:
                        distance = new_dist
                        next = d
                        pre = v
                        node_mat_temp[src][d] = new_dist

            path[str(src)][str(next)] = [i for i in path[str(src)][str(pre)]]
            path[str(src)][str(next)].append(next)

            distance_node_mat[next] = distance

            visited.append(next)
            nodes.remove(next)

        return distance_node_mat, path

    def get_edges(self):
        '''
        初始化连接边
        :return: 
        '''
        if len(self.node_mat)>0 :
            index = 0
            for i in range(len(self.node_mat)):
                for j in range(len(self.node_mat)):
                    if self.node_mat[i][j] == 1:
                        self.edges[index] = Edge(index=index, start_node=i, end_node=j)
                        self.edges_info[str(index)] = {}
                        self.edges_info[str(index)]['src'] = i
                        self.edges_info[str(index)]['des'] = j
                        index+=1
            self.edge_num = index
        else:
            print('Havent generated node_mat')

    def get_nodes(self):
        '''
        初始化节点
        :return: 
        '''
        if len(self.node_mat)>0 and self.node_info:
            for i in range(len(self.node_mat)):
                    self.nodes[i] = Node(index=i, capacity=self.node_info[str(i)])

        else:
            print('Havent generated node_mat')

    def tt_flow_with_route(self):
        '''
        将生成的TT流附带上它的路由信息，将路由转化为Edge编号
        :return:
        '''
        if self.tt_flow and self.paths_table:
            index = 0
            for single_flow in self.tt_flow.values():
                src = single_flow['src']
                des = single_flow['des']
                node_path = [src]
                table = self.paths_table[src]
                node_path.extend(table[str(src)][str(des)])
                single_flow_edge_path = self.node_path2edge_path(node_path)
                self.tt_flow[str(index)]['edge_path'] = single_flow_edge_path
                index+=1
        else:
            print("tt_flow_with_route ERROR")

    def node_path2edge_path(self, path):
        '''
        输入一条流的路由
        将节点表示的路由，转为边路由
        :param path: 
        :return: 
        '''
        if path:
            edge_path = []
            for i in range(len(path)-1):
                src = path[i]
                des = path[i+1]
                edge_id = self.node_match_edge(src, des)
                edge_path.append(edge_id)
            return edge_path

        else:
            print("节点路由转化为边路由出错")
            return [-1]
    def node_match_edge(self, src, des):
        '''
        通过源节点和目的节点的index找到对应的edge的index
        :param src: 
        :param des: 
        :return: 
        '''
        if self.edges:
            for edge in self.edges.values():
                if edge.start_node == src and edge.end_node == des:
                    return edge.id

        return -1

    def get_max_hop(self):
        '''
        获得tt流最大跳数
        :return: 
        '''
        for flow in self.tt_flow.values():
            if self.max_hop < len(flow['edge_path']):
                self.max_hop = len(flow['edge_path'])


    def occupy_edge_slot(self, edge_index, flow_length, action, flow_end_slot):
        '''
        
        :param edge_index: 边索引指数
        :param flow_length: 流长度
        :param action: 流id
        :param flow_end_slot:该流在最后的调度结束时隙 
        :return: 
        '''
        edge = self.edges[edge_index]
        # note 必须先使用record_occupy_fast再使用occupy_slot_fast
        # edge.record_occupy_fast(flow_length=flow_length, action=action, flow_end_slot=flow_end_slot)
        result = edge.occupy_slot_fast(action=action, flow_length=flow_length, flow_end_slot=flow_end_slot)
        return result

    def save_schedule_result(self, i):
        '''
        完成调度后实现调度结果的保存和实现
        :return: 
        '''
        schedule_result = {}
        for edge in self.edges.values():
            schedule_result[edge.id] = edge.time_slot_state
        if not os.path.exists('../result'):
            os.makedirs('../result')
        if schedule_result:
            json.dump(schedule_result, open('../result/schedule_result_{}.json'.format(i), "w"), indent=4)





def main():
    node_num = args.node_num
    tt_num = args.tt_num
    end_num = args.end_num
    switch_num = args.switch_num

    pkt_len_min = args.pkt_len_min
    pkt_len_max = args.pkt_len_max

    data = SimpleNetwork()
    data.generateAll(fileName='SimpleNetwork',node_num=node_num, end_num=end_num, switch_num=switch_num, rand_min=10,
                     rand_max=30, tt_num=tt_num, delay_min=1024, delay_max=2048,
                     pkt_min=pkt_len_min, pkt_max=pkt_len_max, dynamic=True)


if __name__ == '__main__':
    main()