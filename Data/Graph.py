from Data.Node import *
from Data.Edge import *
import os
import json
class Graph:
    def __init__(self, node_num):
        self.node_num = node_num
        self.edge_num = 0
        # 邻接表
        self.adj = []
        self.adj_mat = []
        self.nodes = []
        self.edges_info = {}
        self.edges = []
        for i in range(self.node_num):
            node_i = Node(i, 10)
            self.nodes.append(node_i)
            self.adj.append(self.nodes[i].connection_list)
        # 初始化邻接矩阵 和 节点的访问其他节点记录
        for i in range(self.node_num):
            tmp = []
            for j in range(self.node_num):
                tmp.append(0)
            self.adj_mat.append(tmp)

        for i in range(self.node_num):
            tmp = []
            for j in range(self.node_num):
                tmp.append(0)
            self.nodes[i].set_all_visited_list(tmp)

    def add_edge(self, node1_index, node2_index):
        '''
        将节点1和节点2 进行连接，并且在节点的连接表中添加各自的节点索引
        :param node1:
        :param node2:
        :return:
        '''
        if(node1_index>=0 and node1_index<self.node_num and node2_index>=0 and node2_index<self.node_num):
            self.nodes[node1_index].connection_list.append(node2_index)
            self.nodes[node2_index].connection_list.append(node1_index)
            self.adj_mat[node1_index][node2_index] = 1
            self.adj_mat[node2_index][node1_index] = 1
            self.edge_num+=2
            return True
        else:
            print('超过节点索引范围')
            return False

    def get_all_connection_list(self):
        '''
        得到整个图的邻接表
        :return:
        '''
        # connection_lists = []
        # for i in range(self.node_num):
        #     connection_lists.append(self.nodes[i].connection_list)
        # return connection_lists
        return self.adj

    def get_connection_list(self, index):
        '''
        得到某一个节点的邻接表
        :param index:
        :return:
        '''
        if index<self.node_num and index>=0:
            return self.nodes[index].connection_list
        else:
            print('超过节点索引范围')
            return [-1]

    def get_edges(self):
        if len(self.adj_mat)>0 :
            index = 0
            for i in range(len(self.adj_mat)):
                for j in range(len(self.adj_mat)):
                    if self.adj_mat[i][j] == 1:
                        self.edges[index] = Edge(index=index, start_node=i, end_node=j)
                        self.edges_info[str(index)] = {}
                        self.edges_info[str(index)]['src'] = i
                        self.edges_info[str(index)]['des'] = j
                        index+=1
            self.edge_num = index

        if not os.path.exists('D:\\MyRL\\TSN-RL\\Data\\resource\\info'):
            os.makedirs('D:\\MyRL\\TSN-RL\\Data\\resource\\info')

        if self.edges_info:
            json.dump(self.edges_info, open('D:\\MyRL\\TSN-RL\\Data\\resource\\info\\edges_info.json', "w"), indent=4)
        else:
            print('Havent generated node_mat')

if __name__ == '__main__':
    # content = []
    fo_network_info = open("resource/info/network_info.txt", "r")
    fo_node_info = open("resource/info/node_info.txt", "r")
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