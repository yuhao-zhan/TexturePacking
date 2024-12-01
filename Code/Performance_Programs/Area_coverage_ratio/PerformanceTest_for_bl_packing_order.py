import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from tools import *


# 从文件中读取输入数据
def read_input_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

        # 提取给定宽度和矩形数量
        given_width = int(lines[0].split(':')[1].strip())
        number_of_rectangles = int(lines[1].split(':')[1].strip())

        # 提取矩形的宽度和高度
        items = []
        for line in lines[3:]:  # 从第四行开始跳过表头
            width, height = map(int, line.strip().split())
            items.append([width, height])

        return given_width, number_of_rectangles, np.array(items)


# 从文件读取输入
filename = 'test_size_10_dist_1.txt'
WIDTH, itemNum, AllItem = read_input_from_file(filename)

# 将物品数据转换为DataFrame格式
df_AllItem = pd.DataFrame(AllItem, columns=['width', 'length'])
print(df_AllItem)

# 箱子的长度为所有物品中最大长度与物品数量的乘积
LENGTH = max(AllItem[:, 1]) * itemNum  
Bin = [WIDTH, LENGTH]  # 箱子的宽度与长度
print(f"Initial bin length is: {LENGTH}")  # 打印初始箱子长度

ansBXY = np.zeros((itemNum, 3))  # [箱子编号，X坐标，Y坐标]
RPNXY = []  # 存储已装入物品的坐标
BinNum = 1
flagItem = np.zeros(itemNum)  # 标记物品是否已装入箱子，0表示未装入，1表示已装入
max_length = 0  # 记录箱子的最大长度

# 为每个物品生成一个随机颜色
item_colors = {i: np.random.rand(3, ) for i in range(itemNum)}  # 为每个物品分配一个随机颜色


# 开始装箱过程
def try_pack(bin_length):
    global RPNXY, flagItem, ansBXY, Bin, max_length
    max_length = 0  # 箱子最大长度初始化
    Bin = [WIDTH, bin_length]  # 更新箱子的宽度与长度
    RPNXY = []  # 清空已装入物品的记录
    flagItem = np.zeros(itemNum)  # 重置物品装入标记

    for i in range(itemNum):
        if flagItem[ran[i]] == 0:  # 如果该物品未被装入箱子
            item = AllItem[ran[i], :]
            itemRP = Bin  # 初始位置在箱子的右上角
            flagOL = overlap(item, AllItem, itemRP, RPNXY)  # 检查物品是否重叠
            if flagOL == 0:
                itemRP = finalPos(item, AllItem, itemRP, RPNXY)  # 找到物品的最终位置
                if len(itemRP) > 0:
                    RPNXY.append([ran[i], itemRP[0], itemRP[1]])  # 保存物品的坐标
                    flagItem[ran[i]] = 1  # 标记该物品已装入箱子
                    if itemRP[1] > max_length:  # 更新箱子的最大长度
                        max_length = itemRP[1]
    return all(flagItem)  # 如果所有物品都被装入，返回True，否则返回False


# 计算装箱覆盖率（即物品所占面积与箱子面积的比率）
def compute_coverage_ratio(packed_items, bin_width, bin_length):
    # 将物品的位置与尺寸合并
    packed_items = pd.DataFrame(packed_items, columns=['itemNum', 'X', 'Y'])
    packed_items = packed_items.merge(df_AllItem, left_on='itemNum', right_index=True)

    # 计算所有已装入物品的总面积
    packed_items['area'] = packed_items['width'] * packed_items['length']
    total_area = packed_items['area'].sum()

    # 计算箱子的总面积
    bin_area = bin_width * bin_length

    # 计算覆盖率
    coverage_ratio = total_area / bin_area
    return coverage_ratio


# 可视化已装入物品的图形展示
def visualize_packing(packed_items, bin_width, bin_length, all_items, coverage_ratio_result):
    """
    可视化已装入物品在容器中的位置，并显示正确的Y轴方向。

    参数:
    - packed_items: 物品的列表，每个物品包含[itemNum, X, Y]。
    - bin_width: 容器的宽度。
    - bin_length: 容器的长度。
    - all_items: 所有物品的DataFrame，包含物品的尺寸信息。
    """
    # 创建绘图
    fig, ax = plt.subplots(figsize=(10, 10))

    # 绘制容器的外框
    ax.set_xlim(0, bin_width)
    ax.set_ylim(0, bin_length)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(f'coverage ratio: {coverage_ratio_result:.4f}')
    ax.set_xlabel('X 坐标')
    ax.set_ylabel('Y 坐标')

    # 添加网格以便更好地观察
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # 绘制每个已装入的物品
    for packed_item in packed_items:
        itemNum, X, Y = packed_item
        width, length = all_items.loc[itemNum, ['width', 'length']]

        # 矩形的左下角坐标
        bottom_left_x = X - width
        bottom_left_y = Y - length

        # 创建矩形
        rect = patches.Rectangle(
            (bottom_left_x, bottom_left_y),  # 左下角坐标
            width,
            length,
            linewidth=1,
            edgecolor='black',
            facecolor=np.random.rand(3, ),  # 每个物品的随机颜色
            alpha=0.7
        )
        ax.add_patch(rect)

        # 在矩形上添加物品编号和坐标文本
        ax.text(X - width / 2, Y - length / 2, f'{itemNum}', color='white', ha='center', va='center', fontsize=10)
        ax.text(X, Y, f'({X}, {Y})', color='blue', fontsize=8, ha='left', va='bottom')

    # 设置显示范围并展示图像
    ax.set_xlim(0, bin_width)
    ax.set_ylim(0, bin_length)
    plt.show()


# 初始覆盖率
max_coverage_ratio = 0
min_coverage_ratio = 1

# 尝试装箱多次并寻找最佳和最差的装箱方案
for i in range(1, 10001):
    ran = list(range(itemNum))  # 生成物品的随机序列
    random.shuffle(ran)  # 随机打乱装箱顺序
    if try_pack(LENGTH):
        coverage_ratio = compute_coverage_ratio(RPNXY, WIDTH, max_length)
        print(f"{i}th time coverage_ratio: {coverage_ratio}")
        if coverage_ratio > max_coverage_ratio:
            max_coverage_ratio = coverage_ratio
            length_for_max_coverage_ratio = max_length
            RPNXY_for_max_coverage_ratio = RPNXY
            max_ran = ran
        if coverage_ratio < min_coverage_ratio:
            min_coverage_ratio = coverage_ratio
            length_for_min_coverage_ratio = max_length
            RPNXY_for_min_coverage_ratio = RPNXY
            min_ran = ran

# 输出最大和最小覆盖率的信息
print(f"All items packed!\t Max Coverage Ratio: {max_coverage_ratio:.4f}\t  Min Coverage Ratio: {min_coverage_ratio:.4f}")  # 覆盖率
# 输出最大和最小覆盖率时的物品顺序
print(f"Max Coverage Ratio Ran: {max_ran}\t Min Coverage Ratio Ran: {min_ran}")
# 可视化最大和最小覆盖率的装箱情况
visualize_packing(RPNXY_for_max_coverage_ratio, WIDTH, length_for_max_coverage_ratio, df_AllItem, max_coverage_ratio)
visualize_packing(RPNXY_for_min_coverage_ratio, WIDTH, length_for_min_coverage_ratio, df_AllItem, min_coverage_ratio)
