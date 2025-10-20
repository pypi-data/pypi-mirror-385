"""
Yordamchi funksiyalar uchun testlar
"""

import pytest
import math
import json
from fuzzytri.core import FuzzyTriangular
from fuzzytri.utils import FuzzyUtils, FuzzyConverter
from fuzzytri.alphacut import AlphaCutOperations

class TestFuzzyUtils:
    """FuzzyUtils klassini test qilish"""
    
    def setup_method(self):
        """Test uchun vektorlar yaratish"""
        self.vector1 = FuzzyTriangular(2.0, 1.0, 3.0)
        self.vector2 = FuzzyTriangular(4.0, 2.0, 1.0)
        self.vectors = [
            FuzzyTriangular(1.0, 0.5, 0.5),
            FuzzyTriangular(2.0, 1.0, 1.0),
            FuzzyTriangular(3.0, 1.5, 1.5)
        ]
    
    def test_create_zero_vector(self):
        """Nol vektor yaratish testi"""
        zero = FuzzyUtils.create_zero_vector()
        assert zero == FuzzyTriangular(0.0, 0.0, 0.0)
    
    def test_create_unit_vector(self):
        """Birlik vektor yaratish testi"""
        unit = FuzzyUtils.create_unit_vector()
        assert unit == FuzzyTriangular(1.0, 0.0, 0.0)
    
    def test_create_symmetric(self):
        """Simmetrik vektor yaratish testi"""
        symmetric = FuzzyUtils.create_symmetric(5.0, 2.0)
        expected = FuzzyTriangular(5.0, 2.0, 2.0)
        assert symmetric == expected
    
    def test_distance_euclidean(self):
        """Evklid masofasi testi"""
        dist = FuzzyUtils.distance(self.vector1, self.vector2, 'euclidean')
        expected = math.sqrt((2-4)**2 + (1-2)**2 + (3-1)**2)  # √(4+1+4)=√9=3
        assert dist == expected
    
    def test_distance_manhattan(self):
        """Manxetten masofasi testi"""
        dist = FuzzyUtils.distance(self.vector1, self.vector2, 'manhattan')
        expected = abs(2-4) + abs(1-2) + abs(3-1)  # 2+1+2=5
        assert dist == expected
    
    def test_distance_chebyshev(self):
        """Chebyshev masofasi testi"""
        dist = FuzzyUtils.distance(self.vector1, self.vector2, 'chebyshev')
        expected = max(abs(2-4), abs(1-2), abs(3-1))  # max(2,1,2)=2
        assert dist == expected
    
    def test_distance_invalid_metric(self):
        """Noto'g'ri metrika testi"""
        with pytest.raises(ValueError):
            FuzzyUtils.distance(self.vector1, self.vector2, 'invalid')
    
    def test_similarity(self):
        """O'xshashlik testi"""
        similar_vector = FuzzyTriangular(2.01, 1.01, 3.01)
        different_vector = FuzzyTriangular(10.0, 5.0, 8.0)
        
        sim1 = FuzzyUtils.similarity(self.vector1, similar_vector)
        sim2 = FuzzyUtils.similarity(self.vector1, different_vector)
        
        assert 0 <= sim1 <= 1
        assert 0 <= sim2 <= 1
        assert sim1 > sim2  # O'xshash vektorlar ko'proq o'xshash
    
    def test_to_json(self):
        """JSON konvertatsiyasi testi"""
        json_str = FuzzyUtils.to_json(self.vector1)
        data = json.loads(json_str)
        
        expected = {'a': 2.0, 'a1': 1.0, 'a2': 3.0}
        assert data == expected
    
    def test_from_json(self):
        """JSON'dan vektor yaratish testi"""
        json_str = '{"a": 2.0, "a1": 1.0, "a2": 3.0}'
        vector = FuzzyUtils.from_json(json_str)
        
        assert vector == self.vector1
    
    def test_batch_operations(self):
        """Ketma-ket operatsiyalar testi"""
        vectors1 = [FuzzyTriangular(1,1,1), FuzzyTriangular(2,2,2)]
        vectors2 = [FuzzyTriangular(3,3,3), FuzzyTriangular(4,4,4)]
        
        # Qo'shish
        results = FuzzyUtils.batch_operations(vectors1, vectors2, 'add')
        expected = [FuzzyTriangular(4,4,4), FuzzyTriangular(6,6,6)]
        assert results == expected
        
        # Ko'paytirish
        results = FuzzyUtils.batch_operations(vectors1, vectors2, 'multiply')
        assert len(results) == 2
    
    def test_batch_operations_invalid(self):
        """Noto'g'ri ketma-ket operatsiyalar testi"""
        vectors1 = [FuzzyTriangular(1,1,1)]
        vectors2 = [FuzzyTriangular(2,2,2), FuzzyTriangular(3,3,3)]  # Turli uzunlik
        
        with pytest.raises(ValueError):
            FuzzyUtils.batch_operations(vectors1, vectors2, 'add')
        
        with pytest.raises(ValueError):
            FuzzyUtils.batch_operations(vectors1, vectors1, 'invalid_operation')
    
    def test_statistical_analysis(self):
        """Statistik tahlil testi"""
        stats = FuzzyUtils.statistical_analysis(self.vectors)
        
        assert stats['count'] == 3
        assert isinstance(stats['mean'], FuzzyTriangular)
        assert isinstance(stats['variance'], FuzzyTriangular)
        assert isinstance(stats['std_deviation'], FuzzyTriangular)
        
        # O'rtacha tekshirish
        expected_mean_a = (1.0 + 2.0 + 3.0) / 3  # 2.0
        expected_mean_a1 = (0.5 + 1.0 + 1.5) / 3  # 1.0
        expected_mean_a2 = (0.5 + 1.0 + 1.5) / 3  # 1.0
        
        assert stats['mean'].a == expected_mean_a
        assert stats['mean'].a1 == expected_mean_a1
        assert stats['mean'].a2 == expected_mean_a2

