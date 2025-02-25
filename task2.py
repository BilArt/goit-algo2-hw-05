import json
import time
import mmh3
import numpy as np
import pandas as pd
from bitarray import bitarray
from collections import defaultdict

class HyperLogLog:
    def __init__(self, p=14):
        self.p = p 
        self.m = 1 << p
        self.registers = np.zeros(self.m, dtype=int)

    def add(self, item):
        hash_value = mmh3.hash(item, signed=False)
        index = hash_value & (self.m - 1)
        w = hash_value >> self.p
        self.registers[index] = max(self.registers[index], self._rho(w))

    def count(self):
        Z = np.sum(2.0 ** -self.registers)
        E = (self.m ** 2) / Z * 0.7213 / (1 + 1.079 / self.m)
        return int(E)

    def _rho(self, w):
        return (w & -w).bit_length()

def extract_ips(log_lines):
    ips = set()
    for line in log_lines:
        try:
            log_entry = json.loads(line)
            ip = log_entry.get("remote_addr")
            if ip:
                ips.add(ip)
        except json.JSONDecodeError:
            continue
    return ips

def measure_time(func, *args):
    start_time = time.time()
    result = func(*args)
    return result, time.time() - start_time

if __name__ == "__main__":
    log_data = [
        '{ "timestamp": "2024-07-29T06:25:06+03:00", "remote_addr": "80.211.38.60" }',
        '{ "timestamp": "2024-07-29T06:25:32+03:00", "remote_addr": "80.211.111.215" }',
        '{ "timestamp": "2024-07-29T06:25:33+03:00", "remote_addr": "80.211.38.60" }',
        '{ "timestamp": "2024-07-29T06:25:36+03:00", "remote_addr": "80.211.38.60" }',
        '{ "timestamp": "2024-07-29T06:25:43+03:00", "remote_addr": "80.211.38.60" }'
    ]
    
    unique_ips, exact_time = measure_time(extract_ips, log_data)
    exact_count = len(unique_ips)
    
    hll = HyperLogLog(p=14)
    for ip in unique_ips:
        hll.add(ip)
    hll_count, hll_time = measure_time(hll.count)
    
    results_df = pd.DataFrame({
        "Метод": ["Точный подсчет", "HyperLogLog"],
        "Уникальные элементы": [exact_count, hll_count],
        "Время выполнения (сек.)": [exact_time, hll_time]
    })
    
    import ace_tools as tools
    tools.display_dataframe_to_user(name="Сравнение точности и скорости", dataframe=results_df)