import time
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import Polynomial
from tools import *  


# 从文件读取输入数据
def read_input_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        # 提取给定的宽度和矩形的数量
        given_width = int(lines[0].split(':')[1].strip())
        number_of_rectangles = int(lines[1].split(':')[1].strip())
        items = []
        # 从文件的每一行提取矩形的宽度和高度
        for line in lines[3:]:
            width, height = map(int, line.strip().split())
            items.append([width, height])
        # 返回给定宽度、矩形数量和矩形的数组
        return given_width, number_of_rectangles, np.array(items)


# 执行打包模拟的函数
def try_pack(bin_length, itemNum, AllItem):
    max_length = 0  # 用来记录放入所有矩形后的最大长度
    Bin = [WIDTH, bin_length]  # 设置一个二维的箱子，宽度是 WIDTH，长度是 bin_length
    RPNXY = []  # 用于存储已放置矩形的位置
    flagItem = np.zeros(itemNum)  # 用一个数组记录哪些矩形已经被放置

    # 遍历每个矩形，尝试将其放入箱子
    for i in range(itemNum):
        if flagItem[i] == 0:  # 只考虑未放置的矩形
            item = AllItem[i, :]  # 当前矩形的尺寸
            itemRP = Bin  # 当前的箱子尺寸
            # 检查矩形是否与已经放置的矩形重叠
            flagOL = overlap(item, AllItem, itemRP, RPNXY)  # 假设 overlap 函数在其他地方定义
            if flagOL == 0:  # 如果没有重叠，就可以放置该矩形
                # 计算矩形的最终位置
                itemRP = finalPos(item, AllItem, itemRP, RPNXY)  # 假设 finalPos 函数在其他地方定义
                if len(itemRP) > 0:
                    # 将矩形的索引和位置添加到 RPNXY 中
                    RPNXY.append([i, itemRP[0], itemRP[1]])
                    flagItem[i] = 1  # 标记该矩形已被放置
                    # 更新最大长度
                    if itemRP[1] > max_length:
                        max_length = itemRP[1]
    # 返回是否所有矩形都被放置、最大长度和矩形的最终位置
    return all(flagItem), max_length, RPNXY


# 包含测试用例的目录
test_cases_dir = 'Test_cases'
# 获取目录中所有以 .txt 结尾的文件
file_list = [f for f in os.listdir(test_cases_dir) if f.endswith('.txt')]

# 用来存储结果的数据结构
distributions = ['dist_1', 'dist_2', 'dist_3']  # 假设有三个分布
input_sizes = []  # 用来存储输入大小的列表
average_times = []  # 用来存储每个分布的平均运行时间
# 初始化一个字典，存储每个分布对应的每个大小的运行时间
size_to_times = {dist: {} for dist in distributions}

# 处理每个测试用例
for filename in file_list:
    # 从文件读取输入数据
    WIDTH, itemNum, AllItem = read_input_from_file(os.path.join(test_cases_dir, filename))

    # 从文件名中提取输入的尺寸和分布
    size = int(filename.split('size_')[1].split('_')[0])  # 提取尺寸（例如：从 'size_10' 中提取 10）
    distribution = 'dist_' + filename.split('dist_')[1].split('.txt')[0]  # 提取分布（例如：从 'dist_1' 中提取 'dist_1'）

    # 检查分布是否有效（即在字典中是否存在）
    if distribution not in size_to_times:
        print(f"警告: 未找到分布 {distribution} 在 size_to_times 中。")
        continue  # 如果分布无效，跳过当前迭代

    # 如果尺寸不在字典中，为该尺寸初始化一个空列表
    if size not in size_to_times[distribution]:
        size_to_times[distribution][size] = []

    # 运行打包模拟，并记录运行时间
    start_time = time.time()  # 记录开始时间
    _, max_length, _ = try_pack(max(AllItem[:, 1]) * itemNum, itemNum, AllItem)  # 调用 try_pack 函数进行打包
    end_time = time.time()  # 记录结束时间

    # 计算运行时间
    execution_time = end_time - start_time
    print(f"正在处理文件: {filename}\t 尺寸: {size}\t 分布: {distribution}\t 执行时间: {execution_time} 秒")

    # 将运行时间追加到对应分布和尺寸的字典中
    size_to_times[distribution][size].append(execution_time)

# 将结果写入 CSV 文件并为每个分布绘制图表
for dist in distributions:
    dist_input_sizes = []  # 存储该分布下的所有输入尺寸
    dist_average_times = []  # 存储该分布下的平均运行时间

    # 处理当前分布下的每个尺寸
    for size, times in size_to_times[dist].items():
        average_time = np.mean(times)  # 计算每个尺寸的平均运行时间
        dist_input_sizes.append(size)  # 将尺寸添加到输入尺寸列表中
        dist_average_times.append(average_time)  # 将平均时间添加到时间列表中

        # 将结果写入 CSV 文件
        result_df = pd.DataFrame({
            '输入尺寸': dist_input_sizes,
            '平均运行时间（秒）': dist_average_times
        })
        result_df.to_csv(f'{dist}_running_times.csv', index=False)

    # 绘制该分布的运行时间图表
    plt.figure(figsize=(10, 6))
    plt.scatter(dist_input_sizes, dist_average_times, label=f'{dist} - 平均运行时间', color='blue')

    # 为数据拟合一个二次多项式
    p = Polynomial.fit(dist_input_sizes, dist_average_times, 2)  # 使用二次多项式拟合
    x_fit = np.linspace(min(dist_input_sizes), max(dist_input_sizes), 100)  # 创建一个平滑的 x 值范围
    y_fit = p(x_fit)  # 计算拟合曲线的 y 值

    plt.plot(x_fit, y_fit, label=f'拟合多项式（度数 2）', color='green')

    # 添加标签、标题和网格
    plt.xlabel('输入尺寸（矩形数量）')
    plt.ylabel('平均运行时间（秒）')
    plt.title(f'运行时间 vs 输入尺寸 - {dist} 分布')
    plt.legend()
    plt.grid(True)
    
    # 保存图像并显示
    plt.savefig(f'Distribution_{dist}.png')
    plt.show()

    # 可选：打印当前分布拟合的多项式系数
    print(f"{dist} 拟合的多项式系数: {p.coef}")
