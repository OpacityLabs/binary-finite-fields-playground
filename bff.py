
from functools import reduce
from typing import List

class BFF:
    """
    An implementation of binary finite field arithmetic on fields of order 2^n using integers and bitwise operators.
    """

    def __init__(self, a: int, n: int, r: int):
        self.a = a
        self.n = n
        self.r = r

    def __add__(self, other: 'BFF') -> 'BFF':
        return BFF(self.a ^ other.a, self.n, self.r)

    def __mul__(self, other: 'BFF') -> 'BFF':
        x, y, r = self.a, other.a, 0
        while y:
            r = (r, r ^ x)[y & 1]
            y >>= 1
            x <<= 1
            x = (x, x ^ self.r)[bool(x & (self.n))]
        return BFF(r, self.n, self.r)

    def __pow__(self, pow: int) -> 'BFF':
        prod = BFF(1, self.n, self.r)
        while pow != 0:
            if pow & 1:
                prod *= self
            pow >>= 1
            self *= self
        return prod

    def __invert__(self) -> 'BFF':
        return self ** (self.n - 2)

    def __truediv__(self, other: 'BFF') -> 'BFF':
        return self * ~other

    def __len__(self) -> int:
        return int.bit_length(self.a)

    def __repr__(self) -> str:
        return f"element polynomial: {self.a}, GF(2^{self.n}), irreducible polynomial: {self.r}"

    def affine(self, affine_mat: List[List[int]], affine_c: List[int]) -> 'BFF':
        multiplicand = [int(i) for i in list(bin(self.a)[2:])][::-1]
        res = [sum([(i * n) for i, n in zip(row, multiplicand)]) % 2 for row in affine_mat]
        res = [(i + j) % 2 for i, j in zip(res, affine_c)][::-1]
        return BFF(reduce(lambda x, y: 2 * x + y, res), self.n, self.r)


def aff_from_col(col: List[int]) -> List[List[int]]:
    aff = [col]
    for a in col[::-1]:
        col = [a] + col[:-1]
        aff.append(col)
    return list(zip(*aff))


def generate_s_box() -> List[List[str]]:
    return list(
        zip(
            *[
                [
                    '0x%02x' % (~BFF((i << 4) + j, 256, r=0b100011011)).affine(
                        aff_from_col([1, 1, 1, 1, 1, 0, 0, 0]), [1, 1, 0, 0, 0, 1, 1, 0]
                    ).a
                    for i in range(0x0, 0x10)
                ]
                for j in range(0x0, 0x10)
            ]
        )
    )


def generate_inv_s_box() -> List[List[str]]:
    return list(
        zip(
            *[
                [
                    '0x%02x'
                    % (
                        ~(BFF((i << 4) + j, 256, r=0b100011011).affine(
                            aff_from_col([0, 1, 0, 1, 0, 0, 1, 0]), [1, 0, 1, 0, 0, 0, 0, 0]
                        ))
                    ).a
                    for i in range(0x0, 0x10)
                ]
                for j in range(0x0, 0x10)
            ]
        )
    )


def pprint_box(box: List[List[str]]) -> None:
    print("   ",)
    axis = ['0x%02x' % i for i in range(0x0, 0x10)][::-1]
    print("     ", ", ".join(axis[::-1]))
    for row in box:
        print(axis[-1] + ",", ", ".join(row))
        axis.pop(-1)


if __name__ == "__main__":
    # AES Rijndael S-box and inverse S-box to prove the correctness of the implementation
    pprint_box(generate_s_box())
    pprint_box(generate_inv_s_box())
