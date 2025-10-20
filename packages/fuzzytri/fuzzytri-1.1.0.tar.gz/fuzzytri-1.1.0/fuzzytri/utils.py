"""
Yordamchi funksiyalar va konvertatsiya operatsiyalari
"""

import math
import json
from typing import List, Dict, Any, Tuple
from .core import FuzzyTriangular
from .operations import FuzzyOperations
from .exceptions import InvalidVectorError

class FuzzyUtils:
    """
    Noravshan mantiqi uchun yordamchi funksiyalar
    """
    
    @staticmethod
    def create_zero_vector() -> FuzzyTriangular:
        """Nol vektor yaratish"""
        return FuzzyTriangular(0, 0, 0)
    
    @staticmethod
    def create_unit_vector() -> FuzzyTriangular:
        """Birlik vektor yaratish"""
        return FuzzyTriangular(1, 0, 0)
    
    @staticmethod
    def create_symmetric(a: float, spread: float) -> FuzzyTriangular:
        """
        Simmetrik fuzzy son yaratish
        
        Parameters:
        -----------
        a : float
            Markaziy qiymat
        spread : float
            Diffuzlik (ikkala tomonga)
        """
        return FuzzyTriangular(a, spread, spread)
    
    @staticmethod
    def distance(v1: FuzzyTriangular, v2: FuzzyTriangular, 
                metric: str = 'euclidean') -> float:
        """
        Vektorlar orasidagi masofani hisoblash
        
        Parameters:
        -----------
        v1, v2 : FuzzyTriangular
            Vektorlar
        metric : str
            Metrika turi: 'euclidean', 'manhattan', 'chebyshev'
        """
        if metric == 'euclidean':
            return math.sqrt(
                (v1.a - v2.a)**2 + 
                (v1.a1 - v2.a1)**2 + 
                (v1.a2 - v2.a2)**2
            )
        elif metric == 'manhattan':
            return (
                abs(v1.a - v2.a) + 
                abs(v1.a1 - v2.a1) + 
                abs(v1.a2 - v2.a2)
            )
        elif metric == 'chebyshev':
            return max(
                abs(v1.a - v2.a),
                abs(v1.a1 - v2.a1),
                abs(v1.a2 - v2.a2)
            )
        else:
            raise ValueError(f"Noto'g'ri metrika: {metric}")
    
    @staticmethod
    def similarity(v1: FuzzyTriangular, v2: FuzzyTriangular, 
                  tolerance: float = 1e-6) -> float:
        """
        Vektorlar o'xshashlik darajasini hisoblash [0, 1]
        """
        dist = FuzzyUtils.distance(v1, v2)
        max_possible_dist = FuzzyUtils.distance(
            FuzzyTriangular(0, 0, 0),
            FuzzyTriangular(1, 1, 1)
        )
        return max(0, 1 - dist / max_possible_dist)
    
    @staticmethod
    def to_json(vector: FuzzyTriangular) -> str:
        """Vektorni JSON formatiga o'tkazish"""
        return json.dumps(vector.to_dict())
    
    @staticmethod
    def from_json(json_str: str) -> FuzzyTriangular:
        """JSON'dan vektor yaratish"""
        data = json.loads(json_str)
        return FuzzyTriangular.from_dict(data)
    
    @staticmethod
    def batch_operations(vectors1: List[FuzzyTriangular], 
                        vectors2: List[FuzzyTriangular],
                        operation: str) -> List[FuzzyTriangular]:
        """
        Vektorlar ustida ketma-ket operatsiyalar bajarish
        
        Parameters:
        -----------
        vectors1, vectors2 : List[FuzzyTriangular]
            Vektorlar ro'yxati
        operation : str
            Operatsiya turi: 'add', 'subtract', 'multiply', 'divide'
        """
        if len(vectors1) != len(vectors2):
            raise ValueError("Vektorlar ro'yxatlari uzunligi teng bo'lishi kerak")
        
        operations_map = {
            'add': FuzzyOperations.add,
            'subtract': FuzzyOperations.subtract,
            'multiply': FuzzyOperations.multiply,
            'divide': FuzzyOperations.divide
        }
        
        if operation not in operations_map:
            raise ValueError(f"Noto'g'ri operatsiya: {operation}")
        
        op_func = operations_map[operation]
        results = []
        
        for v1, v2 in zip(vectors1, vectors2):
            try:
                result = op_func(v1, v2)
                results.append(result)
            except Exception as e:
                results.append(FuzzyTriangular(0, 0, 0))  # Xato bo'lsa nol qaytarish
        
        return results
    
    @staticmethod
    def statistical_analysis(vectors: List[FuzzyTriangular]) -> Dict[str, Any]:
        """
        Vektorlar to'plami uchun statistik tahlil
        """
        if not vectors:
            return {}
        
        n = len(vectors)
        
        # O'rtacha qiymatlar
        mean_a = sum(v.a for v in vectors) / n
        mean_a1 = sum(v.a1 for v in vectors) / n
        mean_a2 = sum(v.a2 for v in vectors) / n
        
        # Dispersiya
        var_a = sum((v.a - mean_a)**2 for v in vectors) / n
        var_a1 = sum((v.a1 - mean_a1)**2 for v in vectors) / n
        var_a2 = sum((v.a2 - mean_a2)**2 for v in vectors) / n
        
        return {
            'count': n,
            'mean': FuzzyTriangular(mean_a, mean_a1, mean_a2),
            'variance': FuzzyTriangular(var_a, var_a1, var_a2),
            'std_deviation': FuzzyTriangular(
                math.sqrt(var_a), 
                math.sqrt(var_a1), 
                math.sqrt(var_a2)
            ),
            'min_a': min(v.a for v in vectors),
            'max_a': max(v.a for v in vectors),
            'min_a1': min(v.a1 for v in vectors),
            'max_a1': max(v.a1 for v in vectors),
            'min_a2': min(v.a2 for v in vectors),
            'max_a2': max(v.a2 for v in vectors)
        }

