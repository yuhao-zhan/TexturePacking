import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from tools import *


def read_input_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

        # 提取给定宽度和矩形数量
        given_width = int(lines[0].split(':')[1].strip())
        number_of_rectangles = int(lines[1].split(':')[1].strip())

        # 提取矩形的宽度和高度
        items = []
        for line in lines[3:]:  # 从第4行开始，跳过前面的头部信息
            width, height = map(int, line.strip().split())
            items.append([width, height])

        return given_width, number_of_rectangles, np.array(items)


# 计算覆盖率
def compute_coverage_ratio(packed_items, bin_width, bin_length, df_AllItem):
    packed_items = pd.DataFrame(packed_items, columns=['itemNum', 'X', 'Y'])
    packed_items = packed_items.merge(df_AllItem, left_on='itemNum', right_index=True)

    # 计算物品的总面积
    packed_items['area'] = packed_items['width'] * packed_items['length']
    total_area = packed_items['area'].sum()

    # 计算箱子的总面积
    bin_area = bin_width * bin_length

    # 计算覆盖率
    coverage_ratio = total_area / bin_area
    return coverage_ratio


# 使用类来避免全局变量
class PackingSimulator:
    def __init__(self, WIDTH, itemNum, AllItem):
        self.WIDTH = WIDTH  # 箱子的宽度
        self.itemNum = itemNum  # 物品数量
        self.AllItem = AllItem  # 所有物品的尺寸
        self.df_AllItem = pd.DataFrame(AllItem, columns=['width', 'length'])  # 将物品数据转为DataFrame
        self.LENGTH = max(AllItem[:, 1]) * itemNum  # 箱子的长度为物品中最大长度乘以物品数
        self.Bin = [WIDTH, self.LENGTH]  # 初始化箱子的宽度和长度
        self.max_length = 0  # 记录当前箱子最大的装载长度
        self.RPNXY = []  # 用来存放已装入的物品位置
        self.flagItem = np.zeros(itemNum)  # 标记物品是否已被装入箱子

    def try_pack(self, bin_length):
        self.max_length = 0  # 重置最大箱子长度
        self.Bin = [self.WIDTH, bin_length]  # 设置新的箱子尺寸
        self.RPNXY = []  # 清空已装入的物品记录
        self.flagItem = np.zeros(self.itemNum)  # 重新初始化物品的装载状态

        for i in range(self.itemNum):
            if self.flagItem[i] == 0:  # 如果物品没有被装入
                item = self.AllItem[i, :]  # 获取当前物品的宽度和长度
                itemRP = self.Bin  # 初始位置在箱子右上角
                flagOL = overlap(item, self.AllItem, itemRP, self.RPNXY)  # 检查是否有重叠
                if flagOL == 0:  # 如果没有重叠
                    itemRP = finalPos(item, self.AllItem, itemRP, self.RPNXY)  # 获取物品的最终位置
                    if len(itemRP) > 0:
                        self.RPNXY.append([i, itemRP[0], itemRP[1]])  # 记录物品的坐标
                        self.flagItem[i] = 1  # 标记物品已经装入
                        if itemRP[1] > self.max_length:  # 更新箱子的最大长度
                            self.max_length = itemRP[1]
        return all(self.flagItem)  # 如果所有物品都装入返回True，否则返回False


# 处理所有Test_cases目录下的文件
def process_files():
    coverage_data = np.zeros((9, 3))  # 9个输入大小，3个分布类型
    input_sizes = [10, 50, 100, 500, 1000, 3000, 5000, 8000, 10000]  # 输入大小
    distributions = [1, 2, 3]  # 不同的物品分布类型

    for dist in distributions:
        for size_index, input_size in enumerate(input_sizes):
            filename = f"Test_cases/test_size_{input_size}_dist_{dist}.txt"
            print(f"正在处理文件: {filename}")
            if os.path.exists(filename):  # 如果文件存在
                # 从文件中读取输入数据
                WIDTH, itemNum, AllItem = read_input_from_file(filename)

                # 创建PackingSimulator实例
                simulator = PackingSimulator(WIDTH, itemNum, AllItem)

                # 开始装箱模拟
                max_coverage_ratio = 0
                min_coverage_ratio = 1
                for _ in range(3):
                    ran = list(range(itemNum))
                    random.shuffle(ran)  # 随机生成装箱顺序
                    if simulator.try_pack(simulator.LENGTH):
                        coverage_ratio = compute_coverage_ratio(simulator.RPNXY, simulator.WIDTH, simulator.max_length,
                                                                simulator.df_AllItem)

                        if coverage_ratio > max_coverage_ratio:
                            max_coverage_ratio = coverage_ratio
                        if coverage_ratio < min_coverage_ratio:
                            min_coverage_ratio = coverage_ratio

                # 存储当前输入大小和分布类型的覆盖率
                coverage_data[size_index, dist - 1] = max_coverage_ratio
                print(f"最大覆盖率: {max_coverage_ratio}")

    # 将覆盖率数据保存到csv文件
    df_coverage = pd.DataFrame(coverage_data,
                                columns=[f"Dist_{dist}" for dist in distributions],
                                index=input_sizes)

    df_coverage.to_csv("coverage_data.csv", index_label="输入大小")
    return df_coverage


