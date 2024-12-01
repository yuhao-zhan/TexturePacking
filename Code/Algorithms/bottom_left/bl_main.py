import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from tools import *  # 导入工具模块，假设其中有overlap和finalPos函数

# 读取输入数据函数
def read_input_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

        # 提取箱子宽度和矩形数量
        given_width = int(lines[0].split(':')[1].strip())  # 第一行是箱子的宽度
        number_of_rectangles = int(lines[1].split(':')[1].strip())  # 第二行是矩形的数量

        # 提取矩形的宽度和高度
        items = []
        for line in lines[3:]:  # 从第四行开始读取矩形数据
            width, height = map(int, line.strip().split())  # 每行包含宽度和高度
            items.append([width, height])

        return given_width, number_of_rectangles, np.array(items)

# 从文件读取输入数据
filename = 'test_width_100_max-height_50_size_10_dist_1.txt'
WIDTH, itemNum, AllItem = read_input_from_file(filename)

# 将物品信息转换为DataFrame格式
df_AllItem = pd.DataFrame(AllItem, columns=['width', 'length'])
print(df_AllItem)

# 箱子的初始长度设置为物品中最大长度乘以物品数
LENGTH = max(AllItem[:, 1]) * itemNum
Bin = [WIDTH, LENGTH]  # 定义箱子的宽度和长度
print(f"Initial bin length is: {LENGTH}")  # 打印初始箱子长度

# 随机打乱物品顺序
ran = list(range(itemNum))
random.shuffle(ran)

# 初始化装箱位置数组
ansBXY = np.zeros((itemNum, 3))  # 存储装箱后的物品位置
RPNXY = []  # 存储已装入箱子的位置
BinNum = 1  # 初始箱子编号为1
flagItem = np.zeros(itemNum)  # 标记物品是否已装入，0为未装入，1为已装入
max_length = 0  # 记录箱子的最大长度

# 装箱尝试函数
def try_pack(bin_length):
    global RPNXY, flagItem, ansBXY, Bin, max_length
    max_length = 0  # 初始化最大箱子长度
    Bin = [WIDTH, bin_length]  # 设置当前箱子的宽度和长度
    RPNXY = []  # 清空已装入的物品记录
    flagItem = np.zeros(itemNum)  # 重新标记物品状态

    # 尝试将每个物品装入箱子
    for i in range(itemNum):
        if flagItem[ran[i]] == 0:  # 如果物品未装入箱子
            item = AllItem[ran[i], :]  # 获取物品的宽高
            itemRP = Bin  # 初始位置设定在箱子的右上角
            flagOL = overlap(item, AllItem, itemRP, RPNXY)  # 检查是否与已装入物品重叠
            if flagOL == 0:  # 如果没有重叠
                itemRP = finalPos(item, AllItem, itemRP, RPNXY)  # 计算物品的最终位置
                if len(itemRP) > 0:  # 如果有有效位置
                    RPNXY.append([ran[i], itemRP[0], itemRP[1]])  # 保存物品位置
                    flagItem[ran[i]] = 1  # 标记该物品已装入
                    if itemRP[1] > max_length:  # 更新箱子的最大长度
                        max_length = itemRP[1]
    return all(flagItem)  # 如果所有物品都装入箱子返回True，否则返回False

# 尝试装箱
if try_pack(LENGTH):
    LENGTH = max_length  # 更新箱子的最终长度

print(f"Final bin length is: {LENGTH}")  # 打印最终箱子长度
df_RPNXY = pd.DataFrame(RPNXY, columns=['itemNum', 'X', 'Y'])  # 创建DataFrame存储装箱序列
print(df_RPNXY)  # 打印装箱序列，[物品编号，X坐标，Y坐标]

# 计算覆盖率的函数
def compute_coverage_ratio(packed_items, bin_width, bin_length):
    # 合并物品尺寸和位置数据
    packed_items = pd.DataFrame(packed_items, columns=['itemNum', 'X', 'Y'])
    packed_items = packed_items.merge(df_AllItem, left_on='itemNum', right_index=True)

    # 计算总物品面积
    packed_items['area'] = packed_items['width'] * packed_items['length']
    total_area = packed_items['area'].sum()

    # 计算箱子面积
    bin_area = bin_width * bin_length

    # 计算覆盖率
    coverage_ratio = total_area / bin_area
    return coverage_ratio

# 装箱结果的可视化
def visualize_packing(packed_items, bin_width, bin_length, all_items, coverage_ratio_result):
    """
    可视化已装箱的物品及其在容器中的位置。

    参数:
    - packed_items: 已装入箱子的物品列表，包含[itemNum, X, Y]。
    - bin_width: 容器的宽度。
    - bin_length: 容器的长度。
    - all_items: 包含所有物品尺寸的DataFrame。
    """
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 10))

    # 绘制箱子的边界
    ax.set_xlim(0, bin_width)
    ax.set_ylim(0, bin_length)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(f'coverage ratio: {coverage_ratio_result:.4f}')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')

    # 添加网格线，提高可视化效果
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # 绘制每个已装箱的物品
    for packed_item in packed_items:
        itemNum, X, Y = packed_item
        width, length = all_items.loc[itemNum, ['width', 'length']]

        # 计算矩形的左下角坐标
        bottom_left_x = X - width
        bottom_left_y = Y - length

        # 创建矩形，并随机为每个物品指定颜色
        rect = patches.Rectangle(
            (bottom_left_x, bottom_left_y),  # 左下角坐标
            width,
            length,
            linewidth=1,
            edgecolor='black',
            facecolor=np.random.rand(3, ),  # 随机颜色
            alpha=0.7
        )
        ax.add_patch(rect)

        # 添加文本注释，显示物品编号和坐标
        ax.text(X - width / 2, Y - length / 2, f'{itemNum}', color='white', ha='center', va='center', fontsize=10)
        ax.text(X, Y, f'({X}, {Y})', color='blue', fontsize=8, ha='left', va='bottom')

    # 设置坐标轴范围并显示图表
    ax.set_xlim(0, bin_width)
    ax.set_ylim(0, bin_length)
    plt.show()

# 计算覆盖率并进行可视化
coverage_ratio = compute_coverage_ratio(RPNXY, WIDTH, LENGTH)
print(f"Coverage Ratio: {coverage_ratio:.4f}")  # 打印覆盖率

# 使用装箱算法得到的物品位置、箱子宽度和长度、以及所有物品尺寸进行可视化
packed_items = RPNXY  # 使用装箱算法得到的物品位置
bin_width = WIDTH  # 箱子宽度
bin_length = LENGTH  # 箱子长度
all_items = df_AllItem  # 所有物品的尺寸信息

# 可视化装箱结果
visualize_packing(packed_items, bin_width, bin_length, all_items, coverage_ratio)