class TestFuzzyConverter:
    """FuzzyConverter klassini test qilish"""
    
    def test_to_crisp_centroid(self):
        """Markaziy nuqta usuli testi"""
        vector = FuzzyTriangular(5.0, 2.0, 3.0)
        crisp = FuzzyConverter.to_crisp(vector, 'centroid')
        assert crisp == 5.0
    
    def test_to_crisp_mean_max(self):
        """Maksimumlar o'rtachasi usuli testi"""
        vector = FuzzyTriangular(5.0, 2.0, 3.0)
        crisp = FuzzyConverter.to_crisp(vector, 'mean_max')
        
        expected = (5.0 + (5.0-2.0) + (5.0+3.0)) / 3  # (5+3+8)/3 ≈ 5.333
        assert math.isclose(crisp, expected, rel_tol=1e-6)
    
    def test_to_crisp_first_max(self):
        """Birinchi maksimum usuli testi"""
        vector = FuzzyTriangular(5.0, 2.0, 3.0)
        crisp = FuzzyConverter.to_crisp(vector, 'first_max')
        assert crisp == 5.0
    
    def test_to_crisp_invalid_method(self):
        """Noto'g'ri konvertatsiya usuli testi"""
        vector = FuzzyTriangular(5.0, 2.0, 3.0)
        with pytest.raises(ValueError):
            FuzzyConverter.to_crisp(vector, 'invalid_method')
    
    def test_from_crisp(self):
        """Aniq sondan fuzzy songa o'tkazish testi"""
        crisp_value = 10.0
        uncertainty = 2.0
        fuzzy = FuzzyConverter.from_crisp(crisp_value, uncertainty)
        
        expected = FuzzyTriangular(10.0, 2.0, 2.0)
        assert fuzzy == expected
    
    def test_to_interval(self):
        """Ishonch oralig'iga o'tkazish testi"""
        vector = FuzzyTriangular(5.0, 2.0, 3.0)
        confidence = 0.5
        
        interval = FuzzyConverter.to_interval(vector, confidence)
        expected = AlphaCutOperations.alpha_cut(vector, confidence)
        
        assert interval == expected
        