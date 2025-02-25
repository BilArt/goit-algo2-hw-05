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