"""
Noravshan mantiqining asosiy vektor klassi
"""

from __future__ import annotations
from typing import Tuple, Union, List
from .exceptions import DivisionByZeroError, InvalidVectorError

class FuzzyTriangular:
    """
    Noravshan mantiqidagi uchburchak fuzzy sonlar (a, a₁, a₂)
    
    Bu klass uch o'lchovli vektorlar bilan ishlash imkonini beradi:
    ā = (a, a₁, a₂)
    
    Bu yerda:
    - a: asosiy komponent (markaz)
    - a₁: chap taraf diffuzligi
    - a₂: o'ng taraf diffuzligi
    """
    
    def __init__(self, a: float, a1: float, a2: float):
        """
        Fuzzy uchburchak sonni yaratish
        
        Parameters:
        -----------
        a : float
            Asosiy komponent (markaz)
        a1 : float
            Birinchi yordamchi komponent (chap diffuzlik)
        a2 : float
            Ikkinchi yordamchi komponent (o'ng diffuzlik)
        """
        self.a = float(a)
        self.a1 = float(a1)
        self.a2 = float(a2)
        
        # Vektorning to'g'ri ekanligini tekshirish
        self._validate()
    
    def _validate(self):
        """Vektor qiymatlarini tekshirish"""
        if not all(isinstance(x, (int, float)) for x in [self.a, self.a1, self.a2]):
            raise InvalidVectorError("Barcha komponentlar son bo'lishi kerak")
    
    def __repr__(self) -> str:
        return f"FuzzyTriangular(a={self.a}, a1={self.a1}, a2={self.a2})"
    
    def __str__(self) -> str:
        return f"({self.a}, {self.a1}, {self.a2})"
    
    def __eq__(self, other: object) -> bool:
        """Vektorlarning tengligini tekshirish"""
        if not isinstance(other, FuzzyTriangular):
            return False
        return (self.a == other.a and 
                self.a1 == other.a1 and 
                self.a2 == other.a2)
    
    def __hash__(self) -> int:
        return hash((self.a, self.a1, self.a2))
    
    @property
    def components(self) -> Tuple[float, float, float]:
        """Vektor komponentlarini qaytarish"""
        return (self.a, self.a1, self.a2)
    
    @property
    def is_positive(self) -> bool:
        """Vektor musbatmi?"""
        return self.a > 0
    
    @property
    def is_negative(self) -> bool:
        """Vektor manfimi?"""
        return self.a < 0
    
    @property
    def is_zero(self) -> bool:
        """Vektor nolmi?"""
        return self.a == 0
    
    def copy(self) -> FuzzyTriangular:
        """Vektorning nusxasini yaratish"""
        return FuzzyTriangular(self.a, self.a1, self.a2)
    
    def to_dict(self) -> dict:
        """Vektorni dictionary ko'rinishida qaytarish"""
        return {
            'a': self.a,
            'a1': self.a1,
            'a2': self.a2
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> FuzzyTriangular:
        """Dictionary'dan vektor yaratish"""
        return cls(data['a'], data['a1'], data['a2'])
    
    def magnitude(self) -> float:
        """
        Vektor magnitudasini hisoblash
        √(a² + a₁² + a₂²)
        """
        import math
        return math.sqrt(self.a**2 + self.a1**2 + self.a2**2)
    
    def normalize(self) -> FuzzyTriangular:
        """
        Vektorni normalizatsiya qilish
        """
        mag = self.magnitude()
        if mag == 0:
            return FuzzyTriangular(0, 0, 0)
        return FuzzyTriangular(
            self.a / mag,
            self.a1 / mag,
            self.a2 / mag
        )
    
    def is_similar(self, other: FuzzyTriangular, tolerance: float = 1e-6) -> bool:
        """
        Vektorlar o'xshashligini tekshirish
        """
        if not isinstance(other, FuzzyTriangular):
            return False
        
        return (abs(self.a - other.a) < tolerance and
                abs(self.a1 - other.a1) < tolerance and
                abs(self.a2 - other.a2) < tolerance)
        