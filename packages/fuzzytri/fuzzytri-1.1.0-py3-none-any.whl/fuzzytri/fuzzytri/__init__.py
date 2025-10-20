"""
FuzzyTri - Noravshan mantiq nazariyasi va amaliyoti uchun Python kutubxonasi

Bu kutubxona Noravshan mantiqidagi vektor operatsiyalarini amalga oshirish
uchun mo'ljallangan. Uch o'lchovli fuzzy sonlar bilan ishlash imkoniyatini beradi.
"""

__version__ = "1.0.0"
__author__ = "FuzzyTri Team"
__email__ = "fuzzytri@example.com"

from .core import FuzzyTriangular
from .operations import FuzzyOperations
from .alphacut import AlphaCutOperations
from .utils import FuzzyUtils, FuzzyConverter
from .exceptions import (
    FuzzyTriError,
    VectorOperationError,
    DivisionByZeroError,
    InvalidVectorError,
    AlphaCutError,
    InvalidOperationError
)

__all__ = [
    # Asosiy klasslar
    'FuzzyTriangular',
    
    # Operatsiya klasslari
    'FuzzyOperations',
    'AlphaCutOperations',
    
    # Yordamchi klasslar
    'FuzzyUtils',
    'FuzzyConverter',
    
    # Istisnolar
    'FuzzyTriError',
    'VectorOperationError',
    'DivisionByZeroError',
    'InvalidVectorError',
    'AlphaCutError',
    'InvalidOperationError',
]
