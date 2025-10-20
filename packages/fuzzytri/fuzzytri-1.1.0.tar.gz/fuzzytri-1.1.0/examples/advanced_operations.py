"""
FuzzyTri kutubxonasining ilg'or operatsiyalari misollari
"""
from fuzzytri.utils import FuzzyUtils
from fuzzytri import FuzzyTriangular, AlphaCutOperations, FuzzyConverter

def alpha_cut_examples():
    """Alpha-kesim operatsiyalari misoli"""
    print("=== ALPHA-KESIM OPERATSIYALARI ===\n")
    
    # Fuzzy son yaratish
    fuzzy_number = FuzzyTriangular(5.0, 2.0, 3.0)
    print(f"Fuzzy son: {fuzzy_number}")
    print(f"Qo'llab-quvvatlovchi: {AlphaCutOperations.support(fuzzy_number)}")
    print(f"Yadro: {AlphaCutOperations.core(fuzzy_number)}")
    print(f"Balandlik: {AlphaCutOperations.height(fuzzy_number)}")
    print(f"Normalmi?: {AlphaCutOperations.is_normal(fuzzy_number)}\n")
    
    # Turli alpha qiymatlari uchun kesimlar
    alpha_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    print("Alpha-kesimlar:")
    for alpha in alpha_values:
        lower, upper = AlphaCutOperations.alpha_cut(fuzzy_number, alpha)
        print(f"  α={alpha}: [{lower:.2f}, {upper:.2f}]")
    
    # A'zolik funksiyasi
    print("\nA'zolik funksiyasi:")
    test_points = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    for x in test_points:
        membership = AlphaCutOperations.membership_function(fuzzy_number, x)
        print(f"  μ({x}) = {membership:.2f}")

def membership_function_analysis():
    """A'zolik funksiyasi tahlili"""
    print("\n=== A'ZOLIK FUNKSIYASI TAHLILI ===\n")
    
    # Turli xil fuzzy sonlar
    symmetric = FuzzyTriangular(5.0, 2.0, 2.0)      # Simmetrik
    left_skewed = FuzzyTriangular(5.0, 3.0, 1.0)    # Chapga og'gan
    right_skewed = FuzzyTriangular(5.0, 1.0, 3.0)   # O'ngga og'gan
    precise = FuzzyTriangular(5.0, 0.5, 0.5)        # Aniqroq
    
    fuzzy_numbers = {
        "Simmetrik": symmetric,
        "Chapga og'gan": left_skewed,
        "O'ngga og'gan": right_skewed,
        "Aniqroq": precise
    }
    
    # Har bir fuzzy son uchun a'zolik funksiyasini hisoblash
    test_points = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    
    print("A'zolik darajalari:")
    print("x\t" + "\t".join(fuzzy_numbers.keys()))
    
    for x in test_points:
        memberships = []
        for name, fuzzy_num in fuzzy_numbers.items():
            mu = AlphaCutOperations.membership_function(fuzzy_num, x)
            memberships.append(f"{mu:.2f}")
        
        print(f"{x}\t" + "\t".join(memberships))

def conversion_examples():
    """Konvertatsiya operatsiyalari misoli"""
    print("\n=== KONVERTATSIYA OPERATSIYALARI ===\n")
    
    # Fuzzy son yaratish
    fuzzy_number = FuzzyTriangular(7.0, 2.0, 3.0)
    print(f"Fuzzy son: {fuzzy_number}")
    
    # Aniq songa o'tkazish
    crisp_centroid = FuzzyConverter.to_crisp(fuzzy_number, 'centroid')
    crisp_mean_max = FuzzyConverter.to_crisp(fuzzy_number, 'mean_max')
    crisp_first_max = FuzzyConverter.to_crisp(fuzzy_number, 'first_max')
    
    print(f"Markaziy nuqta usuli: {crisp_centroid:.2f}")
    print(f"Maksimumlar o'rtachasi: {crisp_mean_max:.2f}")
    print(f"Birinchi maksimum: {crisp_first_max:.2f}")
    
    # Aniq sondan fuzzy songa o'tkazish
    crisp_value = 10.0
    fuzzy_from_crisp = FuzzyConverter.from_crisp(crisp_value, uncertainty=1.5)
    print(f"\nAniq son {crisp_value} -> Fuzzy son: {fuzzy_from_crisp}")
    
    # Ishonch oralig'iga o'tkazish
    confidence_levels = [0.0, 0.5, 0.9]
    print("\nIshonch oraliklari:")
    for confidence in confidence_levels:
        interval = FuzzyConverter.to_interval(fuzzy_number, confidence)
        print(f"  {confidence*100}% ishonch: [{interval[0]:.2f}, {interval[1]:.2f}]")

def alpha_cut_reconstruction():
    """Alpha-kesim orqali fuzzy sonni qayta tiklash"""
    print("\n=== ALPHA-KESIM ORQALI QAYTA TIKLASH ===\n")
    
    # Asl fuzzy son
    original = FuzzyTriangular(6.0, 2.0, 4.0)
    print(f"Asl fuzzy son: {original}")
    
    # Alpha-kesimlarni olish
    alpha_levels = [0.0, 0.25, 0.5, 0.75, 1.0]
    alpha_cuts = AlphaCutOperations.alpha_level_set(original, alpha_levels)
    
    print("Alpha-kesimlar:")
    for alpha, cut in zip(alpha_levels, alpha_cuts):
        print(f"  α={alpha}: {cut}")
    
    # Alpha-kesimlardan qayta tiklash
    reconstructed = AlphaCutOperations.from_alpha_cuts(alpha_cuts, alpha_levels)
    print(f"\nQayta tiklangan: {reconstructed}")
    print(f"Xato: {FuzzyUtils.distance(original, reconstructed):.6f}")

def statistical_analysis_example():
    """Statistik tahlil misoli"""
    print("\n=== STATISTIK TAHLIL ===\n")
    
    # Vektorlar to'plami
    vectors = [
        FuzzyTriangular(1.0, 0.5, 0.5),
        FuzzyTriangular(2.0, 1.0, 1.0),
        FuzzyTriangular(3.0, 1.5, 1.5),
        FuzzyTriangular(4.0, 2.0, 2.0),
        FuzzyTriangular(5.0, 2.5, 2.5)
    ]
    
    print("Vektorlar to'plami:")
    for i, v in enumerate(vectors):
        print(f"  v[{i}] = {v}")
    
    # Statistik tahlil
    stats = FuzzyUtils.statistical_analysis(vectors)
    
    print(f"\nStatistik tahlil:")
    print(f"  Soni: {stats['count']}")
    print(f"  O'rtacha: {stats['mean']}")
    print(f"  Dispersiya: {stats['variance']}")
    print(f"  Standart chetlanish: {stats['std_deviation']}")
    print(f"  a min/max: [{stats['min_a']}, {stats['max_a']}]")
    print(f"  a1 min/max: [{stats['min_a1']}, {stats['max_a1']}]")
    print(f"  a2 min/max: [{stats['min_a2']}, {stats['max_a2']}]")

if __name__ == "__main__":
    alpha_cut_examples()
    membership_function_analysis()
    conversion_examples()
    alpha_cut_reconstruction()
    statistical_analysis_example()
    