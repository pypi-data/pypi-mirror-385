from __future__ import annotations
from dataclasses import dataclass
from typing import List


# ----- Istisnolar -----
class DivisionByZeroError(Exception):
    pass


class InvalidOperationError(Exception):
    pass


# ----- FuzzyTriangular sinfi -----
@dataclass
class FuzzyTriangular:
    """
    Triangular fuzzy son/vektor sifatida saqlanadi:
    a   : asosiy qiymat (center)
    a1  : chap "spread" (left)
    a2  : o'ng  "spread" (right)

    Notatsiya: qiymatlarni interval sifatida ifodalash uchun
    [a - a1, a + a2]
    """
    a: float
    a1: float
    a2: float

    def __neg__(self) -> "FuzzyTriangular":
        """
        -ā = (-a, a2, a1)
        chap va o'ng dispersiyalar almashadi.
        """
        return FuzzyTriangular(-self.a, self.a2, self.a1)

    # Operator overloadlar uchun placeholders — ular modul oxirida bog'lanadi
    def __repr__(self) -> str:
        return f"FuzzyTriangular(a={self.a}, a1={self.a1}, a2={self.a2})"


# ----- Operatsiyalar -----
class FuzzyOperations:
    """Noravshan mantiqidagi barcha vektor operatsiyalari"""

    @staticmethod
    def add(v1: FuzzyTriangular, v2: FuzzyTriangular) -> FuzzyTriangular:
        """ā + b̄ = (a+b, a1 + b1, a2 + b2)"""
        return FuzzyTriangular(
            v1.a + v2.a,
            v1.a1 + v2.a1,
            v1.a2 + v2.a2
        )

    @staticmethod
    def subtract(v1: FuzzyTriangular, v2: FuzzyTriangular) -> FuzzyTriangular:
        """
        ā - b̄  = ā + (-b̄)
        -b̄ = (-b, b2, b1)  => yordamchilar: a1 + b2 , a2 + b1
        Natija: (a - b, a1 + b2, a2 + b1)
        """
        neg_v2 = -v2
        return FuzzyOperations.add(v1, neg_v2)

    @staticmethod
    def multiply(v1: FuzzyTriangular, v2: FuzzyTriangular) -> FuzzyTriangular:
        """
        Ko'paytirish: ko'plab yondashuvlar bor. Mana oddiy holat bo'yicha
        signlarga qarab formulalar (ishora kombinatsiyalari) keltirilgan.
        Eslatma: bu formulalar yozilgan qoida asosida.
        """
        a, a1, a2 = v1.a, v1.a1, v1.a2
        b, b1, b2 = v2.a, v2.a1, v2.a2

        main = a * b

        # Yordamchi komponentlarni signlarga qarab beramiz
        if a > 0 and b > 0:
            comp1 = a * b1 + b * a1
            comp2 = a * b2 + b * a2
        elif a > 0 and b < 0:
            comp1 = a * b1 - b * a1
            comp2 = a * b2 - b * a2
        elif a < 0 and b > 0:
            comp1 = -a * b1 + b * a1
            comp2 = -a * b2 + b * a2
        elif a < 0 and b < 0:
            comp1 = -a * b1 - b * a1
            comp2 = -a * b2 - b * a2
        else:
            # agar a==0 yoki b==0 bo'lsa, qayta oddiy ko'rinish
            comp1 = a * b1 + b * a1
            comp2 = a * b2 + b * a2

        return FuzzyTriangular(main, comp1, comp2)

    @staticmethod
    def divide(v1: FuzzyTriangular, v2: FuzzyTriangular) -> FuzzyTriangular:
        """
        Bo'lish — b ning asosiy komponenti nol bo'lsa xatolik.
        Formulalar signlarga qarab keltirilgan (moduldagi yozuvga mos).
        """
        if v2.a == 0:
            raise DivisionByZeroError("Nolga bo'lish mumkin emas (v2.a == 0)")

        a, a1, a2 = v1.a, v1.a1, v1.a2
        b, b1, b2 = v2.a, v2.a1, v2.a2

        main = a / b
        b2_sq = b ** 2

        if a > 0 and b > 0:
            comp1 = (a * b1 - b * a1) / b2_sq
            comp2 = (a * b2 - b * a2) / b2_sq
        elif a > 0 and b < 0:
            comp1 = (a * b1 + b * a1) / b2_sq
            comp2 = (a * b2 + b * a2) / b2_sq
        elif a < 0 and b > 0:
            comp1 = (-a * b1 + b * a1) / b2_sq
            comp2 = (-a * b2 + b * a2) / b2_sq
        elif a < 0 and b < 0:
            comp1 = (-a * b1 - b * a1) / b2_sq
            comp2 = (-a * b2 - b * a2) / b2_sq
        else:
            # a==0 holatida aniq formula: -a1 / b va -a2 / b
            if a == 0:
                comp1 = -a1 / b
                comp2 = -a2 / b
            else:
                comp1 = 0
                comp2 = 0

        return FuzzyTriangular(main, comp1, comp2)

    @staticmethod
    def dot_product(v1: FuzzyTriangular, v2: FuzzyTriangular) -> float:
        """Nuqtali (skalyar) ko'paytma: a·b + a1·b1 + a2·b2"""
        return v1.a * v2.a + v1.a1 * v2.a1 + v1.a2 * v2.a2

    @staticmethod
    def scalar_multiply(k: float, v: FuzzyTriangular) -> FuzzyTriangular:
        return FuzzyTriangular(k * v.a, k * v.a1, k * v.a2)

    @staticmethod
    def scalar_divide(v: FuzzyTriangular, k: float) -> FuzzyTriangular:
        if k == 0:
            raise DivisionByZeroError("Nolga bo'lish mumkin emas (skalyar).")
        return FuzzyTriangular(v.a / k, v.a1 / k, v.a2 / k)

    @staticmethod
    def weighted_average(vectors: List[FuzzyTriangular], weights: List[float]) -> FuzzyTriangular:
        if len(vectors) != len(weights):
            raise InvalidOperationError("Vektorlar va og'irliklar soni teng bo'lishi kerak")
        total_w = sum(weights)
        if total_w == 0:
            raise InvalidOperationError("Og'irliklar yig'indisi nol bo'lishi mumkin emas")

        ta = sum(v.a * w for v, w in zip(vectors, weights))
        ta1 = sum(v.a1 * w for v, w in zip(vectors, weights))
        ta2 = sum(v.a2 * w for v, w in zip(vectors, weights))
        return FuzzyTriangular(ta / total_w, ta1 / total_w, ta2 / total_w)


