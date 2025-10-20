"""
FuzzyTri operatsiyalari uchun testlar
"""

import pytest
from fuzzytri.core import FuzzyTriangular
from fuzzytri.operations import FuzzyOperations
from fuzzytri.exceptions import DivisionByZeroError

class TestFuzzyOperations:
    """FuzzyOperations klassini test qilish"""
    
    def setup_method(self):
        """Test uchun vektorlarni yaratish"""
        # Musbat vektorlar
        self.v1_positive = FuzzyTriangular(3.0, 2.0, 1.0)  # a > 0
        self.v2_positive = FuzzyTriangular(2.0, 1.0, 3.0)  # b > 0
        
        # Manfiy vektorlar
        self.v1_negative = FuzzyTriangular(-3.0, 2.0, 1.0)  # a < 0
        self.v2_negative = FuzzyTriangular(-2.0, 1.0, 3.0)  # b < 0
        
        # Nol vektor
        self.zero_vector = FuzzyTriangular(0.0, 0.0, 0.0)
    
    def test_addition(self):
        """Qo'shish operatsiyasi testi"""
        result = FuzzyOperations.add(self.v1_positive, self.v2_positive)
        expected = FuzzyTriangular(5.0, 3.0, 4.0)
        assert result == expected
    
    def test_subtraction(self):
        """Ayirish operatsiyasi testi"""
        result = FuzzyOperations.subtract(self.v1_positive, self.v2_positive)
        expected = FuzzyTriangular(1.0, 1.0, -2.0)
        assert result == expected
    
    def test_multiplication_positive_positive(self):
        """Ko'paytirish: a > 0, b > 0"""
        result = FuzzyOperations.multiply(self.v1_positive, self.v2_positive)
        
        # Formula: (ab, a·b₁ + b·a₁, a·b₂ + b·a₂)
        expected_a = 3.0 * 2.0  # 6.0
        expected_a1 = 3.0 * 1.0 + 2.0 * 2.0  # 3.0 + 4.0 = 7.0
        expected_a2 = 3.0 * 3.0 + 2.0 * 1.0  # 9.0 + 2.0 = 11.0
        
        expected = FuzzyTriangular(expected_a, expected_a1, expected_a2)
        assert result == expected
    
    def test_multiplication_positive_negative(self):
        """Ko'paytirish: a > 0, b < 0"""
        result = FuzzyOperations.multiply(self.v1_positive, self.v2_negative)
        
        # Formula: (ab, a·b₁ - b·a₁, a·b₂ - b·a₂)
        expected_a = 3.0 * -2.0  # -6.0
        expected_a1 = 3.0 * 1.0 - (-2.0) * 2.0  # 3.0 + 4.0 = 7.0
        expected_a2 = 3.0 * 3.0 - (-2.0) * 1.0  # 9.0 + 2.0 = 11.0
        
        expected = FuzzyTriangular(expected_a, expected_a1, expected_a2)
        assert result == expected
    
    def test_multiplication_negative_positive(self):
        """Ko'paytirish: a < 0, b > 0"""
        result = FuzzyOperations.multiply(self.v1_negative, self.v2_positive)
        
        # Formula: (ab, -a·b₁ + b·a₁, -a·b₂ + b·a₂)
        expected_a = -3.0 * 2.0  # -6.0
        expected_a1 = -(-3.0) * 1.0 + 2.0 * 2.0  # 3.0 + 4.0 = 7.0
        expected_a2 = -(-3.0) * 3.0 + 2.0 * 1.0  # 9.0 + 2.0 = 11.0
        
        expected = FuzzyTriangular(expected_a, expected_a1, expected_a2)
        assert result == expected
    
    def test_multiplication_negative_negative(self):
        """Ko'paytirish: a < 0, b < 0"""
        result = FuzzyOperations.multiply(self.v1_negative, self.v2_negative)
        
        # Formula: (ab, -a·b₁ - b·a₁, -a·b₂ - b·a₂)
        expected_a = -3.0 * -2.0  # 6.0
        expected_a1 = -(-3.0) * 1.0 - (-2.0) * 2.0  # 3.0 + 4.0 = 7.0
        expected_a2 = -(-3.0) * 3.0 - (-2.0) * 1.0  # 9.0 + 2.0 = 11.0
        
        expected = FuzzyTriangular(expected_a, expected_a1, expected_a2)
        assert result == expected
    
    def test_division_positive_positive(self):
        """Bo'lish: a > 0, b > 0"""
        result = FuzzyOperations.divide(self.v1_positive, self.v2_positive)
        
        # Formula: (a/b, (a·b₁ - b·a₁)/b², (a·b₂ - b·a₂)/b²)
        expected_a = 3.0 / 2.0  # 1.5
        b_squared = 2.0 ** 2
        expected_a1 = (3.0 * 1.0 - 2.0 * 2.0) / b_squared  # (3-4)/4 = -0.25
        expected_a2 = (3.0 * 3.0 - 2.0 * 1.0) / b_squared  # (9-2)/4 = 1.75
        
        expected = FuzzyTriangular(expected_a, expected_a1, expected_a2)
        assert result == expected
    
    def test_division_positive_negative(self):
        """Bo'lish: a > 0, b < 0"""
        result = FuzzyOperations.divide(self.v1_positive, self.v2_negative)
        
        # Formula: (a/b, (a·b₁ + b·a₁)/b², (a·b₂ + b·a₂)/b²)
        expected_a = 3.0 / -2.0  # -1.5
        b_squared = (-2.0) ** 2
        expected_a1 = (3.0 * 1.0 + (-2.0) * 2.0) / b_squared  # (3-4)/4 = -0.25
        expected_a2 = (3.0 * 3.0 + (-2.0) * 1.0) / b_squared  # (9-2)/4 = 1.75
        
        expected = FuzzyTriangular(expected_a, expected_a1, expected_a2)
        assert result == expected
    
    def test_division_by_zero(self):
        """Nolga bo'lish xatosi testi"""
        with pytest.raises(DivisionByZeroError):
            FuzzyOperations.divide(self.v1_positive, self.zero_vector)
    
    def test_dot_product(self):
        """Nuqtali ko'paytma testi"""
        result = FuzzyOperations.dot_product(self.v1_positive, self.v2_positive)
        expected = 3.0*2.0 + 2.0*1.0 + 1.0*3.0  # 6 + 2 + 3 = 11
        assert result == expected
    
    def test_scalar_multiply(self):
        """Skalyar ko'paytma testi"""
        scalar = 2.0
        result = FuzzyOperations.scalar_multiply(scalar, self.v1_positive)
        expected = FuzzyTriangular(6.0, 4.0, 2.0)
        assert result == expected
    
    def test_scalar_divide(self):
        """Skalyarga bo'lish testi"""
        scalar = 2.0
        result = FuzzyOperations.scalar_divide(self.v1_positive, scalar)
        expected = FuzzyTriangular(1.5, 1.0, 0.5)
        assert result == expected
    
    def test_scalar_divide_by_zero(self):
        """Skalyar nolga bo'lish xatosi"""
        with pytest.raises(DivisionByZeroError):
            FuzzyOperations.scalar_divide(self.v1_positive, 0.0)
    
    def test_weighted_average(self):
        """Og'irlikli o'rtacha testi"""
        vectors = [
            FuzzyTriangular(1.0, 0.5, 0.5),
            FuzzyTriangular(2.0, 1.0, 1.0),
            FuzzyTriangular(3.0, 1.5, 1.5)
        ]
        weights = [1.0, 2.0, 1.0]
        
        result = FuzzyOperations.weighted_average(vectors, weights)
        
        total_weight = 4.0
        expected_a = (1.0*1.0 + 2.0*2.0 + 3.0*1.0) / total_weight  # 8/4 = 2.0
        expected_a1 = (0.5*1.0 + 1.0*2.0 + 1.5*1.0) / total_weight  # 4/4 = 1.0
        expected_a2 = (0.5*1.0 + 1.0*2.0 + 1.5*1.0) / total_weight  # 4/4 = 1.0
        
        expected = FuzzyTriangular(expected_a, expected_a1, expected_a2)
        assert result == expected

