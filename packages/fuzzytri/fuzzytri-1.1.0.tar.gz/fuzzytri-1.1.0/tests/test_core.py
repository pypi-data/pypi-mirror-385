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
        v = FuzzyTriangular(2.0, 1.5, 3.0)
        assert v.a == 2.0
        assert v.a1 == 1.5
        assert v.a2 == 3.0
    
    def test_invalid_initialization(self):
        with pytest.raises(InvalidVectorError):
            FuzzyTriangular(float('nan'), 1.0, 2.0)
    
    def test_components_property(self):
        v = FuzzyTriangular(3.0, 2.0, 1.0)
        assert v.components == (3.0, 2.0, 1.0)
    
    def test_is_positive(self):
        v_positive = FuzzyTriangular(5.0, 1.0, 2.0)
        v_negative = FuzzyTriangular(-5.0, 1.0, 2.0)
        v_zero = FuzzyTriangular(0.0, 1.0, 2.0)
        assert v_positive.is_positive
        assert not v_negative.is_positive
        assert not v_zero.is_positive
    
    def test_is_negative(self):
        v_positive = FuzzyTriangular(5.0, 1.0, 2.0)
        v_negative = FuzzyTriangular(-5.0, 1.0, 2.0)
        v_zero = FuzzyTriangular(0.0, 1.0, 2.0)
        assert not v_positive.is_negative
        assert v_negative.is_negative
        assert not v_zero.is_negative
    
    def test_is_zero(self):
        v_zero = FuzzyTriangular(0.0, 1.0, 2.0)
        v_non_zero = FuzzyTriangular(1.0, 1.0, 2.0)
        assert v_zero.is_zero
        assert not v_non_zero.is_zero
    
    def test_equality(self):
        v1 = FuzzyTriangular(2.0, 1.0, 3.0)
        v2 = FuzzyTriangular(2.0, 1.0, 3.0)
        v3 = FuzzyTriangular(2.0, 1.5, 3.0)
        assert v1 == v2
        assert v1 != v3
        assert v1 != "not_a_vector"
    
    def test_copy(self):
        v1 = FuzzyTriangular(3.0, 2.0, 1.0)
        v2 = v1.copy()
        assert v1 == v2
        assert v1 is not v2
    
    def test_to_dict(self):
        v = FuzzyTriangular(2.0, 1.5, 3.0)
        expected = {'a': 2.0, 'a1': 1.5, 'a2': 3.0}
        assert v.to_dict() == expected
    
    def test_from_dict(self):
        data = {'a': 2.0, 'a1': 1.5, 'a2': 3.0}
        v = FuzzyTriangular.from_dict(data)
        assert v.a == 2.0
        assert v.a1 == 1.5
        assert v.a2 == 3.0
    
    def test_magnitude(self):
        v = FuzzyTriangular(3.0, 4.0, 0.0)
        expected = math.sqrt(3.0**2 + 4.0**2 + 0.0**2)
        assert v.magnitude() == expected
    
    def test_normalize(self):
        v = FuzzyTriangular(3.0, 4.0, 0.0)
        normalized = v.normalize()
        mag = v.magnitude()
        assert math.isclose(normalized.a, 3.0 / mag)
        assert math.isclose(normalized.a1, 4.0 / mag)
        assert math.isclose(normalized.a2, 0.0 / mag)
    
    def test_normalize_zero_vector(self):
        v = FuzzyTriangular(0.0, 0.0, 0.0)
        normalized = v.normalize()
        assert normalized == v
    
    def test_is_similar(self):
        v1 = FuzzyTriangular(2.0, 1.0, 3.0)
        v2 = FuzzyTriangular(2.000001, 1.000001, 3.000001)
        v3 = FuzzyTriangular(2.1, 1.1, 3.1)
        assert v1.is_similar(v2, tolerance=1e-5)
        assert not v1.is_similar(v3, tolerance=1e-5)
    
    def test_repr_and_str(self):
        v = FuzzyTriangular(2.0, 1.5, 3.0)
        assert "FuzzyTriangular" in repr(v)
        assert "(2.0, 1.5, 3.0)" in str(v)

    def test_math_functions(self):
        """Kophad orqali exp, sin, cos metodlarini test qilish"""
        x = FuzzyTriangular(0.5, 0.0, 1.0)

        exp_x = x.exp()
        sin_x = x.sin()
        cos_x = x.cos()

        assert math.isclose(exp_x.a, math.exp(x.a), rel_tol=1e-6)
        assert math.isclose(exp_x.a1, math.exp(x.a1), rel_tol=1e-6)
        assert math.isclose(exp_x.a2, math.exp(x.a2), rel_tol=1e-6)

        assert math.isclose(sin_x.a, math.sin(x.a), rel_tol=1e-6)
        assert math.isclose(sin_x.a1, math.sin(x.a1), rel_tol=1e-6)
        assert math.isclose(sin_x.a2, math.sin(x.a2), rel_tol=1e-6)

        assert math.isclose(cos_x.a, math.cos(x.a), rel_tol=1e-6)
        assert math.isclose(cos_x.a1, math.cos(x.a1), rel_tol=1e-6)
        assert math.isclose(cos_x.a2, math.cos(x.a2), rel_tol=1e-6)
