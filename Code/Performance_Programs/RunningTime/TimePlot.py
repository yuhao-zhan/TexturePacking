import time
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import Polynomial
from tools import *  # Assuming overlap and finalPos functions are defined elsewhere


# Function to read input from file
def read_input_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        given_width = int(lines[0].split(':')[1].strip())
        number_of_rectangles = int(lines[1].split(':')[1].strip())
        items = []
        for line in lines[3:]:
            width, height = map(int, line.strip().split())
            items.append([width, height])
        return given_width, number_of_rectangles, np.array(items)


# Function to perform the packing simulation
def try_pack(bin_length, itemNum, AllItem):
    max_length = 0
    Bin = [WIDTH, bin_length]
    RPNXY = []
    flagItem = np.zeros(itemNum)

    for i in range(itemNum):
        if flagItem[i] == 0:
            item = AllItem[i, :]
            itemRP = Bin
            flagOL = overlap(item, AllItem, itemRP, RPNXY)  # Assuming overlap function is defined elsewhere
            if flagOL == 0:
                itemRP = finalPos(item, AllItem, itemRP, RPNXY)  # Assuming finalPos function is defined
                if len(itemRP) > 0:
                    RPNXY.append([i, itemRP[0], itemRP[1]])
                    flagItem[i] = 1
                    if itemRP[1] > max_length:
                        max_length = itemRP[1]
    return all(flagItem), max_length, RPNXY


# Directory containing test cases
test_cases_dir = 'Test_cases'
file_list = [f for f in os.listdir(test_cases_dir) if f.endswith('.txt')]

# Data structures to store results
distributions = ['dist_1', 'dist_2', 'dist_3']  # Assuming these are the 3 distributions
input_sizes = []
average_times = []
size_to_times = {dist: {} for dist in distributions}  # Dictionary to store times for each size and distribution

# Process each test case
for filename in file_list:
    # Read the input from the file
    WIDTH, itemNum, AllItem = read_input_from_file(os.path.join(test_cases_dir, filename))

    # Extract size and distribution from the filename
    size = int(filename.split('size_')[1].split('_')[0])  # Extract size (e.g., 10 from 'size_10')
    distribution = 'dist_' + filename.split('dist_')[1].split('.txt')[
        0]  # Extract distribution (e.g., 'dist_1' from 'dist_1')

    # Check if the distribution is valid (i.e., exists in the dictionary)
    if distribution not in size_to_times:
        print(f"Warning: Distribution {distribution} not found in size_to_times.")
        continue  # Skip the current iteration if distribution is invalid

    # If the size is not in the dictionary, initialize it with an empty list
    if size not in size_to_times[distribution]:
        size_to_times[distribution][size] = []

    # Run the simulation and record the running time
    start_time = time.time()
    _, max_length, _ = try_pack(max(AllItem[:, 1]) * itemNum, itemNum, AllItem)
    end_time = time.time()

    # Calculate the execution time
    execution_time = end_time - start_time
    print(
        f"Processing file: {filename}\t Size: {size}\t Distribution: {distribution}\t Execution Time: {execution_time} seconds")

    # Append the running time to the dictionary under the corresponding distribution and size
    size_to_times[distribution][size].append(execution_time)

# Write results to CSV and plot for each distribution
for dist in distributions:
    dist_input_sizes = []
    dist_average_times = []

    # Process each size for the current distribution
    for size, times in size_to_times[dist].items():
        average_time = np.mean(times)
        dist_input_sizes.append(size)
        dist_average_times.append(average_time)

        # Write the results to a CSV file for this distribution
        result_df = pd.DataFrame({
            'Input Size': dist_input_sizes,
            'Average Running Time (seconds)': dist_average_times
        })
        result_df.to_csv(f'{dist}_running_times.csv', index=False)

    # Plotting the results for this distribution
    plt.figure(figsize=(10, 6))
    plt.scatter(dist_input_sizes, dist_average_times, label=f'{dist} - Average Running Time', color='blue')
    # plt.plot(dist_input_sizes, dist_average_times, color='red', linestyle='--', label=f'{dist} - Fitted Polynomial')

    # Fit a polynomial to the data
    p = Polynomial.fit(dist_input_sizes, dist_average_times, 2)  # Fit a quadratic polynomial
    x_fit = np.linspace(min(dist_input_sizes), max(dist_input_sizes), 100)
    y_fit = p(x_fit)

    plt.plot(x_fit, y_fit, label=f'Fitted Polynomial (Degree 2)', color='green')

    plt.xlabel('Input Size (Number of Items)')
    plt.ylabel('Average Running Time (seconds)')
    plt.title(f'Running Time vs Input Size for {dist} Distribution')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'Distribution_{dist}.png')
    plt.show()

    # Optionally, print the polynomial coefficients for this distribution
    print(f"{dist} Fitted Polynomial Coefficients: {p.coef}")
