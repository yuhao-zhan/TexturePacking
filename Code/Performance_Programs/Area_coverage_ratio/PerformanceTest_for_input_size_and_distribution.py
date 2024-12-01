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

        # Extract Given Width and Number of Rectangles
        given_width = int(lines[0].split(':')[1].strip())
        number_of_rectangles = int(lines[1].split(':')[1].strip())

        # Extract Width and Height of Rectangles
        items = []
        for line in lines[3:]:  # Start from line 4 to skip headers
            width, height = map(int, line.strip().split())
            items.append([width, height])

        return given_width, number_of_rectangles, np.array(items)


# Compute Coverage Ratio
def compute_coverage_ratio(packed_items, bin_width, bin_length, df_AllItem):
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


# Class-based approach to avoid global variables
class PackingSimulator:
    def __init__(self, WIDTH, itemNum, AllItem):
        self.WIDTH = WIDTH
        self.itemNum = itemNum
        self.AllItem = AllItem
        self.df_AllItem = pd.DataFrame(AllItem, columns=['width', 'length'])
        self.LENGTH = max(AllItem[:, 1]) * itemNum  # 箱子长为物品中最大的长度乘以物品数目
        self.Bin = [WIDTH, self.LENGTH]  # 箱子宽度与长度
        self.max_length = 0  # 记录箱子最大长度
        self.RPNXY = []  # 清空已装入的物品记录
        self.flagItem = np.zeros(itemNum)  # 标记物品是否被装入箱子，0没有装入，1装入

    def try_pack(self, bin_length):
        self.max_length = 0
        self.Bin = [self.WIDTH, bin_length]  # 箱子宽度与长度
        self.RPNXY = []  # 清空已装入的物品记录
        self.flagItem = np.zeros(self.itemNum)  # 重新标记物品状态

        for i in range(self.itemNum):
            if self.flagItem[i] == 0:
                item = self.AllItem[i, :]
                itemRP = self.Bin  # 起始位置在箱子右上角
                flagOL = overlap(item, self.AllItem, itemRP, self.RPNXY)  # 检查是否重叠
                if flagOL == 0:
                    itemRP = finalPos(item, self.AllItem, itemRP, self.RPNXY)  # 找到物品的最终位置
                    if len(itemRP) > 0:
                        self.RPNXY.append([i, itemRP[0], itemRP[1]])  # 保存物品位置
                        self.flagItem[i] = 1  # 标记物品已装入
                        if itemRP[1] > self.max_length:  # 更新箱子最大长度
                            self.max_length = itemRP[1]
        return all(self.flagItem)  # 所有物品都装入箱子返回True，否则False


# Process all files in Test_cases directory
def process_files():
    coverage_data = np.zeros((9, 3))  # 9 input sizes, 3 distributions
    input_sizes = [10, 50, 100, 500, 1000, 3000, 5000, 8000, 10000]
    # input_sizes = [10]
    distributions = [1, 2, 3]

    for dist in distributions:
        for size_index, input_size in enumerate(input_sizes):
            filename = f"Test_cases/test_size_{input_size}_dist_{dist}.txt"
            print(f"Processing file: {filename}")
            if os.path.exists(filename):
                # Read input data from the file
                WIDTH, itemNum, AllItem = read_input_from_file(filename)

                # Create a PackingSimulator instance
                simulator = PackingSimulator(WIDTH, itemNum, AllItem)

                # Packing simulation
                max_coverage_ratio = 0
                min_coverage_ratio = 1
                for _ in range(3):
                    ran = list(range(itemNum))
                    random.shuffle(ran)  # 随机生成装箱序列
                    if simulator.try_pack(simulator.LENGTH):
                        coverage_ratio = compute_coverage_ratio(simulator.RPNXY, simulator.WIDTH, simulator.max_length,
                                                                simulator.df_AllItem)

                        if coverage_ratio > max_coverage_ratio:
                            max_coverage_ratio = coverage_ratio
                        if coverage_ratio < min_coverage_ratio:
                            min_coverage_ratio = coverage_ratio

                # Store the coverage ratio for the current input size and distribution
                coverage_data[size_index, dist - 1] = max_coverage_ratio
                print(f"Max Coverage Ratio: {max_coverage_ratio}")

    # # Write coverage data to a file
    # df_coverage = pd.DataFrame(coverage_data, columns=[f"Dist_{dist}" for dist in distributions], index=input_sizes)
        # Ensure the correct dimensions for the DataFrame
    df_coverage = pd.DataFrame(coverage_data,
                                columns=[f"Dist_{dist}" for dist in distributions],
                                index=input_sizes)

    df_coverage.to_csv("coverage_data.csv", index_label="Input Size")
    return df_coverage


