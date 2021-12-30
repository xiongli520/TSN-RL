import json
import matplotlib.pyplot as plt

def get_data(file_name):
    schedule_result = json.load(open(file_name))
    flow_length = []
    flow_offset = []
    edge_notation = []  # 标记不同的链路
    flow_id = []        # 标记不同的流，为不同的颜色

    for edge_id, edge_info in schedule_result.items():
        for tt_flows in edge_info:
            flow_length.append(tt_flows['end_slot'] - tt_flows['start_slot'] + 1)
            flow_offset.append(tt_flows['start_slot'])
            edge_notation.append(int(edge_id))
            flow_id.append(tt_flows['tt_flow'])

    return flow_offset, flow_length, edge_notation, flow_id

def main():
    fig, ax = plt.subplots()
    color_buffer = ['#ff3b27','#ff3b27', '#faff3b', '#5cff3e', '#62ffc1',
                    '#6addff', '#145dff', '#b662ff', '#0b4900','#a80042' ]
    flow_offset, flow_length, edge_notation, flow_id = get_data('../result/DQN/schedule_result_380.json')
    for i in range(len(flow_offset)):
        ax.broken_barh([(flow_offset[i], flow_length[i])], (edge_notation[i], 1), facecolors=color_buffer[flow_id[i]%10])

    plt.show()


if __name__ == '__main__':
    main()
