def dijkstra(graph, src):
    length = len(graph)

    for i in range(length):
        for j in range(length):
            if graph[i][j] == 0:
                graph[i][j] = 999
    nodes = [i for i in range(length)]

    visited = [src]
    path = {src:{src:[]}}
    nodes.remove(src)
    distance_graph = {src:0}
    pre = next = src

    while nodes:
        distance = float('inf')
        for v in visited:
             for d in nodes:
                new_dist = graph[src][v] + graph[v][d]
                if new_dist < distance:
                    distance = new_dist
                    next = d
                    pre = v
                    graph[src][d] = new_dist


        path[src][next] = [i for i in path[src][pre]]
        path[src][next].append(next)

        distance_graph[next] = distance

        visited.append(next)
        nodes.remove(next)

    return distance_graph, path


if __name__ == '__main__':
    graph_list = [[0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 1, 1, 1, 1, 1, 0]]



    distance, path = dijkstra(graph_list, 2)
    print(distance, '\n', path)
