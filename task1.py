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

def check_password_uniqueness(bloom_filter, passwords):
    result = {}
    for password in passwords:
        if not isinstance(password, str) or not password:
            result[password] = "Некорректное значение"
        elif bloom_filter.contains(password):
            result[password] = "уже использованный"
        else:
            result[password] = "уникальный"
            bloom_filter.add(password)
    return result

if __name__ == "__main__":
    bloom = BloomFilter(size=1000, num_hashes=3)

    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    result = check_password_uniqueness(bloom, new_passwords_to_check)

    for password, status in result.items():
        print(f"Пароль '{password}' - {status}.")
