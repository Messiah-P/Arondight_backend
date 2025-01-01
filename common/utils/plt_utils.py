import uuid
import hashlib


def generate_unique_8digit():
    # 生成 UUID 并计算哈希值
    hash_value = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    # 将哈希值转换为整数，并限制为 8 位数字范围
    return int(hash_value, 16) % 90_000_000 + 10_000_000

# if __name__ == "__main__":
#     for _ in range(5):
#         print(generate_unique_8digit())