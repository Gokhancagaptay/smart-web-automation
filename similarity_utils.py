from __future__ import annotations


def _tokenize(text: str) -> set[str]:
    """Split the incoming text into lowercase whitespace tokens."""
    return {token for token in text.lower().split() if token}


def levenshtein_similarity(a: str, b: str) -> float:
    """Return a normalized Levenshtein similarity score between 0.0 and 1.0."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current = [i]
        for j, char_b in enumerate(b, start=1):
            cost = 0 if char_a == char_b else 1
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + cost,
                )
            )
        previous = current

    distance = previous[-1]
    normalizer = max(len(a), len(b))
    return 1.0 - (distance / normalizer)


def jaccard_similarity(a: str, b: str) -> float:
    """Return the Jaccard similarity of whitespace token sets."""
    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)

    if not tokens_a and not tokens_b:
        return 1.0

    union = tokens_a | tokens_b
    if not union:
        return 0.0

    intersection = tokens_a & tokens_b
    return len(intersection) / len(union)


def ngram_similarity(text: str, keyword: str, n: int = 2) -> float:
    """
    🆕 N-gram benzerlik skoru hesaplar.
    
    Kısmi eşleşmeleri yakalamak için karakter n-gram'larını kullanır.
    Örneğin "sepete" ve "sepet" yüksek benzerlik gösterir.
    
    Args:
        text: Karşılaştırılacak metin
        keyword: Anahtar kelime
        n: N-gram boyutu (varsayılan: 2 = bigram)
    
    Returns:
        float: 0.0 - 1.0 arası benzerlik skoru
    """
    if not text or not keyword:
        return 0.0
    
    text = text.lower()
    keyword = keyword.lower()
    
    # N-gram'ları oluştur
    def get_ngrams(s: str, n: int) -> set[str]:
        if len(s) < n:
            return {s}
        return {s[i:i+n] for i in range(len(s) - n + 1)}
    
    text_ngrams = get_ngrams(text, n)
    keyword_ngrams = get_ngrams(keyword, n)
    
    if not text_ngrams or not keyword_ngrams:
        return 0.0
    
    intersection = text_ngrams & keyword_ngrams
    union = text_ngrams | keyword_ngrams
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def substring_containment_score(text: str, keyword: str) -> float:
    """
    🆕 Substring içerme skoru.
    
    Keyword'ün text içinde geçip geçmediğini ve ne kadar örtüştüğünü ölçer.
    Tam içerme durumunda yüksek skor verir.
    
    Args:
        text: Ana metin
        keyword: Aranan kelime
    
    Returns:
        float: 0.0 - 1.0 arası içerme skoru
    """
    if not text or not keyword:
        return 0.0
    
    text = text.lower()
    keyword = keyword.lower()
    
    # Tam içerme
    if keyword in text:
        # Keyword'ün text'e oranı (daha kısa text daha yüksek skor)
        return min(1.0, len(keyword) / (len(text) * 0.5))
    
    # Text keyword içinde mi
    if text in keyword:
        return len(text) / len(keyword)
    
    return 0.0


def combined_similarity(text: str, keyword: str) -> float:
    """
    🆕 Birleşik benzerlik skoru.
    
    Tüm benzerlik metriklerini birleştirir ve en iyi skoru döner.
    
    Args:
        text: Karşılaştırılacak metin
        keyword: Anahtar kelime
    
    Returns:
        float: En yüksek benzerlik skoru
    """
    scores = [
        levenshtein_similarity(text, keyword),
        jaccard_similarity(text, keyword),
        ngram_similarity(text, keyword, n=2),
        ngram_similarity(text, keyword, n=3),
        substring_containment_score(text, keyword),
    ]
    
    return max(scores)

