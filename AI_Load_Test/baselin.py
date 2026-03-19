import requests
import time
import statistics

URL = "http://127.0.0.1:8005/notes"

latencies = []

for _ in range(50):
    start = time.time()
    r = requests.get(URL)
    end = time.time()
    latencies.append((end - start) * 1000)

print("Average Latency:", statistics.mean(latencies), "ms")
print("Min Latency:", min(latencies), "ms")
print("Max Latency:", max(latencies), "ms")
print("Std Deviation:", statistics.stdev(latencies), "ms")