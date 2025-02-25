import hashlib
import mmh3
import bitarray

class BloomFilter:
    def __init__(self, size=1000, num_hashes=3):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bitarray.bitarray(size)
        self.bit_array.setall(0)

    def _hashes(self, item):
        return [mmh3.hash(item, seed) % self.size for seed in range(self.num_hashes)]

    def add(self, item):
        for hash_value in self._hashes(item):
            self.bit_array[hash_value] = 1

    def contains(self, item):
        return all(self.bit_array[hash_value] for hash_value in self._hashes(item))

