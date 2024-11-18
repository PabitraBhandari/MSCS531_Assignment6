#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

// Struct to hold arguments for each thread
typedef struct {
    int start;
    int end;
    double scalar;
    double *x;
    double *y;
} ThreadArgs;

// Function to perform daxpy for a portion of the vector
void *daxpy_thread(void *args) {
    ThreadArgs *data = (ThreadArgs *)args;
    for (int i = data->start; i < data->end; ++i) {
        data->y[i] = data->scalar * data->x[i] + data->y[i];
    }
    return NULL;
}

int main() {
    const int vector_size = 1000;  // Size of the vectors
    const int num_threads = 4;    // Number of threads
    const double scalar = 2.0;    // Scalar multiplier

    // Allocate memory for the vectors
    double *x = malloc(vector_size * sizeof(double));
    double *y = malloc(vector_size * sizeof(double));
    if (x == NULL || y == NULL) {
        fprintf(stderr, "Error allocating memory\n");
        return 1;
    }

    // Initialize the vectors
    for (int i = 0; i < vector_size; ++i) {
        x[i] = 1.0;  // Vector x filled with 1.0
        y[i] = 2.0;  // Vector y filled with 2.0
    }

    // Create threads
    pthread_t threads[num_threads];
    ThreadArgs args[num_threads];
    int chunk_size = vector_size / num_threads;

    for (int i = 0; i < num_threads; ++i) {
        args[i].start = i * chunk_size;
        args[i].end = (i == num_threads - 1) ? vector_size : (i + 1) * chunk_size;
        args[i].scalar = scalar;
        args[i].x = x;
        args[i].y = y;
        pthread_create(&threads[i], NULL, daxpy_thread, &args[i]);
    }

    // Wait for threads to complete
    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], NULL);
    }

    // Verify the result
    for (int i = 0; i < vector_size; ++i) {
        if (y[i] != scalar * x[i] + 2.0) {
            fprintf(stderr, "Error at index %d: %f\n", i, y[i]);
            free(x);
            free(y);
            return 1;
        }
    }

    printf("Daxpy computation completed successfully!\n");

    // Free allocated memory
    free(x);
    free(y);
    return 0;
}