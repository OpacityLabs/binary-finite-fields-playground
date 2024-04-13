from typing import List

class Point:
    def __init__(self, x: List[int], y: List[int], f: List[int]):
        self.x = x.copy()
        self.y = y.copy()
        self.f = f.copy()
        self.n = len(self.f) - 1

    def get_x(self) -> List[int]:
        return self.x.copy()

    def get_y(self) -> List[int]:
        return self.y.copy()

    def get_f(self) -> List[int]:
        return self.f.copy()

    def get_n(self) -> int:
        return self.n

    def pad_elements(self) -> None:
        l = self.n
        self.x += [0] * (l - len(self.x))
        self.y += [0] * (l - len(self.y))

    def is_equal(self, p: 'Point') -> bool:
        x1 = self.x.copy()
        y1 = self.y.copy()
        x2 = p.x.copy()
        y2 = p.y.copy()
        l = max(len(x1), len(x2), len(y1), len(y2))
        x1 += [0] * (l - len(x1))
        y1 += [0] * (l - len(y1))
        x2 += [0] * (l - len(x2))
        y2 += [0] * (l - len(y2))
        return x1 == x2 and y1 == y2

    def on_curve(self) -> bool:
        return on_curve(self.get_x(), self.get_y(), self.get_f())

    def add(self, p: 'Point') -> 'Point':
        return add_points(self, p)

    def mult(self, k: int) -> 'Point':
        return scalar_multiply_point(self, k)

    def out(self) -> str:
        x = "".join(str(i) for i in reversed(self.x.copy()))
        y = "".join(str(i) for i in reversed(self.y.copy()))
        return "(" + x + ", " + y + ")"

    def dec_out(self) -> str:
        x = sum(self.x[i] * 2 ** i for i in range(len(self.x)))
        y = sum(self.y[i] * 2 ** i for i in range(len(self.y)))
        return "(" + str(x) + ", " + str(y) + ")"

    def print_poly(self) -> str:
        poly = "("
        poly += print_poly(self.get_x())
        poly += ", "
        poly += print_poly(self.get_y())
        poly += ")"
        return poly

    def copy(self) -> 'Point':
        return Point(self.x.copy(), self.y.copy(), self.f.copy())


def multiply_ffe(a: List[int], b: List[int], f: List[int]) -> List[int]:
    a = a.copy()
    b = b.copy()
    f = f.copy()
    if f[-1] != 1:
        print("Check to ensure the degree of F(x) is correct")
    if len(a) > len(f) or len(b) > len(f):
        print("Check to ensure A(x) and B(x) have already been reduced")
    l = len(f)
    a += [0] * (l - len(a))
    b += [0] * (l - len(b))
    c = [0] * (l * 2)
    for i in range(l):
        c = add_ffe(c, b[i] * a)
        a = [0] + a
    c.reverse()
    f.reverse()
    if c.count(1) == 0:
        return [0] * (l - 1)
    c = c[c.index(1):]
    f = f[c.index(1):]
    while len(c) >= len(f):
        c = add_ffe(c, f)
        c = c[c.index(1):]
    c.reverse()
    return c


def inverse_ffe(a: List[int], f: List[int]) -> List[int]:
    m = len(f) - 1
    temp = multiply_ffe(a, a, f)
    output = temp.copy()
    while m > 2:
        temp = multiply_ffe(temp, temp, f)
        output = multiply_ffe(output, temp, f)
        m -= 1
    return output


def add_ffe(a: List[int], b: List[int]) -> List[int]:
    a = a.copy()
    b = b.copy()
    l = max(len(a), len(b))
    a += [0] * (l - len(a))
    b += [0] * (l - len(b))
    c = []
    for i in range(l):
        c.append(a[i] ^ b[i])
    return c


def add_points(p1: 'Point', p2: 'Point') -> 'Point':
    f = p1.get_f()
    if p1.is_equal(p2):
        t1 = multiply_ffe(p1.get_y(), inverse_ffe(p1.get_x(), f), f)
        t2 = p1.get_x()
        s = add_ffe(t1, t2)
        t1 = multiply_ffe(s, s, f)
        t2 = s
        t3 = [1]
        x3 = add_ffe(t1, t2)
        x3 = add_ffe(x3, t3)
    else:
        num = add_ffe(p1.get_y(), p2.get_y())
        den = add_ffe(p1.get_x(), p2.get_x())
        s = multiply_ffe(num, inverse_ffe(den, f), f)
        t1 = add_ffe(multiply_ffe(s, s, f), s)
        t2 = add_ffe(p1.get_x(), p2.get_x())
        t3 = [1]
        x3 = add_ffe(t1, t2)
        x3 = add_ffe(x3, t3)
    t1 = multiply_ffe(add_ffe(p1.get_x(), x3), s, f)
    t2 = x3
    t3 = p1.get_y()
    y3 = add_ffe(t1, t2)
    y3 = add_ffe(y3, t3)
    p3 = Point(x3, y3, f)
    return p3


