"""
FuzzyTri kutubxonasining asosiy foydalanish misollari
"""

from fuzzytri import FuzzyTriangular, FuzzyOperations, FuzzyUtils

def basic_operations_example():
    """Asosiy operatsiyalar misoli"""
    print("=== ASOSIY OPERATSIYALAR MISOLI ===\n")
    
    # Vektorlar yaratish
    v1 = FuzzyTriangular(3.0, 2.0, 1.0)
    v2 = FuzzyTriangular(2.0, 1.0, 3.0)
    
    print(f"v1 = {v1}")
    print(f"v2 = {v2}\n")
    
    # Qo'shish
    addition = v1 + v2
    print(f"v1 + v2 = {addition}")
    
    # Ayirish
    subtraction = v1 - v2
    print(f"v1 - v2 = {subtraction}")
    
    # Ko'paytirish
    multiplication = v1 * v2
    print(f"v1 * v2 = {multiplication}")
    
    # Bo'lish
    division = v1 / v2
    print(f"v1 / v2 = {division}")
    
    # Nuqtali ko'paytma
    dot_product = FuzzyOperations.dot_product(v1, v2)
    print(f"v1 · v2 = {dot_product}")

def different_sign_cases_example():
    """Turli ishora kombinatsiyalari misoli"""
    print("\n=== TURLI ISHORA KOMBINATSIYALARI ===\n")
    
    # Turli ishoralarga ega vektorlar
    positive = FuzzyTriangular(4.0, 1.0, 2.0)   # a > 0
    negative = FuzzyTriangular(-3.0, 2.0, 1.0)  # a < 0
    zero = FuzzyTriangular(0.0, 1.0, 1.0)       # a = 0
    
    print("Musbat * Musbat:")
    result1 = positive * positive
    print(f"({positive}) * ({positive}) = {result1}")
    
    print("\nMusbat * Manfiy:")
    result2 = positive * negative
    print(f"({positive}) * ({negative}) = {result2}")
    
    print("\nManfiy * Manfiy:")
    result3 = negative * negative
    print(f"({negative}) * ({negative}) = {result3}")
    
    print("\nNol bilan ko'paytirish:")
    result4 = positive * zero
    print(f"({positive}) * ({zero}) = {result4}")

def utility_functions_example():
    """Yordamchi funksiyalar misoli"""
    print("\n=== YORDAMCHI FUNKSIYALAR ===\n")
    
    # Vektor yaratish
    v1 = FuzzyTriangular(2.0, 1.0, 3.0)
    v2 = FuzzyTriangular(4.0, 2.0, 1.0)
    
    print(f"v1 = {v1}")
    print(f"v2 = {v2}\n")
    
    # Masofa hisoblash
    euclidean_dist = FuzzyUtils.distance(v1, v2, 'euclidean')
    manhattan_dist = FuzzyUtils.distance(v1, v2, 'manhattan')
    
    print(f"Evklid masofasi: {euclidean_dist:.4f}")
    print(f"Manxetten masofasi: {manhattan_dist:.4f}")
    
    # O'xshashlik
    similarity = FuzzyUtils.similarity(v1, v2)
    print(f"O'xshashlik darajasi: {similarity:.4f}")
    
    # Magnituda
    magnitude_v1 = v1.magnitude()
    magnitude_v2 = v2.magnitude()
    print(f"v1 magnitudasi: {magnitude_v1:.4f}")
    print(f"v2 magnitudasi: {magnitude_v2:.4f}")
    
    # Normalizatsiya
    normalized_v1 = v1.normalize()
    print(f"v1 normalizatsiyasi: {normalized_v1}")

def batch_operations_example():
    """Ketma-ket operatsiyalar misoli"""
    print("\n=== KETMA-KET OPERATSIYALAR ===\n")
    
    # Vektorlar ro'yxati
    vectors1 = [
        FuzzyTriangular(1.0, 0.5, 0.5),
        FuzzyTriangular(2.0, 1.0, 1.0),
        FuzzyTriangular(3.0, 1.5, 1.5)
    ]
    
    vectors2 = [
        FuzzyTriangular(2.0, 1.0, 1.0),
        FuzzyTriangular(3.0, 1.5, 1.5),
        FuzzyTriangular(4.0, 2.0, 2.0)
    ]
    
    print("Vektorlar 1:")
    for i, v in enumerate(vectors1):
        print(f"  v1[{i}] = {v}")
    
    print("\nVektorlar 2:")
    for i, v in enumerate(vectors2):
        print(f"  v2[{i}] = {v}")
    
    # Ketma-ket qo'shish
    addition_results = FuzzyUtils.batch_operations(vectors1, vectors2, 'add')
    print("\nQo'shish natijalari:")
    for i, result in enumerate(addition_results):
        print(f"  v1[{i}] + v2[{i}] = {result}")
    
    # Ketma-ket ko'paytirish
    multiplication_results = FuzzyUtils.batch_operations(vectors1, vectors2, 'multiply')
    print("\nKo'paytirish natijalari:")
    for i, result in enumerate(multiplication_results):
        print(f"  v1[{i}] * v2[{i}] = {result}")

if __name__ == "__main__":
    basic_operations_example()
    different_sign_cases_example()
    utility_functions_example()
    batch_operations_example()
    