# ----- Operator overloadlarni FuzzyTriangular ga o'rnatish -----
def _add_operator_overloads():
    def add_operator(self, other):
        if isinstance(other, FuzzyTriangular):
            return FuzzyOperations.add(self, other)
        return NotImplemented

    def sub_operator(self, other):
        if isinstance(other, FuzzyTriangular):
            return FuzzyOperations.subtract(self, other)
        return NotImplemented

    def mul_operator(self, other):
        if isinstance(other, FuzzyTriangular):
            return FuzzyOperations.multiply(self, other)
        elif isinstance(other, (int, float)):
            return FuzzyOperations.scalar_multiply(other, self)
        return NotImplemented

    def truediv_operator(self, other):
        if isinstance(other, FuzzyTriangular):
            return FuzzyOperations.divide(self, other)
        elif isinstance(other, (int, float)):
            return FuzzyOperations.scalar_divide(self, other)
        return NotImplemented

    # Bind methods
    FuzzyTriangular.__add__ = add_operator
    FuzzyTriangular.__sub__ = sub_operator
    FuzzyTriangular.__mul__ = mul_operator
    FuzzyTriangular.__truediv__ = truediv_operator

    # reversed ops: ra - self etc.
    FuzzyTriangular.__radd__ = add_operator
    FuzzyTriangular.__rsub__ = lambda self, other: FuzzyOperations.subtract(
        other if isinstance(other, FuzzyTriangular) else FuzzyTriangular(other, 0, 0),
        self
    )
    FuzzyTriangular.__rmul__ = lambda self, other: FuzzyOperations.scalar_multiply(other, self)
    FuzzyTriangular.__neg__ = lambda self: FuzzyTriangular(-self.a, self.a2, self.a1)


_add_operator_overloads()


# ----- Tez tekshirish (misollar) -----
# if __name__ == "__main__":
#     # Oddiy misollar:
#     A = FuzzyTriangular(10.0, 2.0, 3.0)   # [8, 13]
#     B = FuzzyTriangular(4.0, 1.0, 0.5)    # [3, 4.5]

#     print("A:", A)
#     print("B:", B)
#     print("-B (neg):", -B)
#     print("A + B :", A + B)
#     print("A - B :", A - B)   # -> (10-4, 2 + 0.5, 3 + 1) = (6, 2.5, 4)
#     print("A * B :", A * B)
#     print("A / B :", A / B)
#     print("Dot   :", FuzzyOperations.dot_product(A, B))
