"""
Noravshan mantiqidagi vektor operatsiyalari
"""

from __future__ import annotations
from typing import Tuple, List
from .core import FuzzyTriangular
from .exceptions import DivisionByZeroError, InvalidOperationError

class FuzzyOperations:
    """
    Noravshan mantiqidagi barcha vektor operatsiyalari
    """
    
    @staticmethod
    def add(v1: FuzzyTriangular, v2: FuzzyTriangular) -> FuzzyTriangular:
        """
        Vektor qo'shish: ā + b̄ = (a+b, a₁+b₁, a₂+b₂)
        
        Bu operatsiya ishoralardan qat'iy nazar bir xil
        """
        return FuzzyTriangular(
            v1.a + v2.a,
            v1.a1 + v2.a1,
            v1.a2 + v2.a2
        )
    
    @staticmethod
    def subtract(v1: FuzzyTriangular, v2: FuzzyTriangular) -> FuzzyTriangular:
        """
        Vektor ayirish: ā - b̄ = (a-b, a₁-b₁, a₂-b₂)
        
        Bu operatsiya ishoralardan qat'iy nazar bir xil
        """
        return FuzzyTriangular(
            v1.a - v2.a,
            v1.a1 - v2.a1,
            v1.a2 - v2.a2
        )
    
    @staticmethod
    def multiply(v1: FuzzyTriangular, v2: FuzzyTriangular) -> FuzzyTriangular:
        """
        Vektor ko'paytirish: ā · b̄
        
        Ishoraga qarab turli xil formulalar qo'llaniladi:
        
        Ishora kombinatsiyalari:
        1. a > 0, b > 0: (ab, a·b₁ + b·a₁, a·b₂ + b·a₂)
        2. a > 0, b < 0: (ab, a·b₁ - b·a₁, a·b₂ - b·a₂)
        3. a < 0, b > 0: (ab, -a·b₁ + b·a₁, -a·b₂ + b·a₂)
        4. a < 0, b < 0: (ab, -a·b₁ - b·a₁, -a·b₂ - b·a₂)
        """
        a, a1, a2 = v1.a, v1.a1, v1.a2
        b, b1, b2 = v2.a, v2.a1, v2.a2
        
        # Asosiy komponent
        main_component = a * b
        
        # Yordamchi komponentlar
        if a > 0 and b > 0:
            # Case 1: a > 0, b > 0
            comp1 = a * b1 + b * a1
            comp2 = a * b2 + b * a2
        elif a > 0 and b < 0:
            # Case 2: a > 0, b < 0
            comp1 = a * b1 - b * a1
            comp2 = a * b2 - b * a2
        elif a < 0 and b > 0:
            # Case 3: a < 0, b > 0
            comp1 = -a * b1 + b * a1
            comp2 = -a * b2 + b * a2
        elif a < 0 and b < 0:
            # Case 4: a < 0, b < 0
            comp1 = -a * b1 - b * a1
            comp2 = -a * b2 - b * a2
        else:
            # Nol holatlari
            if a == 0 or b == 0:
                comp1 = a * b1 + b * a1
                comp2 = a * b2 + b * a2
            else:
                comp1 = 0
                comp2 = 0
        
        return FuzzyTriangular(main_component, comp1, comp2)
    
    @staticmethod
    def divide(v1: FuzzyTriangular, v2: FuzzyTriangular) -> FuzzyTriangular:
        """
        Vektor bo'lish: ā / b̄
        
        Ishoraga qarab turli xil formulalar qo'llaniladi:
        
        Ishora kombinatsiyalari:
        1. a > 0, b > 0: (a/b, (a·b₁ - b·a₁)/b², (a·b₂ - b·a₂)/b²)
        2. a > 0, b < 0: (a/b, (a·b₁ + b·a₁)/b², (a·b₂ + b·a₂)/b²)
        3. a < 0, b > 0: (a/b, (-a·b₁ + b·a₁)/b², (-a·b₂ + b·a₂)/b²)
        4. a < 0, b < 0: (a/b, (-a·b₁ - b·a₁)/b², (-a·b₂ - b·a₂)/b²)
        """
        if v2.a == 0:
            raise DivisionByZeroError("Nolga bo'lish mumkin emas")
        
        a, a1, a2 = v1.a, v1.a1, v1.a2
        b, b1, b2 = v2.a, v2.a1, v2.a2
        
        # Asosiy komponent
        main_component = a / b
        b_squared = b ** 2
        
        # Yordamchi komponentlar
        if a > 0 and b > 0:
            # Case 1: a > 0, b > 0
            comp1 = (a * b1 - b * a1) / b_squared
            comp2 = (a * b2 - b * a2) / b_squared
        elif a > 0 and b < 0:
            # Case 2: a > 0, b < 0
            comp1 = (a * b1 + b * a1) / b_squared
            comp2 = (a * b2 + b * a2) / b_squared
        elif a < 0 and b > 0:
            # Case 3: a < 0, b > 0
            comp1 = (-a * b1 + b * a1) / b_squared
            comp2 = (-a * b2 + b * a2) / b_squared
        elif a < 0 and b < 0:
            # Case 4: a < 0, b < 0
            comp1 = (-a * b1 - b * a1) / b_squared
            comp2 = (-a * b2 - b * a2) / b_squared
        else:
            # Nol holatlari
            if a == 0:
                comp1 = -a1 / b
                comp2 = -a2 / b
            else:
                comp1 = 0
                comp2 = 0
        
        return FuzzyTriangular(main_component, comp1, comp2)
    
    @staticmethod
    def dot_product(v1: FuzzyTriangular, v2: FuzzyTriangular) -> float:
        """
        Nuqtali ko'paytma (skalyar ko'paytma)
        a·b + a₁·b₁ + a₂·b₂
        """
        return v1.a * v2.a + v1.a1 * v2.a1 + v1.a2 * v2.a2
    
    @staticmethod
    def scalar_multiply(scalar: float, vector: FuzzyTriangular) -> FuzzyTriangular:
        """
        Skalyar ko'paytma: k · ā
        """
        return FuzzyTriangular(
            scalar * vector.a,
            scalar * vector.a1,
            scalar * vector.a2
        )
    
    @staticmethod
    def scalar_divide(vector: FuzzyTriangular, scalar: float) -> FuzzyTriangular:
        """
        Skalyarga bo'lish: ā / k
        """
        if scalar == 0:
            raise DivisionByZeroError("Nolga bo'lish mumkin emas")
        
        return FuzzyTriangular(
            vector.a / scalar,
            vector.a1 / scalar,
            vector.a2 / scalar
        )
    
    @staticmethod
    def weighted_average(vectors: List[FuzzyTriangular], 
                        weights: List[float]) -> FuzzyTriangular:
        """
        Vektorlarning og'irlikli o'rtachasini hisoblash
        """
        if len(vectors) != len(weights):
            raise InvalidOperationError("Vektorlar va og'irliklar soni teng bo'lishi kerak")
        
        if sum(weights) == 0:
            raise InvalidOperationError("Og'irliklar yig'indisi nol bo'lishi mumkin emas")
        
        total_a = 0
        total_a1 = 0
        total_a2 = 0
        
        for vector, weight in zip(vectors, weights):
            total_a += vector.a * weight
            total_a1 += vector.a1 * weight
            total_a2 += vector.a2 * weight
        
        total_weight = sum(weights)
        
        return FuzzyTriangular(
            total_a / total_weight,
            total_a1 / total_weight,
            total_a2 / total_weight
        )

# Operator overloading uchun qo'shimcha metodlar
def _add_operator_overloads():
    """FuzzyTriangular klassiga operator overloading qo'shish"""
    
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
    
    # Operatorlarni klassga qo'shish
    FuzzyTriangular.__add__ = add_operator
    FuzzyTriangular.__sub__ = sub_operator
    FuzzyTriangular.__mul__ = mul_operator
    FuzzyTriangular.__truediv__ = truediv_operator
    FuzzyTriangular.__radd__ = add_operator
    FuzzyTriangular.__rsub__ = lambda self, other: FuzzyOperations.subtract(
        other if isinstance(other, FuzzyTriangular) else FuzzyTriangular(other, 0, 0), 
        self
    )
    FuzzyTriangular.__rmul__ = lambda self, other: FuzzyOperations.scalar_multiply(other, self)

# Operator overloading ni faollashtirish
_add_operator_overloads()
