"""
Noravshan mantiqining takomillashtirilgan asosiy klassi
Uchburchak fuzzy sonlar va ular ustida amallar
"""

from __future__ import annotations
import math
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Union, List, Dict, Optional, Callable
from enum import Enum


class DefuzzificationMethod(Enum):
    """Defuzzifikatsiya usullari"""
    CENTROID = 'centroid'
    BISECTOR = 'bisector'
    MEAN_OF_MAXIMUM = 'mom'
    LARGEST_OF_MAXIMUM = 'lom'
    SMALLEST_OF_MAXIMUM = 'som'


class OperationType(Enum):
    """Amallar turlari"""
    MIN = 'min'
    MAX = 'max'
    PRODUCT = 'product'
    SUM = 'sum'
    ALGEBRAIC_PRODUCT = 'algebraic_product'
    ALGEBRAIC_SUM = 'algebraic_sum'


class FuzzyTriangular:
    """
    Noravshan mantiqidagi takomillashtirilgan uchburchak fuzzy sonlar
    
    Xususiyatlari:
    - a: maksimal qiymat (core)
    - b: chap chegarasi (support boshi)
    - c: o'ng chegarasi (support oxiri)
    
    Matematik ifoda: (a, b, c) uchun:
    μ(x) = { 0,                    x ≤ b yoki x ≥ c
           { (x - b)/(a - b),      b < x < a  
           { (c - x)/(c - a),      a ≤ x < c }
    """
    
    def __init__(self, a: float, b: float, c: float, name: str = "Triangular"):
        """
        Fuzzy uchburchak sonni yaratish
        
        Parameters:
        -----------
        a : float
            Maksimal qiymat (core)
        b : float (left)
            Chap chegarasi (support boshi)
        c : float (right)
            O'ng chegarasi (support oxiri)
        name : str
            Fuzzy son nomi
        """
        # if not (b <= a <= c):
        #     raise ValueError("b <= a <= c shart bajarilishi kerak")
            
        self.a = float(a)  # core (maksimal)
        self.b = float(b)  # chap chegarasi
        self.c = float(c)  # o'ng chegarasi
        self.name = name
        
        # Validatsiya
        self._validate()
    
    def _validate(self):
        """Qiymatlarni tekshirish"""
        if any(not isinstance(x, (int, float)) for x in [self.a, self.b, self.c]):
            raise TypeError("Barcha parametrlar son bo'lishi kerak")
        # (b <= a <= c)
        if self.b > self.a or self.a > self.c:
            raise ValueError("Shart bajarilishi kerak: b <= a <= c")
    
    # ===============================
    #  ASOSIY METODLAR
    # ===============================
    
    def membership(self, x: float) -> float:
        """
        x nuqtadagi a'zolik darajasini hisoblash
        
        Parameters:
        -----------
        x : float
            Input qiymati
            
        Returns:
        --------
        float : [0, 1] oraliqdagi a'zolik darajasi
        """
        if x <= self.b or x >= self.c:
            return 0.0
        elif self.b < x < self.a:
            if self.a == self.b:
                return 1.0
            return (x - self.b) / (self.a - self.b)
        elif self.a <= x < self.c:
            if self.c == self.a:
                return 1.0
            return (self.c - x) / (self.c - self.a)
        return 0.0
    
    def __call__(self, x: float) -> float:
        """Funksiya sifatida chaqirish"""
        return self.membership(x)
    
    # ===============================
    #  MAGIC METODLAR
    # ===============================
    
    def __repr__(self) -> str:
        return f"FuzzyTriangular(a={self.a}, b={self.b}, c={self.c}, name='{self.name}')"
    
    def __str__(self) -> str:
        return f"{self.name}({self.a}, {self.b}, {self.c})"
    
    def __eq__(self, other: object) -> bool:
        """Tenglikni tekshirish"""
        if not isinstance(other, FuzzyTriangular):
            return False
        return (math.isclose(self.a, other.a) and 
                math.isclose(self.b, other.b) and 
                math.isclose(self.c, other.c))
    
    def __hash__(self) -> int:
        return hash((self.a, self.b, self.c, self.name))
    
    # ===============================
    #  XUSUSIYATLAR
    # ===============================
    
    @property
    def support(self) -> Tuple[float, float]:
        """Support (a'zolik > 0 bo'lgan oraliq)"""
        return (self.b, self.c)
    
    @property
    def core(self) -> Tuple[float, float]:
        """Core (a'zolik = 1 bo'lgan oraliq)"""
        return (self.a, self.a)
    
    @property
    def height(self) -> float:
        """Maksimal a'zolik darajasi"""
        return 1.0
    
    @property
    def is_normal(self) -> bool:
        """Normal fuzzy to'plam (height = 1)"""
        return math.isclose(self.height, 1.0)
    
    @property
    def area(self) -> float:
        """Fuzzy to'plam yuzasi"""
        return (self.c - self.b) / 2
    
    @property
    def centroid(self) -> float:
        """Markaz nuqtasi"""
        return (self.b + self.a + self.c) / 3
    
    # ===============================
    #  ALFA-KESIM (ALPHA-CUT) OPERATSIYALARI
    # ===============================
    
    def alpha_cut(self, alpha: float) -> Tuple[float, float]:
        """
        Alfa-kesim oraliqni hisoblash
        
        Parameters:
        -----------
        alpha : float
            Alfa darajasi [0, 1]
            
        Returns:
        --------
        Tuple[float, float] : [left, right] oraliq
        """
        if not 0 <= alpha <= 1:
            raise ValueError("Alpha [0, 1] oraliqda bo'lishi kerak")
        
        if alpha == 0:
            return self.support
        elif alpha == 1:
            return self.core
        
        left = self.b + alpha * (self.a - self.b)
        right = self.c - alpha * (self.c - self.a)
        
        return (left, right)
    
    def strong_alpha_cut(self, alpha: float) -> Tuple[float, float]:
        """
        Kuchli alfa-kesim (a'zolik > alpha)
        """
        if not 0 <= alpha < 1:
            raise ValueError("Alpha [0, 1) oraliqda bo'lishi kerak")
        
        left = self.b + alpha * (self.a - self.b)
        right = self.c - alpha * (self.c - self.a)
        
        return (left, right)
    
    # ===============================
    #  DEFUZZIFIKATSIYA
    # ===============================
    
    def defuzzify(self, method: Union[str, DefuzzificationMethod] = DefuzzificationMethod.CENTROID, 
                  step: float = 0.01) -> float:
        """
        Fuzzy sonni aniq songa aylantirish
        
        Parameters:
        -----------
        method : DefuzzificationMethod
            Defuzzifikatsiya usuli
        step : float
            Hisoblash qadami
            
        Returns:
        --------
        float : Defuzzifikatsiya natijasi
        """
        if isinstance(method, str):
            method = DefuzzificationMethod(method)
        
        x_min, x_max = self.support
        x_values = np.arange(x_min, x_max + step, step)
        
        if method == DefuzzificationMethod.CENTROID:
            return self._centroid_defuzzify(x_values)
        elif method == DefuzzificationMethod.BISECTOR:
            return self._bisector_defuzzify(x_values, step)
        elif method == DefuzzificationMethod.MEAN_OF_MAXIMUM:
            return self._mean_maximum_defuzzify(x_values)
        elif method == DefuzzificationMethod.LARGEST_OF_MAXIMUM:
            return self._largest_maximum_defuzzify(x_values)
        elif method == DefuzzificationMethod.SMALLEST_OF_MAXIMUM:
            return self._smallest_maximum_defuzzify(x_values)
        else:
            raise ValueError(f"Nomatalum usul: {method}")
    
    def _centroid_defuzzify(self, x_values: np.ndarray) -> float:
        """Markaz defuzzifikatsiyasi"""
        memberships = np.array([self.membership(x) for x in x_values])
        if np.sum(memberships) == 0:
            return self.centroid
        return np.sum(x_values * memberships) / np.sum(memberships)
    
    def _bisector_defuzzify(self, x_values: np.ndarray, step: float) -> float:
        """Bisektor defuzzifikatsiyasi"""
        memberships = np.array([self.membership(x) for x in x_values])
        total_area = np.sum(memberships) * step
        
        cumulative = 0
        for i, x in enumerate(x_values):
            cumulative += memberships[i] * step
            if cumulative >= total_area / 2:
                return x
        return self.centroid
    
    def _mean_maximum_defuzzify(self, x_values: np.ndarray) -> float:
        """Maksimumlarning o'rtachasi"""
        memberships = np.array([self.membership(x) for x in x_values])
        max_val = np.max(memberships)
        max_points = x_values[np.isclose(memberships, max_val)]
        return float(np.mean(max_points))
    
    def _largest_maximum_defuzzify(self, x_values: np.ndarray) -> float:
        """Eng katta maksimum"""
        memberships = np.array([self.membership(x) for x in x_values])
        max_val = np.max(memberships)
        max_points = x_values[np.isclose(memberships, max_val)]
        return np.max(max_points)
    
    def _smallest_maximum_defuzzify(self, x_values: np.ndarray) -> float:
        """Eng kichik maksimum"""
        memberships = np.array([self.membership(x) for x in x_values])
        max_val = np.max(memberships)
        max_points = x_values[np.isclose(memberships, max_val)]
        return np.min(max_points)
    
    # ===============================
    #  ARIFMETIK AMALLAR
    # ===============================
    
    def __add__(self, other: Union[FuzzyTriangular, float]) -> FuzzyTriangular:
        """Qo'shish amali"""
        if isinstance(other, (int, float)):
            return FuzzyTriangular(self.a + other, self.b + other, self.c + other, 
                                 f"({self.name} + {other})")
        elif isinstance(other, FuzzyTriangular):
            return FuzzyTriangular(self.a + other.a, self.b + other.b, self.c + other.c,
                                 f"({self.name} + {other.name})")
        return NotImplemented
    
    def __sub__(self, other: Union[FuzzyTriangular, float]) -> FuzzyTriangular:
        """Ayirish amali"""
        if isinstance(other, (int, float)):
            return FuzzyTriangular(self.a - other, self.b - other, self.c - other,
                                f"({self.name} - {other})")
        elif isinstance(other, FuzzyTriangular):
            # ã - b̃ = (a - b₂, a₁ + b₁, a₂ + b₁)
            a_new = self.a - other.c  # a - b₂
            b_new = self.b + other.b  # a₁ + b₁
            c_new = self.c + other.b  # a₂ + b₁
            
            # Qiymatlarni tartiblash
            points = [a_new, b_new, c_new]
            points.sort()
            
            return FuzzyTriangular(
                points[1],  # core - o'rtadagi qiymat
                points[0],  # left - eng kichik
                points[2],  # right - eng katta
                f"({self.name} - {other.name})"
            )
        return NotImplemented
    
    def __mul__(self, other: Union[FuzzyTriangular, float]) -> FuzzyTriangular:
        """Ko'paytirish amali"""
        if isinstance(other, (int, float)):
            if other >= 0:
                return FuzzyTriangular(self.a * other, self.b * other, self.c * other,
                                     f"({self.name} × {other})")
            else:
                return FuzzyTriangular(self.c * other, self.b * other, self.a * other,
                                     f"({self.name} × {other})")
        elif isinstance(other, FuzzyTriangular):
            points = [self.a * other.a, self.a * other.c, 
                     self.c * other.a, self.c * other.c,
                     self.b * other.b]
            return FuzzyTriangular(min(points), self.b * other.b, max(points),
                                 f"({self.name} × {other.name})")
        return NotImplemented
    
    def __truediv__(self, other: Union[FuzzyTriangular, float]) -> FuzzyTriangular:
        """Bo'lish amali"""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Nolga bo'lish mumkin emas")
            if other > 0:
                return FuzzyTriangular(self.a / other, self.b / other, self.c / other,
                                    f"({self.name} / {other})")
            else:
                return FuzzyTriangular(self.c / other, self.b / other, self.a / other,
                                    f"({self.name} / {other})")
        elif isinstance(other, FuzzyTriangular):
            if other.b <= 0 <= other.c:
                raise ZeroDivisionError("Maxraj nolni o'z ichiga oladi")
            
            if self.a > 0 and other.a > 0:
                core = self.a / other.a
                left = (self.a * other.b + other.a * (self.a - self.b)) / (other.a * (other.a - other.b))
                right = (self.a * other.c + other.a * (self.c - self.a)) / (other.a * other.c)
            elif self.a < 0 and other.a > 0:
                core = self.a / other.a
                left = (self.a * other.b - other.a * (self.a - self.b)) / (other.a * (other.a - other.b))
                right = (self.a * other.c - other.a * (self.c - self.a)) / (other.a * other.c)
            elif self.a < 0 and other.a < 0:
                core = self.a / other.a
                left = (self.a * other.b + self.a * (other.a - other.b)) / (other.a * (other.a - other.b))
                right = ((self.a - self.b) * other.a + self.a * other.c) / (other.a * other.c)
            else:
                core = self.a / other.a
                left = (self.a * other.b - self.a * (other.a - other.b)) / (other.a * (other.a - other.b))
                right = (self.a * other.c + (self.c - self.a) * other.a) / (other.a * other.c)
            
            points = [core, left, right]
            points.sort()
            
            return FuzzyTriangular(
                points[1],
                points[0],
                points[2],
                f"({self.name} / {other.name})"
            )
        return NotImplemented
    # ===============================
    #  MANTIQIY AMALLAR
    # ===============================
    
    def union(self, other: FuzzyTriangular, method: OperationType = OperationType.MAX) -> Callable[[float], float]:
        """
        Birlashma amali
        
        Parameters:
        -----------
        other : FuzzyTriangular
            Ikkinchi fuzzy to'plam
        method : OperationType
            Birlashma usuli
            
        Returns:
        --------
        Callable : Yangi a'zolik funksiyasi
        """
        def membership_func(x: float) -> float:
            if method == OperationType.MAX:
                return max(self.membership(x), other.membership(x))
            elif method == OperationType.ALGEBRAIC_SUM:
                mu1, mu2 = self.membership(x), other.membership(x)
                return mu1 + mu2 - mu1 * mu2
            else:
                raise ValueError(f"Noto'g'ri birlashma usuli: {method}")
        
        return membership_func
    
    def intersection(self, other: FuzzyTriangular, method: OperationType = OperationType.MIN) -> Callable[[float], float]:
        """
        Kesishma amali
        
        Parameters:
        -----------
        other : FuzzyTriangular
            Ikkinchi fuzzy to'plam
        method : OperationType
            Kesishma usuli
            
        Returns:
        --------
        Callable : Yangi a'zolik funksiyasi
        """
        def membership_func(x: float) -> float:
            if method == OperationType.MIN:
                return min(self.membership(x), other.membership(x))
            elif method == OperationType.PRODUCT:
                return self.membership(x) * other.membership(x)
            elif method == OperationType.ALGEBRAIC_PRODUCT:
                return self.membership(x) * other.membership(x)
            else:
                raise ValueError(f"Noto'g'ri kesishma usuli: {method}")
        
        return membership_func
    
    def complement(self) -> Callable[[float], float]:
        """
        Komplement (inkor) amali
        """
        return lambda x: 1 - self.membership(x)
    
    # ===============================
    #  TRANSFORMATSIYALAR
    # ===============================
    
    def scale(self, factor: float) -> FuzzyTriangular:
        """Masshtabni o'zgartirish"""
        return FuzzyTriangular(self.a * factor, self.b * factor, self.c * factor,
                             f"{self.name}_scaled_{factor}")
    
    def shift(self, value: float) -> FuzzyTriangular:
        """Silmash"""
        return FuzzyTriangular(self.a + value, self.b + value, self.c + value,
                             f"{self.name}_shifted_{value}")
    
    def concentrate(self) -> FuzzyTriangular:
        """Konsentratsiya (a'zolik darajasini kvadratga oshirish)"""
        # Bu kvadratik transformatsiya emas, balki konsentratsiya
        return FuzzyTriangular(self.a, self.b, self.c, f"concentrated_{self.name}")
    
    def dilate(self) -> FuzzyTriangular:
        """Dilatatsiya (a'zolik darajasini ildiz ostiga olish)"""
        return FuzzyTriangular(self.a, self.b, self.c, f"dilated_{self.name}")
    
    # ===============================
    #  KOPHADLI (POLYNOMIAL) TRANSFORMATSIYALAR
    # ===============================
    
    def _taylor_exp(self, x: float, n: int = 10) -> float:
        """Teylor qatori orqali exp(x) hisoblash"""
        result = 0.0
        for i in range(n):
            result += (x ** i) / math.factorial(i)
        return result
    
    def _taylor_sin(self, x: float, n: int = 10) -> float:
        """Teylor qatori orqali sin(x) hisoblash"""
        result = 0.0
        for i in range(n):
            coef = (-1) ** i
            power = 2 * i + 1
            result += coef * (x ** power) / math.factorial(power)
        return result
    
    def _taylor_cos(self, x: float, n: int = 10) -> float:
        """Teylor qatori orqali cos(x) hisoblash"""
        result = 0.0
        for i in range(n):
            coef = (-1) ** i
            power = 2 * i
            result += coef * (x ** power) / math.factorial(power)
        return result
    
    def transform(self, func: Callable[[float], float], func_name: str = "custom") -> List[Tuple[float, float]]:
        """
        Fuzzy transformatsiya
        
        Parameters:
        -----------
        func : Callable
            Transformatsiya funksiyasi
        func_name : str
            Transformatsiya nomi
            
        Returns:
        --------
        List[Tuple] : (x, transformed_value) juftliklari
        """
        x_range = np.linspace(self.b, self.c, 200)
        return [(x, func(self.membership(x))) for x in x_range]
    
    def fuzzy_exp(self, n_terms: int = 10) -> List[Tuple[float, float]]:
        """Fuzzy eksponensial transformatsiya"""
        return self.transform(lambda mu: self._taylor_exp(mu, n_terms), "exp")
    
    def fuzzy_sin(self, n_terms: int = 10) -> List[Tuple[float, float]]:
        """Fuzzy sinus transformatsiya"""
        return self.transform(lambda mu: self._taylor_sin(mu, n_terms), "sin")
    
    def fuzzy_cos(self, n_terms: int = 10) -> List[Tuple[float, float]]:
        """Fuzzy kosinus transformatsiya"""
        return self.transform(lambda mu: self._taylor_cos(mu, n_terms), "cos")
    
    # ===============================
    #  VIZUALIZATSIYA
    # ===============================
    
    def plot(self, x_range: Optional[Tuple[float, float]] = None, 
             color: str = 'blue', title: Optional[str] = None,
             show_core: bool = True, show_support: bool = True,
             ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Fuzzy to'plamni chizish
        
        Parameters:
        -----------
        x_range : Tuple[float, float]
            X o'qi oralig'i
        color : str
            Chizish rangi
        title : str
            Grafik sarlavhasi
        show_core : bool
            Core ni ko'rsatish
        show_support : bool
            Support ni ko'rsatish
        ax : plt.Axes
            Matplotlib o'qi
            
        Returns:
        --------
        plt.Axes : Chizilgan grafik
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        
        if x_range is None:
            x_min, x_max = self.b - 1, self.c + 1
        else:
            x_min, x_max = x_range
        
        x = np.linspace(x_min, x_max, 1000)
        y = np.array([self.membership(xi) for xi in x])
        
        ax.plot(x, y, color=color, linewidth=2, label=self.name)
        ax.fill_between(x, y, alpha=0.2, color=color)
        
        # Core va support ni ko'rsatish
        if show_core:
            ax.axvline(self.a, color='red', linestyle='--', alpha=0.7, label='Core')
        
        if show_support:
            ax.axvline(self.b, color='green', linestyle='--', alpha=0.7, label='Support start')
            ax.axvline(self.c, color='green', linestyle='--', alpha=0.7, label='Support end')
        
        ax.set_xlabel('x')
        ax.set_ylabel('Membership Degree μ(x)')
        ax.set_title(title or f'Fuzzy Set: {self.name}')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        return ax
    
    def plot_transformation(self, transformation: str = 'exp', 
                          color: str = 'red', n_terms: int = 10):
        """
        Transformatsiyani chizish
        """
        if transformation == 'exp':
            data = self.fuzzy_exp(n_terms)
            title = f'Fuzzy Exponential Transformation: {self.name}'
        elif transformation == 'sin':
            data = self.fuzzy_sin(n_terms)
            title = f'Fuzzy Sine Transformation: {self.name}'
        elif transformation == 'cos':
            data = self.fuzzy_cos(n_terms)
            title = f'Fuzzy Cosine Transformation: {self.name}'
        else:
            raise ValueError("Transformation 'exp', 'sin' yoki 'cos' bo'lishi kerak")
        
        x_vals, y_vals = zip(*data)
        
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, color=color, linewidth=2)
        plt.title(title)
        plt.xlabel('x')
        plt.ylabel(f'{transformation}(μ(x))')
        plt.grid(True, alpha=0.3)
        plt.show()
    
    # ===============================
    #  SERIALIZATSIYA
    # ===============================
    
    def to_dict(self) -> Dict[str, Union[float, str]]:
        """Dictionary ko'rinishiga o'tkazish"""
        return {
            'a': self.a,
            'b': self.b,
            'c': self.c,
            'name': self.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Union[float, int, str]]) -> FuzzyTriangular:
        """Dictionary'dan yaratish"""
        try:
            a = float(data['a'])
            b = float(data['b'])
            c = float(data['c'])
        except KeyError as e:
            raise ValueError("Missing required keys 'a', 'b', or 'c' in data") from e
        except (TypeError, ValueError) as e:
            raise ValueError("Values for 'a', 'b', and 'c' must be numeric") from e

        return cls(
            a=a,
            b=b,
            c=c,
            name=str(data.get('name', 'Triangular'))
        )
    
    def to_json(self) -> str:
        """JSON string ga o'tkazish"""
        import json
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> FuzzyTriangular:
        """JSON string'dan yaratish"""
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    # ===============================
    #  STATIK METODLAR
    # ===============================
    
    @staticmethod
    def create_symmetric(center: float, width: float, name: str = "Symmetric") -> FuzzyTriangular:
        """
        Simmetrik fuzzy son yaratish
        """
        return FuzzyTriangular(
            center,
            center - width,
            center + width,
            name
        )
    
    @staticmethod
    def create_from_alpha_cuts(alpha_cuts: Dict[float, Tuple[float, float]], 
                             name: str = "FromAlphaCuts") -> FuzzyTriangular:
        """
        Alfa-kesimlar orqali fuzzy son yaratish
        """
        if 1.0 not in alpha_cuts:
            raise ValueError("Alpha=1.0 kesim bo'lishi kerak")
        
        core = alpha_cuts[1.0]
        if core[0] != core[1]:
            raise ValueError("Alpha=1.0 kesim bitta nuqta bo'lishi kerak")
        
        a = core[0]  # core nuqtasi
        
        if 0.0 not in alpha_cuts:
            raise ValueError("Alpha=0.0 kesim bo'lishi kerak")
        
        support = alpha_cuts[0.0]
        b, c = support  # b - chap, c - o'ng
        
        return FuzzyTriangular(a, b, c, name)


