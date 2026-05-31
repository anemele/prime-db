import math
import sys
import time

num_list = [
    {0: 1},
    {1: 1},
    {2: 1},
    {3: 1},
    {2: 2},
    {5: 1},
    {2: 1, 3: 1},
]
# Python 切片是浅拷贝，因此这里只保留奇素数
prime_list = [
    # 2,
    3,
    5,
]
N = 10000000


def _append(idx: int, val: int) -> None:
    d = num_list[idx].copy()
    d[val] = d.get(val, 0) + 1
    num_list.append(d)


def _op(num: int) -> None:
    if not num & 1:
        _append(num >> 1, 2)
        return

    bound = math.isqrt(num)
    for prime in prime_list:
        if prime > bound:
            break
        if num % prime == 0:
            _append(num // prime, prime)
            return

    num_list.append({num: 1})
    prime_list.append(num)


def calc():

    n = len(num_list)
    start = time.perf_counter()
    for num in range(n, N):
        if not num & 0x100000:
            sys.stdout.write(f"\r{num / N * 100:.2f}%")
        _op(num)
    end = time.perf_counter()
    print(f"\rcalc {N} costs {end - start:.3f}s")


def dump():
    with open("db.txt", "w") as fp:
        for num in num_list:
            line = "*".join(
                str(prime) if power == 1 else f"{prime}^{power}"
                for prime, power in sorted(num.items())
            )
            fp.write(line)
            fp.write("\n")

    with open("prime.txt", "w") as fp:
        fp.write("2\n")
        fp.write("\n".join(map(str, prime_list)))

    # 移位运算优先级低于加减
    bitmap = bytearray((N >> 3) + 1)
    bitmap[0] |= 4  # 2
    for prime in prime_list:
        idx1 = prime >> 3
        idx2 = prime & 7
        bitmap[idx1] |= 1 << idx2
    with open("bitmap.bin", "wb") as fp:
        fp.write(bitmap)


def check():
    with open("db.txt") as fp:
        data = fp.read().splitlines()
    with open("bitmap.bin", "rb") as fp:
        bitmap = fp.read()

    def check(n: int) -> bool:

        idx1 = n >> 3
        idx2 = n & 7
        bit = bitmap[idx1] & (1 << idx2)
        is_prime = not not bit
        print(data[n])
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