# 绘制覆盖率数据
def plot_coverage_data(df_coverage):
    # 绘制覆盖率与输入大小的关系图（固定分布）
    for dist in range(1, 4):
        plt.figure(figsize=(8, 6))  # 设置更大的图形尺寸

        # 获取输入大小的位置
        x_pos = np.arange(len(df_coverage.index))

        # 绘制条形图
        bars = plt.bar(x_pos, df_coverage[f"Dist_{dist}"], width=0.6, color='#4A90E2', edgecolor='black',
                       linewidth=1.2)  # 使用专业风格

        # 设置x轴的标签为输入大小
        plt.xticks(x_pos, df_coverage.index, rotation=45, fontname='Times New Roman', fontweight='bold',
                   fontsize=12)

        # 设置y轴的标签
        plt.yticks(fontname='Times New Roman', fontweight='bold',
                   fontsize=12)

        # 添加标题和坐标轴标签
        plt.title(f"覆盖率与输入大小的关系 (Dist {dist})", fontname='Times New Roman', fontweight='bold',
                  fontsize=16)
        plt.xlabel("输入大小", fontname='Times New Roman', fontweight='bold', fontsize=14)
        plt.ylabel("覆盖率", fontname='Times New Roman', fontweight='bold', fontsize=14)

        # 在条形图上方显示覆盖率的数值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.4f}',
                     ha='center', va='bottom', fontname='Times New Roman', fontweight='bold', fontsize=10)

        # 添加y轴的网格线
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 调整布局
        plt.tight_layout()

        # 保存图像
        plt.savefig(f"Performance_fixing_distribution/coverage_ratio_dist_{dist}.png")
        plt.close()

    # 绘制覆盖率与分布类型的关系图（固定输入大小）
    for input_size in df_coverage.index:
        plt.figure(figsize=(8, 6))  # 设置更大的图形尺寸

        # 获取分布类型的位置
        x_pos = np.arange(len(df_coverage.columns))

        # 绘制条形图
        bars = plt.bar(x_pos, df_coverage.loc[input_size, :], width=0.6, color='#4A90E2', edgecolor='black',
                       linewidth=1.2)

        # 设置x轴的标签为分布类型
        plt.xticks(x_pos, df_coverage.columns, rotation=45, fontname='Times New Roman', fontweight='bold',
                   fontsize=12)

        # 设置y轴的标签
        plt.yticks(fontname='Times New Roman', fontweight='bold',
                   fontsize=12)

        # 添加标题和坐标轴标签
        plt.title(f"覆盖率与分布类型的关系 (输入大小 {input_size})", fontname='Times New Roman',
                  fontweight='bold', fontsize=16)
        plt.xlabel("分布类型", fontname='Times New Roman', fontweight='bold', fontsize=14)
        plt.ylabel("覆盖率", fontname='Times New Roman', fontweight='bold', fontsize=14)

        # 在条形图上方显示覆盖率的数值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.4f}',
                     ha='center', va='bottom', fontname='Times New Roman', fontweight='bold', fontsize=10)

        # 添加y轴的网格线
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 调整布局
        plt.tight_layout()

        # 保存图像
        plt.savefig(f"Performance_fixing_input_size/coverage_ratio_input_size_{input_size}.png",
                    dpi=300)
        plt.close()


# 主执行函数
df_coverage = process_files()
plot_coverage_data(df_coverage)
print("处理完成！覆盖率数据已保存至'coverage_data.csv'，并且图表已保存为图片。")
