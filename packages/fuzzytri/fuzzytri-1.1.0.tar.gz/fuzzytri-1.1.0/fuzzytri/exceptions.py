"""
Noravshan mantiq kutubxonasi uchun maxsus istisnolar
"""

class FuzzyTriError(Exception):
    """Asosiy FuzzyTri istisno klassi"""
    pass

class VectorOperationError(FuzzyTriError):
    """Vektor operatsiyalari uchun istisno"""
    pass

class DivisionByZeroError(VectorOperationError):
    """Nolga bo'lish istisnosi"""
    def __init__(self, message="Nolga bo'lish mumkin emas"):
        super().__init__(message)

class InvalidVectorError(FuzzyTriError):
    """Noto'g'ri vektor uchun istisno"""
    pass

class AlphaCutError(FuzzyTriError):
    """Alpha-kesim operatsiyalari uchun istisno"""
    pass

class InvalidOperationError(FuzzyTriError):
    """Noto'g'ri operatsiya uchun istisno"""
    pass