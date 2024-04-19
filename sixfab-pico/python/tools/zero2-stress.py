import concurrent.futures
import time

# Function to calculate Fibonacci numbers - purely for CPU load
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Function to stress CPU for a specified duration in seconds
def stress_cpu(duration_seconds, num_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(fib, 1000000) for _ in range(num_threads)]
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            time.sleep(1)  # Sleep to prevent this loop from consuming CPU
        # Cancel all running tasks (if any remain)
        for future in futures:
            future.cancel()

# Example usage: Stress CPU for 10 seconds using as many threads as CPU cores
stress_cpu(10, 4)
