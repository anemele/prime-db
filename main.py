import array
import struct
import time
from pathlib import Path
from typing import Any, Callable

N = 100_000_000
PACK_FMT = "I"  # I: unsigned int
ITEM_SIZE = 4
_ITEM_SIZE_BITS = 2
assert ITEM_SIZE == struct.calcsize(PACK_FMT)

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
    fp = fp_spf.open("rb")

    def expand_spf(n: int) -> str:
        parts = []
        while n > 1:
            fp.seek(n << _ITEM_SIZE_BITS)
            bs = fp.read(ITEM_SIZE)
            p: int = struct.unpack(PACK_FMT, bs)[0]
            cnt = 0
            while n % p == 0:
                cnt += 1
                n //= p
            parts.append(f"{p}^{cnt}" if cnt > 1 else str(p))
        return "*".join(parts)

    _ui("expand spf", expand_spf)
    fp.close()


def check():
    fp = fp_bitmap.open("rb")

    def check_n(n: int) -> bool:
        fp.seek(n >> 3)
        byte = fp.read(1)[0]
        bit = byte & (1 << (n & 7))
        is_prime = not not bit
        return is_prime

    _ui("test prime", check_n)
    fp.close()
