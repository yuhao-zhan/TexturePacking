import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from tools import *


def read_input_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

        # Extract Given Width and Number of Rectangles
        given_width = int(lines[0].split(':')[1].strip())
        number_of_rectangles = int(lines[1].split(':')[1].strip())

        # Extract Width and Height of Rectangles
        items = []
        for line in lines[3:]:  # Start from line 4 to skip headers
            width, height = map(int, line.strip().split())
            items.append([width, height])

        return given_width, number_of_rectangles, np.array(items)


# Read inputs from the file
filename = 'test_width_100_max-height_50_size_10_dist_1.txt'
WIDTH, itemNum, AllItem = read_input_from_file(filename)

# Convert the items into a DataFrame
df_AllItem = pd.DataFrame(AllItem, columns=['width', 'length'])
print(df_AllItem)

LENGTH = max(AllItem[:, 1]) * itemNum  # 箱子长为物品中最大的长度乘以物品数目
Bin = [WIDTH, LENGTH]  # 箱子宽度与长度
print(f"Initial bin length is: {LENGTH}")  # 箱子长度

ran = list(range(itemNum))
random.shuffle(ran)  # 随机生成装箱序列

ansBXY = np.zeros((itemNum, 3))  # [箱子编号，X坐标，Y坐标]
RPNXY = []
BinNum = 1
flagItem = np.zeros(itemNum)  # 标记物品是否被装入箱子，0没有装入，1装入
max_length = 0  # 记录箱子最大长度


# 开始装箱

def try_pack(bin_length):
    global RPNXY, flagItem, ansBXY, Bin, max_length
    max_length = 0  # 箱子最大长度初始化
    Bin = [WIDTH, bin_length]  # 箱子宽度与长度
    RPNXY = []  # 清空已装入的物品记录
    flagItem = np.zeros(itemNum)  # 重新标记物品状态

    for i in range(itemNum):
        if flagItem[ran[i]] == 0:
            item = AllItem[ran[i], :]
            itemRP = Bin  # 起始位置在箱子右上角
            flagOL = overlap(item, AllItem, itemRP, RPNXY)  # 检查是否重叠
            if flagOL == 0:
                itemRP = finalPos(item, AllItem, itemRP, RPNXY)  # 找到物品的最终位置
                if len(itemRP) > 0:
                    RPNXY.append([ran[i], itemRP[0], itemRP[1]])  # 保存物品位置
                    flagItem[ran[i]] = 1  # 标记物品已装入
                    if itemRP[1] > max_length:  # 更新箱子最大长度
                        max_length = itemRP[1]
    return all(flagItem)  # 所有物品都装入箱子返回True，否则False


# if try_pack(LENGTH):  # 尝试装箱
#     final_RPNXY = RPNXY.copy()  # 记录最终装箱序列
#     final_length = max_length
#     print(f"Try bin length: {LENGTH}")  # 尝试的箱子长度

if try_pack(LENGTH):
    LENGTH = max_length;

print(f"Final bin length is: {LENGTH}")  # 箱子长度
df_RPNXY = pd.DataFrame(RPNXY, columns=['itemNum', 'X', 'Y'])
print(df_RPNXY)  # 装箱序列,[物品编号，X坐标，Y坐标]


# Compute Coverage Ratio
def compute_coverage_ratio(packed_items, bin_width, bin_length):
    # Merge item dimensions with packed positions
    packed_items = pd.DataFrame(packed_items, columns=['itemNum', 'X', 'Y'])
    packed_items = packed_items.merge(df_AllItem, left_on='itemNum', right_index=True)

    # Calculate total item area
    packed_items['area'] = packed_items['width'] * packed_items['length']
    total_area = packed_items['area'].sum()

    # Calculate bin area
    bin_area = bin_width * bin_length

    # Compute ratio
    coverage_ratio = total_area / bin_area
    return coverage_ratio


# Visualization of packed items
def visualize_packing(packed_items, bin_width, bin_length, all_items, coverage_ratio_result):
    """
    Visualizes the packed items in the container with correct Y-axis orientation.

    Parameters:
    - packed_items: List of [itemNum, X, Y] for packed items.
    - bin_width: Width of the container.
    - bin_length: Length of the container.
    - all_items: DataFrame containing dimensions of all items.
    """
    # Create a plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Draw the container
    ax.set_xlim(0, bin_width)
    ax.set_ylim(0, bin_length)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(f'coverage ratio: {coverage_ratio_result:.4f}')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')

    # Add grid for better visualization
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Draw each packed item
    for packed_item in packed_items:
        itemNum, X, Y = packed_item
        width, length = all_items.loc[itemNum, ['width', 'length']]

        # Bottom-left corner of the rectangle
        bottom_left_x = X - width
        bottom_left_y = Y - length

        # Create rectangle
        rect = patches.Rectangle(
            (bottom_left_x, bottom_left_y),  # Bottom-left corner
            width,
            length,
            linewidth=1,
            edgecolor='black',
            facecolor=np.random.rand(3, ),  # Random color for each item
            alpha=0.7
        )
        ax.add_patch(rect)

        # Add text annotations for dimensions and coordinates
        ax.text(X - width / 2, Y - length / 2, f'{itemNum}', color='white', ha='center', va='center', fontsize=10)
        ax.text(X, Y, f'({X}, {Y})', color='blue', fontsize=8, ha='left', va='bottom')

    # Set limits and show plot
    ax.set_xlim(0, bin_width)
    ax.set_ylim(0, bin_length)
    plt.show()


# Compute coverage ratio and visualize packing
coverage_ratio = compute_coverage_ratio(RPNXY, WIDTH, LENGTH)
print(f"Coverage Ratio: {coverage_ratio:.4f}")  # 覆盖率

# Assuming packed_items = RPNXY, bin_width = WIDTH, bin_length = LENGTH, and all_items = df_AllItem
packed_items = RPNXY  # Use RPNXY from the packing algorithm
bin_width = WIDTH  # Width of the container
bin_length = LENGTH  # Length of the container
all_items = df_AllItem  # Dimensions of all items as DataFrame

visualize_packing(packed_items, bin_width, bin_length, all_items, coverage_ratio)
