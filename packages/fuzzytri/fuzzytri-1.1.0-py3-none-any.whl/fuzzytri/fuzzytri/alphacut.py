"""
Alpha-kesim operatsiyalari va xususiyatlari
"""

from typing import Tuple, List, Optional
from .core import FuzzyTriangular
from .exceptions import AlphaCutError

class AlphaCutOperations:
    """
    Alpha-kesim asosidagi operatsiyalar
    """
    
    @staticmethod
    def alpha_cut(vector: FuzzyTriangular, alpha: float) -> Tuple[float, float]:
        """
        Alpha-kesimni hisoblash
        
        Parameters:
        -----------
        vector : FuzzyTriangular
            Fuzzy uchburchak son
        alpha : float
            Alpha qiymati [0, 1] oraliqda
        
        Returns:
        --------
        Tuple[float, float] : (pastki chegara, yuqori chegara)
        """
        if not 0 <= alpha <= 1:
            raise AlphaCutError("Alpha [0, 1] oraliqda bo'lishi kerak")
        
        # Alpha-kesim formulasi
        lower_bound = vector.a - (1 - alpha) * vector.a1
        upper_bound = vector.a + (1 - alpha) * vector.a2
        
        return (lower_bound, upper_bound)
    
    @staticmethod
    def alpha_level_set(vector: FuzzyTriangular, 
                       alpha_levels: List[float]) -> List[Tuple[float, float]]:
        """
        Alpha darajalar to'plami uchun kesimlarni hisoblash
        
        Parameters:
        -----------
        vector : FuzzyTriangular
            Fuzzy uchburchak son
        alpha_levels : List[float]
            Alpha darajalar ro'yxati
        
        Returns:
        --------
        List[Tuple[float, float]] : Har bir alpha daraja uchun kesimlar
        """
        results = []
        for alpha in alpha_levels:
            try:
                cut = AlphaCutOperations.alpha_cut(vector, alpha)
                results.append(cut)
            except AlphaCutError:
                continue
        return results
    
    @staticmethod
    def from_alpha_cuts(alpha_cuts: List[Tuple[float, float]], 
                        alpha_levels: List[float]) -> Optional[FuzzyTriangular]:
        """
        Alpha-kesimlardan fuzzy sonni qayta tiklash
        
        Parameters:
        -----------
        alpha_cuts : List[Tuple[float, float]]
            Alpha kesimlar ro'yxati
        alpha_levels : List[float]
            Alpha darajalar ro'yxati
        
        Returns:
        --------
        FuzzyTriangular : Qayta tiklangan fuzzy son
        """
        if len(alpha_cuts) != len(alpha_levels):
            raise AlphaCutError("Kesimlar va darajalar soni teng bo'lishi kerak")
        
        if len(alpha_cuts) < 2:
            raise AlphaCutError("Kamida 2 ta alpha kesim kerak")
        
        try:
            # Eng past alpha (0) uchun kesim
            min_alpha_idx = alpha_levels.index(min(alpha_levels))
            lower_cut = alpha_cuts[min_alpha_idx]
            
            # Eng yuqori alpha (1) uchun kesim
            max_alpha_idx = alpha_levels.index(max(alpha_levels))
            upper_cut = alpha_cuts[max_alpha_idx]
            
            # Asosiy parametrlarni hisoblash
            a = (lower_cut[0] + upper_cut[0]) / 2
            a1 = a - lower_cut[0]
            a2 = upper_cut[1] - a
            
            return FuzzyTriangular(a, a1, a2)
        
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def membership_function(vector: FuzzyTriangular, x: float) -> float:
        """
        A'zolik funksiyasini hisoblash
        
        Parameters:
        -----------
        vector : FuzzyTriangular
            Fuzzy uchburchak son
        x : float
            Nuqta qiymati
        
        Returns:
        --------
        float : A'zolik darajasi [0, 1]
        """
        a, a1, a2 = vector.a, vector.a1, vector.a2
        
        if x < a - a1 or x > a + a2:
            return 0.0
        elif x < a:
            return 1 - (a - x) / a1 if a1 != 0 else 1.0
        elif x > a:
            return 1 - (x - a) / a2 if a2 != 0 else 1.0
        else:
            return 1.0
    
    @staticmethod
    def support(vector: FuzzyTriangular) -> Tuple[float, float]:
        """
        Qo'llab-quvvatlovchi to'plamni hisoblash (alpha=0)
        """
        return (vector.a - vector.a1, vector.a + vector.a2)
    
    @staticmethod
    def core(vector: FuzzyTriangular) -> Tuple[float, float]:
        """
        Yadro to'plamni hisoblash (alpha=1)
        """
        return (vector.a, vector.a)
    
    @staticmethod
    def height(vector: FuzzyTriangular) -> float:
        """
        Fuzzy sonning balandligini hisoblash
        """
        return AlphaCutOperations.membership_function(vector, vector.a)
    
    @staticmethod
    def is_normal(vector: FuzzyTriangular) -> bool:
        """
        Fuzzy son normalmi? (balandlik = 1)
        """
        return AlphaCutOperations.height(vector) == 1.0
    
    @staticmethod
    def is_convex(vector: FuzzyTriangular) -> bool:
        """
        Fuzzy son konveksmi?
        """
        return vector.a1 >= 0 and vector.a2 >= 0
    
    @staticmethod
    def is_finite(vector: FuzzyTriangular) -> bool:
        """
        Fuzzy son cheklanganmi?
        """
        return (vector.a1 < float('inf')) and (vector.a2 < float('inf'))
    
    @staticmethod
    def centroid(vector: FuzzyTriangular) -> float:
        """
        Fuzzy sonning markaziy nuqtasini hisoblash
        """
        a, a1, a2 = vector.a, vector.a1, vector.a2
        return (a + (a - a1) + (a + a2)) / 3
    
    @staticmethod
    def spread(vector: FuzzyTriangular) -> float:
        """
        Fuzzy sonning tarqalishini hisoblash
        """
        return vector.a1 + vector.a2
    