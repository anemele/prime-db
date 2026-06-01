import array
import time
from pathlib import Path
from typing import Any, Callable

N = 100_000_000
PACK_FMT = "I"  # I: unsigned int

db_path = Path("db")
db_path.mkdir(exist_ok=True)
fp_spf = db_path / "spf.bin"
fp_bitmap = db_path / "bitmap.bin"


def calc():
    spf_list = [0] * N
    prime_list = []

    start = time.perf_counter()
    for i in range(2, N):
        if spf_list[i] == 0:
            spf_list[i] = i
            prime_list.append(i)
        for p in prime_list:
            ip = i * p
            if ip >= N:
                break
            spf_list[ip] = p
            if p == spf_list[i]:
                break
    end = time.perf_counter()
    print(f"calc {N} costs {end - start:.3f}s")

    def dump():
        with fp_spf.open("wb") as fp:
            array.array(PACK_FMT, spf_list).tofile(fp)

        # 移位运算优先级低于加减
        bitmap = bytearray((N >> 3) + 1)
        bitmap[0] |= 4  # 2
        for prime in prime_list:
            idx1 = prime >> 3
            idx2 = prime & 7
            bitmap[idx1] |= 1 << idx2
        with fp_bitmap.open("wb") as fp:
            fp.write(bitmap)

    return dump


def _ui(prompt: str, f: Callable[[int], Any]):
    print(prompt)
    while True:
        s = input("\n? ").strip()
        if not s:
            break
        elif s.isdigit():
            n = int(s)
            if n >= N:
                print("over max db")
            else:
                print(f(n))
        else:
            print("invalid input")


def expand():
    arr = array.array(PACK_FMT)
    arr.frombytes(fp_spf.read_bytes())
    spf_lst = arr.tolist()

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

    _ui("expand spf", expand_spf)


def check():
    bitmap = fp_bitmap.read_bytes()

    def check_n(n: int) -> bool:
        idx1 = n >> 3
        idx2 = n & 7
        bit = bitmap[idx1] & (1 << idx2)
        is_prime = not not bit
        return is_prime

    _ui("test prime", check_n)
