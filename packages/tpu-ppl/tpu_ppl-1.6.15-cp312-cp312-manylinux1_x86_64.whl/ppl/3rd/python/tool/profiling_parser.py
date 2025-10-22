import os
import sys
import ast
import re
# from tabulate import tabulate


def parse_line(line):
    list_str = line[line.find('['):len(line) - 1]
    strs = ast.literal_eval(list_str)
    return strs


def print_data(data, header):
    # print(tabulate(data, headers=header))
    head_len = []
    for x in range(len(header)):
        item_len = len(header[x])
        for item in data:
            item_len = max(len(str(item[x])), item_len)
        head_len.append(item_len)
    format_str = ["{:<" + str(x) + "}" for x in head_len]
    format_str = " ".join(format_str)
    print(format_str.format(*header))
    for item in data:
        print(format_str.format(*item))


def parse_profiling(path, chip):
    data_dir = os.path.join(path,
                            "result_profiling/output/PerfWeb/profile_data.js")
    files = []
    if os.path.exists(data_dir):
        files.append(data_dir)
    else:
        path = os.path.join(path, "result_profiling")
        for i in os.listdir(path):
            file_path = os.path.join(os.path.join(path, i), "output/PerfWeb/profile_data.js")
            files.append((file_path, os.stat(file_path).st_mtime))
        files.sort(key=lambda x: x[1])
        files = [f for f, t in files]
    for data_dir in files:
        with open(data_dir) as file:
            header_item = []
            data_item = []
            for line in file:
                if line.find("summary_header") > 0:
                    header_item = parse_line(line)
                if line.find("summary_data") > 0:
                    data_item = parse_line(line)
            if len(header_item) == 0 or len(data_item) == 0:
                raise Exception("parse error")
            if len(header_item) < 9:
                raise Exception("parse error")
            print_list = [0, 1, 2, 3, 4, 6, 7, 8]
            sub_header_item = [header_item[i] for i in print_list]
            sub_data_item = []
            for item in data_item:
                sub_data_item.append([item[i] for i in print_list])
            print("=================================")
            if len(files) > 1:
                args = data_dir.split('/')[-4].split("-")
                print(f"{args[0]} with args: ({', '.join(args[1:])})", end=" ")
            print("profiling result:\n")
            print("=================================")
            print("==================================================================================")
            print_data(sub_data_item, sub_header_item)
            print("==================================================================================")


def parse_bm1684x_dma_data(line):
    data = line[line.find('[') + 1:line.find(']')]
    data = data.split(',')
    start_time = round(float(data[1]), 2)
    end_time = round(float(data[2]), 2)
    total_time = end_time - start_time
    speed_str = data[10]
    speed = float(speed_str[speed_str.find('=') + 1:speed_str.find('G')])
    data_size = speed * total_time * 1000
    return [start_time, end_time, total_time, speed, data_size]


def parse_bm1684x_bd_data(line):
    data = line[line.find('[') + 1:line.find(']')]
    data = data.split(',')
    start_time = round(float(data[1]), 2)
    end_time = round(float(data[2]), 2)
    total_time = end_time - start_time
    return [start_time, end_time, total_time]


def parse_bm1684x_pcie(path):
    dma_data = []
    bd_data = []
    data_dir = os.path.join(path,
                            "pro_out/profile_data.js")
    with open(data_dir) as file:
        for line in file:
            if line.find("gdma_id=") > 0 and line.find("speed") > 0:
                dma_data.append(parse_bm1684x_dma_data(line))
            if line.find("bd_id=") > 0 and line.find("cycle") > 0:
                bd_data.append(parse_bm1684x_bd_data(line))

    total_time = dma_data[-1][1] - dma_data[0][0]
    total_dma_time = sum([x[2] for x in dma_data])
    total_tiu_time = sum([x[2] for x in bd_data])
    total_data = sum([x[4] for x in dma_data])
    avg_bandwidth = total_data / total_dma_time / 1000
    para = (total_dma_time + total_tiu_time) / total_time
    header = [
        "Parallelism(%)", "totalTime(us)", "TiuWorkingRatio",
        "totalTiuTime(us)", "totalGdmaTime(us)", "GdmaDdrAvgBandwidth(GB/s)"
    ]
    item0 = '%.2f%%' % (para * 100)
    item1 = '%.2fus' % total_time
    item2 = '%.2f%%' % (total_tiu_time / total_time * 100)
    item3 = '%.2fus' % total_tiu_time
    item4 = '%.2fus' % total_dma_time
    item5 = '%.2fGB/s' % avg_bandwidth

    data = [[item0, item1, item2, item3, item4, item5]]
    print("=================================")
    print("profiling result:")
    print("==================================================================================")
    print_data(data, header)
    print("==================================================================================")


if __name__ == "__main__":
    path = sys.argv[1]
    parse_bm1684x_pcie(path)