def scalar_multiply_point(p: 'Point', k: int) -> 'Point':
    temp = p.copy()
    output = 0
    k = int2bin(k)
    for i in k:
        if i == 1:
            if output == 0:
                output = temp.copy()
            else:
                output = add_points(output, temp)
        temp = add_points(temp, temp)
    return output


def on_curve(x: List[int], y: List[int], f: List[int]) -> bool:
    l = len(f) - 1
    left = add_ffe(multiply_ffe(y, y, f), multiply_ffe(x, y, f))
    left += [0] * (l - len(left))
    t2 = multiply_ffe(x, x, f)
    t1 = multiply_ffe(x, t2, f)
    t3 = [1]
    right = add_ffe(t1, t2)
    right = add_ffe(right, t3)
    right += [0] * (l - len(right))
    if left == right:
        return True
    else:
        return False


def order_point(a: 'Point', p: 'Point', n: int) -> int:
    temp = p.copy()
    for k in range(1, n):
        if temp.is_equal(a):
            break
        temp = add_points(temp, p)
    for i in range(1, n + 1):
        if k * i % n == 0:
            return i
    return 0


def order_simple(i: int, e: int) -> int:
    for x in range(1, e + 1):
        if i * x % e == 0:
            return x
    return 0


def number_points(f: List[int]) -> int:
    point_list = []
    l = len(f) - 1
    i = 0
    for xi in range(2 ** l):
        x = int2bin(xi)
        for yi in range(2 ** l):
            y = int2bin(yi)
            if on_curve(x, y, f):
                i += 1
                point_list.append(Point(x, y, f))
        if xi % 30 == 0:
            print("Found", xi, "points so far...")
    i += 1
    print("Number of Points =", str(i))
    return i


def maximal_points(p: 'Point', n: int) -> int:
    p.pad_elements()
    test_point = p.copy()
    i = 1
    while True:
        order = order_simple(i, n)
        if test_point.on_curve() == False:
            print("Error: Point", test_point.out(), "not on curve!")
            break
        if order == n:
            print(i, "P =", test_point.out(), "ord =", str(order))
        if test_point.get_x() == p.get_x() and i > 1 and i < n - 1:
            print("Error: did not start with primitive element")
            break
        if i == n - 1:
            break
        i += 1
        test_point = add_points(test_point, p)
        test_point.pad_elements()
    return 0

def print_poly(p: List[int]) -> str:
    output = ""
    if p[0] == 1:
        output = "1"
    for i in range(1, len(p)):
        if p[i] == 1:
            output = "X^" + str(i) + " + " + output
    if output[-2] == "+":
        output = output[0:-3]
    return output


def exp2bin(exp: List[int]) -> List[int]:
    output = [0] * (max(exp) + 1)
    for i in exp:
        output[i] = 1
    return output


def str2bin(s: str) -> List[int]:
    s = list(s)
    s.reverse()
    for i in range(len(s)):
        s[i] = int(s[i])
    return s


def hex2bin(h: str) -> List[int]:
    output = []
    hex_table = [
        "0000", "0001", "0010", "0011",
        "0100", "0101", "0110", "0111",
        "1000", "1001", "1010", "1011",
        "1100", "1101", "1110", "1111"
    ]
    for c in h:
        output += list(hex_table[int(c, 16)])
    output.reverse()
    for i in range(len(output)):
        output[i] = int(output[i])
    return output


def int2bin(i: int) -> List[int]:
    if i == 0:
        return [0]
    h = hex(i)[2:]
    output = hex2bin(h)
    output.reverse()
    output = output[output.index(1):]
    output.reverse()
    return output

if __name__ == "__main__":
    f = exp2bin([9, 8, 0])
    x_p = exp2bin([1, 0])
    y_p = exp2bin([5, 4, 3])
    p = Point(x_p, y_p, f)
    p.pad_elements()
    n = 518
    a = 13
    b = 31
    print("Primitive point P =", p.out())
    print("Step 1")
    a_point = scalar_multiply_point(p, a)
    b_point = scalar_multiply_point(p, b)
    print("Alice computes 13P = A =", a_point.out())
    print("And sends point A to Bob")
    print("Bob computes 31P = B =", b_point.out())
    print("And sends point B to Alice")
    print("Step 2")
    a2_point = scalar_multiply_point(b_point, a)
    b2_point = scalar_multiply_point(a_point, b)
    print("Alice receives B =", b_point.out(), "and computes 13B =", a2_point.out())
    print("Bob receives A =", a_point.out(), "and computes 31A =", b2_point.out())
    c_point = scalar_multiply_point(p, a * b)
    print("Both parties have the shared key", c_point.out())
    print("Maximal Points")
    maximal_points(p, n)