# ===============================
#  FOYDALANISH MISOLI
# ===============================

def main():
    """Asosiy funksiya - misollar"""
    
    # Fuzzy sonlar yaratish (a=core, b=chap, c=o'ng)
    young = FuzzyTriangular(20, 0, 40, "Young")           # core=20, support=(0,40)
    middle_aged = FuzzyTriangular(45, 30, 60, "MiddleAged") # core=45, support=(30,60)
    old = FuzzyTriangular(70, 50, 100, "Old")             # core=70, support=(50,100)
    
    print("Fuzzy Sonlar:")
    print(f"Yosh: {young}")
    print(f"O'rta yosh: {middle_aged}")
    print(f"Qari: {old}")
    
    # A'zolik darajalari
    age = 35
    print(f"\n{age} yosh uchun a'zolik darajalari:")
    print(f"Yosh: {young(age):.3f}")
    print(f"O'rta yosh: {middle_aged(age):.3f}")
    print(f"Qari: {old(age):.3f}")
    
    # Alfa-kesim
    alpha = 0.5
    young_alpha = young.alpha_cut(alpha)
    print(f"\nYosh uchun alpha={alpha} kesim: {young_alpha}")
    
    # Defuzzifikatsiya
    centroid = young.defuzzify()
    print(f"\nYosh fuzzy sonining markazi: {centroid:.2f}")
    
    # Arifmetik amallar
    shifted_young = young + 10
    print(f"\nYosh + 10 = {shifted_young}")
    
    # Grafik chizish
    young.plot(color='blue', show_core=True, show_support=True)
    middle_aged.plot(color='green')
    old.plot(color='red')
    plt.show()
    
    # Transformatsiya
    young.plot_transformation('exp')

if __name__ == "__main__":
    main()
