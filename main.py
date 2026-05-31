import array
import math
import time
from pathlib import Path

spf_list = [0, 1, 2, 3, 2, 5, 2]
# Python 切片是浅拷贝，因此这里只保留奇素数
prime_list = [
    # 2,
    3,
    5,
]
N = 10000000
PACK_FMT = "I"  # I: unsigned int

db_path = Path("db")
db_path.mkdir(exist_ok=True)
fp_spf = db_path / "spf.bin"
fp_prime = db_path / "prime.txt"
fp_bitmap = db_path / "bitmap.bin"


def _op(num: int) -> None:
    if not num & 1:
        spf_list.append(2)
        return

    bound = math.isqrt(num)
    for prime in prime_list:
        if prime > bound:
            break
        if not num % prime:
            spf_list.append(prime)
            return

    spf_list.append(num)
    prime_list.append(num)


def calc():
    n = len(spf_list)
    start = time.perf_counter()
    for num in range(n, N):
        _op(num)
    end = time.perf_counter()
    print(f"calc {N} costs {end - start:.3f}s")


def dump():
    with fp_spf.open("wb") as fp:
        array.array(PACK_FMT, spf_list).tofile(fp)

    with fp_prime.open("w") as fp:
        fp.write("2\n")
        fp.write("\n".join(map(str, prime_list)))

    # 移位运算优先级低于加减
    bitmap = bytearray((N >> 3) + 1)
    bitmap[0] |= 4  # 2
    for prime in prime_list:
        idx1 = prime >> 3
        idx2 = prime & 7
        bitmap[idx1] |= 1 << idx2
    with fp_bitmap.open("wb") as fp:
        fp.write(bitmap)


def check():
    arr = array.array(PACK_FMT)
    arr.frombytes(fp_spf.read_bytes())
    spf_lst = arr.tolist()
    bitmap = fp_bitmap.read_bytes()

    def expand_spf(n: int) -> str:
        parts = []
        while n > 1:
            p = spf_lst[n]
            cnt = 0
            while n % p == 0:
                cnt += 1
                n //= p
            parts.append(f"{p}^{cnt}" if cnt > 1 else str(p))
        return "*".join(parts)

    def check(n: int) -> bool:
        idx1 = n >> 3
        idx2 = n & 7
        bit = bitmap[idx1] & (1 << idx2)
        is_prime = not not bit
        if is_prime:
            # print(n)
            print("prime")
        else:
            print(expand_spf(n))
        return is_prime

    print("test if an integer is prime")
    while True:
        s = input("\n? ").strip()
        if not s:
            break
        elif s.isdigit():
            check(int(s))
        else:
            print("invalid input")
