from Data.DASP.DoC_Graph import *
import random

import numpy as np

from scipy import linalg as LA
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

class Stream_Partition:
    def __init__(self, doc_graph, group_num):
        self.doc_graph = doc_graph
        self.group_num = group_num
        self.tt_num = doc_graph.tt_num

        self.groups = [[] for _ in range(self.group_num)]
        self.groups = self.part_init()
        self.cgc = self.cal_cgc(self.groups)
        self.nCGC = self.cal_nCGC(self.groups)
        # self.label = self.normalized_cut(self.doc_graph.adj_mat, self.group_num)
        self.groups_final = [[] for _ in range(self.group_num)]
        self.part_final()
        self.cgc_final = self.cal_cgc(self.groups_final)
        self.nCGC_final = self.cal_nCGC(self.groups_final)

    def part_init(self):
        '''
        # 初始化随机打乱排序
        :return:
        '''
        arr = list(range(self.tt_num))
        random.shuffle(arr)
        cuts = random.choices(list(range(1, self.tt_num-1)), k=self.group_num-1)
        cuts.sort()
        cuts.insert(0, 0)
        cuts.append(self.tt_num-1)
        groups = []
        for i in range(self.group_num):
            groups.append(arr[cuts[i]:cuts[i+1]])
        return groups

    def cal_cgc(self, groups):
        '''
        计算cgc
        :return:
        '''
        cgc = 0
        for i in range(self.group_num):
            for j in range(i+1, self.group_num):
               cgc += self.cal_cgc_i(group1=groups[i], group2=groups[j])
        return cgc

    def cal_cgc_i(self, group1, group2):
        '''
        计算两个组的cgc
        :param group1:
        :param group2:
        :return:
        '''
        cgc_i = 0
        for i in group1:
            for j in group2:
                if j in self.doc_graph.doc_nodes[i].connection_index_list:
                    index = self.doc_graph.doc_nodes[i].connection_index_list.index(j)
                    cgc_i += self.doc_graph.doc_nodes[i].connection_weight_list[index]
        return cgc_i

    def cal_nCGC(self, groups):
        nCGC = 0
        for i in range(self.group_num):
            tmp = self.cal_assoc(groups[i])
            if tmp==0:
                return float('inf')
            nCGC += (self.cgc/tmp)

        return nCGC


    def cal_assoc(self, group_i):
        assoc_i = 0
        for i in group_i:
            for j in range(self.tt_num):
                if j in self.doc_graph.doc_nodes[i].connection_index_list:
                    index = self.doc_graph.doc_nodes[i].connection_index_list.index(j)
                    assoc_i += self.doc_graph.doc_nodes[i].connection_weight_list[index]
        return assoc_i

    # def normalized_cut(self, adj_mat, k):
    #     '''
    #     使用Ncut分组
    #     :param adj_mat:
    #     :param k:
    #     :return:
    #     '''
    #     # A = similarity_function(points)
    #     W = np.eye(len(adj_mat)) - normalize(adj_mat, norm='l1')
    #     eigvalues, eigvectors = LA.eig(W)
    #     indices = np.argsort(eigvalues)[1:k]
    #     return KMeans(n_clusters=k).fit_predict(eigvectors[:, indices])

    def Calculate_Matrix_L_sym(self, W):
        '''
        # 计算标准化的拉普拉斯矩阵
        :param W:
        :return:
        '''
        degreeMatrix = np.sum(W, axis=1)  # 按照行对W矩阵进行求和
        L = np.diag(degreeMatrix) - W  # 计算对应的对角矩阵减去w
        # 拉普拉斯矩阵标准化，就是选择Ncut切图
        sqrtDegreeMatrix = np.diag(1.0 / (degreeMatrix ** (0.5)))  # D^(-1/2)
        L_sym = np.dot(np.dot(sqrtDegreeMatrix, L), sqrtDegreeMatrix)  # D^(-1/2) L D^(-1/2)
        return L_sym

    def normalization(self, matrix):
        '''
        # 归一化
        :param matrix:
        :return:
        '''
        sum = np.sqrt(np.sum(matrix ** 2, axis=1, keepdims=True))  # 求数组的正平方根
        nor_matrix = matrix / sum  # 求平均
        return nor_matrix

    def part_final(self):
        '''
        根据标签进行分组
        :return:
        '''

        L_sym = self.Calculate_Matrix_L_sym(self.doc_graph.adj_mat)  # 依据W计算标准化拉普拉斯矩阵
        lam, H = np.linalg.eig(L_sym)  # 特征值分解

        t = np.argsort(lam)  # 将lam中的元素进行排序，返回排序后的下标
        H = np.c_[H[:, t[0]], H[:, t[1]]]  # 0和1类的两个矩阵按行连接，就是把两矩阵左右相加，要求行数相等。
        H = self.normalization(H)  # 归一化处理
        model = KMeans(n_clusters=self.group_num)  # 新建20簇的Kmeans模型
        model.fit(H)  # 训练
        labels = model.labels_  # 得到聚类后的每组数据对应的标签类型

        flow_id = 0
        for i in range(labels.size):
            self.groups_final[labels[i]].append(flow_id)
            flow_id+=1


if __name__ == '__main__':
    fo_network_info = open("../resource/info/network_info.txt", "r")
    fo_node_info = open("../resource/info/node_info.txt", "r")
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
    doc_graph = DoC_Graph(flow_generator.tt_flows)
    stream_partition = Stream_Partition(doc_graph, 4)