class FuzzyConverter:
    """
    Turli formatlar o'rtasida konvertatsiya qilish
    """
    
    @staticmethod
    def to_crisp(vector: FuzzyTriangular, method: str = 'centroid') -> float:
        """
        Fuzzy sondan aniq songa o'tkazish
        
        Parameters:
        -----------
        vector : FuzzyTriangular
            Fuzzy son
        method : str
            Konvertatsiya usuli: 'centroid', 'mean_max', 'first_max'
        """
        if method == 'centroid':
            # Markaziy nuqta usuli
            return vector.a
        elif method == 'mean_max':
            # Maksimumlar o'rtachasi
            return (vector.a + (vector.a - vector.a1) + (vector.a + vector.a2)) / 3
        elif method == 'first_max':
            # Birinchi maksimum
            return vector.a
        else:
            raise ValueError(f"Noto'g'ri konvertatsiya usuli: {method}")
    
    @staticmethod
    def from_crisp(value: float, uncertainty: float = 0.1) -> FuzzyTriangular:
        """
        Aniq sondan fuzzy songa o'tkazish
        
        Parameters:
        -----------
        value : float
            Aniq qiymat
        uncertainty : float
            Noaniqlik darajasi
        """
        return FuzzyTriangular(value, uncertainty, uncertainty)
    
    @staticmethod
    def to_interval(vector: FuzzyTriangular, 
                   confidence: float = 0.5) -> Tuple[float, float]:
        """
        Fuzzy sondan ishonch oralig'iga o'tkazish
        
        Parameters:
        -----------
        vector : FuzzyTriangular
            Fuzzy son
        confidence : float
            Ishonch darajasi [0, 1]
        """
        from .alphacut import AlphaCutOperations
        return AlphaCutOperations.alpha_cut(vector, confidence)
    