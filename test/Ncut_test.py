# encoding=utf-8
import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg as LA
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.preprocessing import normalize


def similarity_function(points):
    res = rbf_kernel(points)
    for i in range(len(res)):
        res[i, i] = 0
    return res


def normalized_cut(points, k):
    A = similarity_function(points)
    W = np.eye(len(A)) - normalize(A, norm='l1')
    eigvalues, eigvectors = LA.eig(W)
    indices = np.argsort(eigvalues)[1:k]
    return KMeans(n_clusters=k).fit_predict(eigvectors[:, indices])


def calculate_w_ij(a, b, sigma=1):
    w_ab = np.exp(-np.sum((a - b) ** 2) / (2 * sigma ** 2))
    return w_ab


# 计算邻接矩阵
def Construct_Matrix_W(data, k=5):
    rows = len(data)  # 取出数据行数
    W = np.zeros((rows, rows))  # 对矩阵进行初始化：初始化W为rows*rows的方阵
    for i in range(rows):  # 遍历行
        for j in range(rows):  # 遍历列
            if (i != j):  # 计算不重复点的距离
                W[i][j] = calculate_w_ij(data[i], data[j])  # 调用函数计算距离
        # t = np.argsort(W[i, :])  # 对W中进行行排序，并提取对应索引
        # for x in range(rows - k):  # 对W进行处理
        #     W[i][t[x]] = 0
    W = (W + W.T) / 2  # 主要是想处理可能存在的复数的虚部，都变为实数
    return W


def Calculate_Matrix_L_sym(W):  # 计算标准化的拉普拉斯矩阵
    degreeMatrix = np.sum(W, axis=1)  # 按照行对W矩阵进行求和
    L = np.diag(degreeMatrix) - W  # 计算对应的对角矩阵减去w
    # 拉普拉斯矩阵标准化，就是选择Ncut切图
    sqrtDegreeMatrix = np.diag(1.0 / (degreeMatrix ** (0.5)))  # D^(-1/2)
    L_sym = np.dot(np.dot(sqrtDegreeMatrix, L), sqrtDegreeMatrix)  # D^(-1/2) L D^(-1/2)
    return L_sym


def normalization(matrix):  # 归一化
    sum = np.sqrt(np.sum(matrix ** 2, axis=1, keepdims=True))  # 求数组的正平方根
    nor_matrix = matrix / sum  # 求平均
    return nor_matrix

if __name__ == '__main__':

    X, y = make_blobs()
    W = Construct_Matrix_W(X)  # 计算邻接矩阵
    L_sym = Calculate_Matrix_L_sym(W)  # 依据W计算标准化拉普拉斯矩阵
    lam, H = np.linalg.eig(L_sym)  # 特征值分解

    t = np.argsort(lam)  # 将lam中的元素进行排序，返回排序后的下标
    H = np.c_[H[:, t[0]], H[:, t[1]]]  # 0和1类的两个矩阵按行连接，就是把两矩阵左右相加，要求行数相等。
    H = normalization(H)  # 归一化处理

    model = KMeans(n_clusters=3)  # 新建20簇的Kmeans模型
    model.fit(H)  # 训练
    labels = model.labels_  # 得到聚类后的每组数据对应的标签类型

    # 画图
    plt.style.use('ggplot')
    # 原数据
    fig, (ax0, ax1) = plt.subplots(ncols=2)
    ax0.scatter(X[:, 0], X[:, 1], c=y)
    ax0.set_title('raw data')
    # 谱聚类结果
    ax1.scatter(X[:, 0], X[:, 1], c=labels)
    ax1.set_title('Normalized Cut')
    plt.show()



    # X, y = make_blobs()
    # labels = normalized_cut(X, 3)
    # # 画图
    # plt.style.use('ggplot')
    # # 原数据
    # fig, (ax0, ax1) = plt.subplots(ncols=2)
    # ax0.scatter(X[:, 0], X[:, 1], c=y)
    # ax0.set_title('raw data')
    # # 谱聚类结果
    # ax1.scatter(X[:, 0], X[:, 1], c=labels)
    # ax1.set_title('Normalized Cut')
    # plt.show()