# Plotting function
def plot_coverage_data(df_coverage):
    # Plot relationship between area coverage ratio and input size (fixed distribution)
    import numpy as np
    import matplotlib.pyplot as plt

    # Assuming you already have the df_coverage DataFrame populated

    for dist in range(1, 4):
        plt.figure(figsize=(8, 6))  # Larger figure size for better presentation

        # Get the x positions (index of input sizes)
        x_pos = np.arange(len(df_coverage.index))  # These will be the positions of the bars

        # Create the bar chart with custom color and width
        bars = plt.bar(x_pos, df_coverage[f"Dist_{dist}"], width=0.6, color='#4A90E2', edgecolor='black',
                       linewidth=1.2)  # Professional look with thicker edges

        # Set the x-ticks to the actual input sizes
        plt.xticks(x_pos, df_coverage.index, rotation=45, fontname='Times New Roman', fontweight='bold',
                   fontsize=12)  # Bold font for x-axis labels

        # Set y-axis font and make sure it's in bold
        plt.yticks(fontname='Times New Roman', fontweight='bold',
                   fontsize=12)  # Set y-axis font to Times New Roman (bold)

        # Add title and labels with Times New Roman font and bold
        plt.title(f"Coverage Ratio vs Input Size (Dist {dist})", fontname='Times New Roman', fontweight='bold',
                  fontsize=16)
        plt.xlabel("Input Size", fontname='Times New Roman', fontweight='bold', fontsize=14)
        plt.ylabel("Coverage Ratio", fontname='Times New Roman', fontweight='bold', fontsize=14)

        # Add the coverage ratio values on top of the bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.4f}',
                     ha='center', va='bottom', fontname='Times New Roman', fontweight='bold', fontsize=10)

        # Add gridlines for better readability (only for y-axis)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Adjust layout for better spacing and ensure no text is cut off
        plt.tight_layout()

        # Save the plot as an image
        plt.savefig(f"Performance_fixing_distribution/coverage_ratio_dist_{dist}.png")
        plt.close()

    # Plot relationship between area coverage ratio and distribution (fixed input size)
    for input_size in df_coverage.index:
        plt.figure(figsize=(8, 6))  # Larger figure size for better presentation

        # Get the x positions (index of distributions)
        x_pos = np.arange(len(df_coverage.columns))  # These will be the positions of the bars

        # Create the bar chart with custom color and width
        bars = plt.bar(x_pos, df_coverage.loc[input_size, :], width=0.6, color='#4A90E2', edgecolor='black',
                       linewidth=1.2)  # Muted Blue

        # Set the x-ticks to the actual distribution labels
        plt.xticks(x_pos, df_coverage.columns, rotation=45, fontname='Times New Roman', fontweight='bold',
                   fontsize=12)  # Bold font for x-axis labels

        # Set y-axis font and make sure it's in bold
        plt.yticks(fontname='Times New Roman', fontweight='bold',
                   fontsize=12)  # Set y-axis font to Times New Roman (bold)

        # Add title and labels with Times New Roman font and bold
        plt.title(f"Coverage Ratio vs Distribution (Input Size {input_size})", fontname='Times New Roman',
                  fontweight='bold', fontsize=16)
        plt.xlabel("Distribution", fontname='Times New Roman', fontweight='bold', fontsize=14)
        plt.ylabel("Coverage Ratio", fontname='Times New Roman', fontweight='bold', fontsize=14)

        # Add the coverage ratio values on top of the bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.4f}',
                     ha='center', va='bottom', fontname='Times New Roman', fontweight='bold', fontsize=10)

        # Add gridlines for better readability (only for y-axis)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Adjust layout for better spacing and ensure no text is cut off
        plt.tight_layout()

        # Save the plot as an image with a professional file name
        plt.savefig(f"Performance_fixing_input_size/coverage_ratio_input_size_{input_size}.png",
                    dpi=300)  # Save with high resolution
        plt.close()


# Main execution
df_coverage = process_files()
plot_coverage_data(df_coverage)
print("Processing complete! Coverage data saved in 'coverage_data.csv' and plots saved as images.")
