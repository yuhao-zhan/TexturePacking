#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

// Function to generate uniform random numbers within a range
int generate_uniform(int min, int max) {
    return min + rand() % (max - min + 1);
}

// Function to generate normal distributed random numbers
int generate_normal(int mean, int stddev) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return (int)(mean + z0 * stddev);
}

// Function to generate exponential distributed random numbers
int generate_exponential(int lambda) {
    double u = (double)rand() / RAND_MAX;
    return (int)(-log(1 - u) / lambda);
}

// Function to generate a single test case
void generate_test_case(const char* filename, int num_rectangles, int width_min, int width_max, int height_min, int height_max, int distribution) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "Error opening file: %s\n", filename);
        exit(1);
    }

    fprintf(file, "Given width: %d\n", width_max);
    fprintf(file, "Number of rectangles: %d\n", num_rectangles);
    fprintf(file, "Width\tHeight\n");

    for (int i = 0; i < num_rectangles; i++) {
        int width, height;

        // Generate dimensions based on the chosen distribution
        if (distribution == 0) { // Normal distribution
            width = generate_normal((width_min + width_max) / 2, (width_max - width_min) / 6);
            height = generate_normal((height_min + height_max) / 2, (height_max - height_min) / 6);
        } else if (distribution == 1) { // Skewed distribution (favoring smaller widths/heights)
            width = generate_uniform(width_min, width_max / 2);
            height = generate_uniform(height_min, height_max / 2);
        } else { // Skewed distribution (favoring larger widths/heights)
            width = generate_uniform(width_max / 2, width_max);
            height = generate_uniform(height_max / 2, height_max);
        }

        // Ensure dimensions are within bounds
        if (width < width_min) width = width_min;
        if (width > width_max) width = width_max;
        if (height < height_min) height = height_min;
        if (height > height_max) height = height_max;

        fprintf(file, "%d\t%d\n", width, height);
    }

    fclose(file);
    printf("Test case written to %s\n", filename);
}

// Main function
int main() {
    srand(time(NULL)); // Seed the random number generator

    // Parameters for test case generation
    int given_width = 100;
    int maximum_height = 50;
    int sizes[] = {10, 50, 100, 500, 1000, 3000, 5000, 8000, 10000}; // Different sizes of test cases
    //int num_given_widths = sizeof(given_widths) / sizeof(given_widths[0]);
    //int num_maximum_heights = sizeof(maximum_heights) / sizeof(maximum_heights[0]);
    int num_sizes = sizeof(sizes) / sizeof(sizes[0]);

//    // Loop through all combinations of given width and maximum height
//    for (int w = 0; w < num_given_widths; w++) {
//        for (int h = 0; h < num_maximum_heights; h++) {
//            int given_width = given_widths[w];
//            int maximum_height = maximum_heights[h];

    // Loop through all sizes of test cases
    for (int s = 0; s < num_sizes; s++) {
        int num_rectangles = sizes[s];

        // Generate test cases for 5 different distributions
        for (int d = 0; d < 3; d++) {
            char filename[100];
            sprintf(filename, "../Test_cases/test_size_%d_dist_%d.txt", num_rectangles, d+1);
            generate_test_case(filename, num_rectangles, 1, given_width, 1, maximum_height, d);
        }
    }
    printf("All test cases generated successfully.\n");
    return 0;
}