"""
Alpha-kesim operatsiyalari uchun testlar
"""

import pytest
from fuzzytri.core import FuzzyTriangular
from fuzzytri.alphacut import AlphaCutOperations
from fuzzytri.exceptions import AlphaCutError

class TestAlphaCutOperations:
    """AlphaCutOperations klassini test qilish"""
    
    def setup_method(self):
        """Test uchun vektor yaratish"""
        self.vector = FuzzyTriangular(5.0, 2.0, 3.0)  # a=5, a1=2, a2=3
    
    def test_alpha_cut_basic(self):
        """Asosiy alpha-kesim testi"""
        alpha = 0.5
        lower, upper = AlphaCutOperations.alpha_cut(self.vector, alpha)
        
        # Formula: lower = a - (1-alpha)*a1, upper = a + (1-alpha)*a2
        expected_lower = 5.0 - (1-0.5)*2.0  # 5 - 0.5*2 = 4.0
        expected_upper = 5.0 + (1-0.5)*3.0  # 5 + 0.5*3 = 6.5
        
        assert lower == expected_lower
        assert upper == expected_upper
    
    def test_alpha_cut_zero(self):
        """Alpha=0 testi (qo'llab-quvvatlovchi)"""
        alpha = 0.0
        lower, upper = AlphaCutOperations.alpha_cut(self.vector, alpha)
        
        expected_lower = 5.0 - (1-0.0)*2.0  # 5 - 2 = 3.0
        expected_upper = 5.0 + (1-0.0)*3.0  # 5 + 3 = 8.0
        
        assert lower == expected_lower
        assert upper == expected_upper
    
    def test_alpha_cut_one(self):
        """Alpha=1 testi (yadro)"""
        alpha = 1.0
        lower, upper = AlphaCutOperations.alpha_cut(self.vector, alpha)
        
        expected_lower = 5.0 - (1-1.0)*2.0  # 5 - 0 = 5.0
        expected_upper = 5.0 + (1-1.0)*3.0  # 5 + 0 = 5.0
        
        assert lower == expected_lower
        assert upper == expected_upper
    
    def test_alpha_cut_invalid_alpha(self):
        """Noto'g'ri alpha qiymati testi"""
        with pytest.raises(AlphaCutError):
            AlphaCutOperations.alpha_cut(self.vector, -0.5)
        
        with pytest.raises(AlphaCutError):
            AlphaCutOperations.alpha_cut(self.vector, 1.5)
    
    def test_alpha_level_set(self):
        """Alpha darajalar to'plami testi"""
        alpha_levels = [0.0, 0.5, 1.0]
        results = AlphaCutOperations.alpha_level_set(self.vector, alpha_levels)
        
        assert len(results) == 3
        
        # Alpha=0.0
        assert results[0] == (3.0, 8.0)
        # Alpha=0.5
        assert results[1] == (4.0, 6.5)
        # Alpha=1.0
        assert results[2] == (5.0, 5.0)
    
    def test_from_alpha_cuts(self):
        """Alpha-kesimlardan vektor tiklash testi"""
        alpha_cuts = [(3.0, 8.0), (4.0, 6.5), (5.0, 5.0)]
        alpha_levels = [0.0, 0.5, 1.0]
        
        result = AlphaCutOperations.from_alpha_cuts(alpha_cuts, alpha_levels)
        
        # Asosiy parametrlarni hisoblash
        expected_a = (5.0 + 5.0) / 2  # 5.0
        expected_a1 = 5.0 - 3.0  # 2.0
        expected_a2 = 8.0 - 5.0  # 3.0
        
        expected = FuzzyTriangular(expected_a, expected_a1, expected_a2)
        assert result == expected
    
    def test_from_alpha_cuts_invalid(self):
        """Noto'g'ri alpha-kesimlar testi"""
        with pytest.raises(AlphaCutError):
            AlphaCutOperations.from_alpha_cuts([(1,2)], [0.0])
        
        with pytest.raises(AlphaCutError):
            AlphaCutOperations.from_alpha_cuts([(1,2), (3,4)], [0.0])
    
    def test_membership_function(self):
        """A'zolik funksiyasi testi"""
        vector = FuzzyTriangular(5.0, 2.0, 3.0)
        
        # Markazda
        assert AlphaCutOperations.membership_function(vector, 5.0) == 1.0
        
        # Chap tomonda
        assert AlphaCutOperations.membership_function(vector, 4.0) == 0.5
        assert AlphaCutOperations.membership_function(vector, 3.0) == 0.0
        assert AlphaCutOperations.membership_function(vector, 2.0) == 0.0
        
        # O'ng tomonda
        assert AlphaCutOperations.membership_function(vector, 6.0) == 2/3  # 1 - (6-5)/3
        assert AlphaCutOperations.membership_function(vector, 8.0) == 0.0
        assert AlphaCutOperations.membership_function(vector, 9.0) == 0.0
    
    def test_support(self):
        """Qo'llab-quvvatlovchi testi"""
        support = AlphaCutOperations.support(self.vector)
        expected = (3.0, 8.0)  # a-a1=3, a+a2=8
        assert support == expected
    
    def test_core(self):
        """Yadro testi"""
        core = AlphaCutOperations.core(self.vector)
        expected = (5.0, 5.0)  # a=5
        assert core == expected
    
    def test_height(self):
        """Balandlik testi"""
        height = AlphaCutOperations.height(self.vector)
        assert height == 1.0
    
    def test_is_normal(self):
        """Normal fuzzy son testi"""
        normal_vector = FuzzyTriangular(5.0, 2.0, 3.0)
        assert AlphaCutOperations.is_normal(normal_vector) == True

class TestEdgeCases:
    """Chegara holatlari testlari"""
    
    def test_zero_spread_vector(self):
        """Diffuzligi nol bo'lgan vektor"""
        vector = FuzzyTriangular(5.0, 0.0, 0.0)
        
        # Alpha-kesim
        lower, upper = AlphaCutOperations.alpha_cut(vector, 0.5)
        assert lower == 5.0
        assert upper == 5.0
        
        # A'zolik funksiyasi
        assert AlphaCutOperations.membership_function(vector, 5.0) == 1.0
        assert AlphaCutOperations.membership_function(vector, 4.0) == 0.0
        assert AlphaCutOperations.membership_function(vector, 6.0) == 0.0
    
    def test_negative_vector_alpha_cut(self):
        """Manfiy vektor uchun alpha-kesim"""
        vector = FuzzyTriangular(-5.0, 2.0, 3.0)
        
        lower, upper = AlphaCutOperations.alpha_cut(vector, 0.5)
        expected_lower = -5.0 - (1-0.5)*2.0  # -5 - 1 = -6.0
        expected_upper = -5.0 + (1-0.5)*3.0  # -5 + 1.5 = -3.5
        
        assert lower == expected_lower
        assert upper == expected_upper
        