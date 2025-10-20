"""
FuzzyTri core klasslari uchun testlar
"""

import pytest
import math
from fuzzytri.core import FuzzyTriangular
from fuzzytri.exceptions import InvalidVectorError

class TestFuzzyTriangular:
    """FuzzyTriangular klassini test qilish"""
    
    def test_initialization(self):
        """Vektor yaratish testi"""
        v = FuzzyTriangular(2.0, 1.5, 3.0)
        assert v.a == 2.0
        assert v.a1 == 1.5
        assert v.a2 == 3.0
    
    def test_invalid_initialization(self):
        """Noto'g'ri vektor yaratish testi"""
        with pytest.raises(InvalidVectorError):
            FuzzyTriangular("invalid", 1.0, 2.0)
    
    def test_components_property(self):
        """Komponentlar property testi"""
        v = FuzzyTriangular(3.0, 2.0, 1.0)
        assert v.components == (3.0, 2.0, 1.0)
    
    def test_is_positive(self):
        """Musbat vektor testi"""
        v_positive = FuzzyTriangular(5.0, 1.0, 2.0)
        v_negative = FuzzyTriangular(-5.0, 1.0, 2.0)
        v_zero = FuzzyTriangular(0.0, 1.0, 2.0)
        
        assert v_positive.is_positive == True
        assert v_negative.is_positive == False
        assert v_zero.is_positive == False
    
    def test_is_negative(self):
        """Manfiy vektor testi"""
        v_positive = FuzzyTriangular(5.0, 1.0, 2.0)
        v_negative = FuzzyTriangular(-5.0, 1.0, 2.0)
        v_zero = FuzzyTriangular(0.0, 1.0, 2.0)
        
        assert v_positive.is_negative == False
        assert v_negative.is_negative == True
        assert v_zero.is_negative == False
    
    def test_is_zero(self):
        """Nol vektor testi"""
        v_zero = FuzzyTriangular(0.0, 1.0, 2.0)
        v_non_zero = FuzzyTriangular(1.0, 1.0, 2.0)
        
        assert v_zero.is_zero == True
        assert v_non_zero.is_zero == False
    
    def test_equality(self):
        """Vektorlar tengligi testi"""
        v1 = FuzzyTriangular(2.0, 1.0, 3.0)
        v2 = FuzzyTriangular(2.0, 1.0, 3.0)
        v3 = FuzzyTriangular(2.0, 1.5, 3.0)
        
        assert v1 == v2
        assert v1 != v3
        assert v1 != "not_a_vector"
    
    def test_copy(self):
        """Vektor nusxalash testi"""
        v1 = FuzzyTriangular(3.0, 2.0, 1.0)
        v2 = v1.copy()
        
        assert v1 == v2
        assert v1 is not v2
    
    def test_to_dict(self):
        """Dictionary konvertatsiyasi testi"""
        v = FuzzyTriangular(2.0, 1.5, 3.0)
        expected = {'a': 2.0, 'a1': 1.5, 'a2': 3.0}
        assert v.to_dict() == expected
    
    def test_from_dict(self):
        """Dictionary'dan vektor yaratish testi"""
        data = {'a': 2.0, 'a1': 1.5, 'a2': 3.0}
        v = FuzzyTriangular.from_dict(data)
        assert v.a == 2.0
        assert v.a1 == 1.5
        assert v.a2 == 3.0
    
    def test_magnitude(self):
        """Vektor magnitudasi testi"""
        v = FuzzyTriangular(3.0, 4.0, 0.0)
        expected = math.sqrt(3.0**2 + 4.0**2 + 0.0**2)
        assert v.magnitude() == expected
    
    def test_normalize(self):
        """Vektor normalizatsiyasi testi"""
        v = FuzzyTriangular(3.0, 4.0, 0.0)
        normalized = v.normalize()
        
        mag = v.magnitude()
        expected_a = 3.0 / mag
        expected_a1 = 4.0 / mag
        expected_a2 = 0.0
        
        assert math.isclose(normalized.a, expected_a)
        assert math.isclose(normalized.a1, expected_a1)
        assert math.isclose(normalized.a2, expected_a2)
    
    def test_normalize_zero_vector(self):
        """Nol vektor normalizatsiyasi testi"""
        v = FuzzyTriangular(0.0, 0.0, 0.0)
        normalized = v.normalize()
        assert normalized == v
    
    def test_is_similar(self):
        """Vektorlar o'xshashligi testi"""
        v1 = FuzzyTriangular(2.0, 1.0, 3.0)
        v2 = FuzzyTriangular(2.000001, 1.000001, 3.000001)
        v3 = FuzzyTriangular(2.1, 1.1, 3.1)
        
        assert v1.is_similar(v2, tolerance=1e-5) == True
        assert v1.is_similar(v3, tolerance=1e-5) == False
    
    def test_repr_and_str(self):
        """String ko'rinishlari testi"""
        v = FuzzyTriangular(2.0, 1.5, 3.0)
        
        repr_str = repr(v)
        str_str = str(v)
        
        assert "FuzzyTriangular" in repr_str
        assert "(2.0, 1.5, 3.0)" in str_str
        