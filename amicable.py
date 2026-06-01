import array
from pathlib import Path

db_path = Path("./db")
assert db_path.exists()

spf_fp = db_path / "spf.bin"
size = 1_000_000

arr = array.array("I")
with open(spf_fp, "rb") as fp:
    arr.fromfile(fp, size)

factors = [{} for _ in range(size)]

ea = enumerate(arr)
next(ea)  # skip 0
next(ea)  # skip 1

for n, spf in ea:
    if n == spf:
        factors[n][spf] = 1
        continue
    d = factors[n]
    d.update(factors[n // spf])
    d[spf] = d.get(spf, 0) + 1

sum_of_real_f = [1] * size
sum_of_real_f[0] = 0

ef = enumerate(factors)
next(ef)
next(ef)

for n, fs in ef:
    kv = tuple(fs.items())
    if len(kv) == 1:
        k, v = kv[0]
        if v == 1:
            continue

        s = (k ** (v + 1) - 1) // (k - 1)
        sum_of_real_f[n] = s - n
        continue

    s = 1
    for k, v in kv:
        s *= (k ** (v + 1) - 1) // (k - 1)
    sum_of_real_f[n] = s - n

amicable_numbers = []
perfect_numbers = []
# 6
# 28
# 496
# 8128
# 33,550,336
# 8,589,869,056
# 137,438,691,328
# ...
# 52 found up to 2025-10

es = enumerate(sum_of_real_f)
next(es)
next(es)

for n, sn in es:
    if sn > n:
        continue
    elif sn < n:
        if n == sum_of_real_f[sn]:
            amicable_numbers.append((sn, n))
    else:
        perfect_numbers.append(n)

with open(db_path / "amicable_numbers.txt", "w") as fp:
    fp.write("\n".join(map(str, amicable_numbers)))
with open(db_path / "perfect_numbers.txt", "w") as fp:
    fp.write("\n".join(map(str, perfect_numbers)))