class TestOperatorOverloading:
    """Operator overloading testlari"""
    
    def test_add_operator(self):
        """+ operatori testi"""
        v1 = FuzzyTriangular(2.0, 1.0, 3.0)
        v2 = FuzzyTriangular(1.0, 2.0, 1.0)
        
        result = v1 + v2
        expected = FuzzyTriangular(3.0, 3.0, 4.0)
        assert result == expected
    
    def test_subtract_operator(self):
        """- operatori testi"""
        v1 = FuzzyTriangular(2.0, 1.0, 3.0)
        v2 = FuzzyTriangular(1.0, 2.0, 1.0)
        
        result = v1 - v2
        expected = FuzzyTriangular(1.0, -1.0, 2.0)
        assert result == expected
    
    def test_multiply_operator(self):
        """* operatori testi"""
        v1 = FuzzyTriangular(2.0, 1.0, 3.0)
        v2 = FuzzyTriangular(3.0, 2.0, 1.0)
        
        result = v1 * v2
        expected = FuzzyOperations.multiply(v1, v2)
        assert result == expected
    
    def test_divide_operator(self):
        """/ operatori testi"""
        v1 = FuzzyTriangular(2.0, 1.0, 3.0)
        v2 = FuzzyTriangular(3.0, 2.0, 1.0)
        
        result = v1 / v2
        expected = FuzzyOperations.divide(v1, v2)
        assert result == expected
    
    def test_scalar_multiplication(self):
        """Skalyar ko'paytma operatori testi"""
        v = FuzzyTriangular(2.0, 1.0, 3.0)
        scalar = 3.0
        
        result = v * scalar
        expected = FuzzyTriangular(6.0, 3.0, 9.0)
        assert result == expected
        
        result2 = scalar * v
        assert result2 == expected
        