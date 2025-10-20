def word_count(text: str) -> int:
    """Verilmiş mətndə sözlərin sayını qaytarır"""
    return len(text.split())

def char_count(text: str) -> int:
    """Verilmiş mətndə hərflərin sayını qaytarır (boşluqlar daxil deyil)"""
    return len(text.replace(" ", ""))

def most_common_word(text: str) -> str:
    """Verilmiş mətndə ən çox istifadə olunan sözü qaytarır"""
    words = text.split()
    if not words:
        return ""
    word_freq = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1
    return max(word_freq, key=word_freq.get)

def unique_words(text: str) -> list:
    """Verilmiş mətndə unikal sözlərin siyahısını qaytarır"""
    return list(set(text.split()))
