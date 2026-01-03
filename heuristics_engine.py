# heuristics_engine.py
import unicodedata
import config
from similarity_utils import (
    levenshtein_similarity, 
    jaccard_similarity, 
    ngram_similarity, 
    combined_similarity
)

class Heuristics:
    def __init__(self):
        # Varsayılan ağırlıklar (kategori bazlı ağırlıklar config'den alınacak)
        self.DEFAULT_WEIGHTS = config.DEFAULT_WEIGHTS
        self.THRESHOLD = config.SCORE_THRESHOLD

        self.CRITICAL_KEYWORDS = {
            "login": ["giriş", "giris", "login", "sign in", "üye girişi", "uye girisi", "oturum aç", "tamam", "devam"],
            "signup": ["üye ol", "uye ol", "kayıt ol", "sign up", "register", "hesap oluştur"],
            "submit": ["gönder", "tamam", "onayla", "devam et", "kaydet", "giriş yap"],
            "email": ["e-posta", "eposta", "email", "mail", "kullanıcı adı", "username", "adresiniz"],
            "password": ["şifre", "sifre", "parola", "password", "pass", "key"],
            
            # 🆕 KAYIT FORMU İÇİN YENİ KATEGORİLER
            "text_input": ["isim", "ad", "name", "soyad", "soyisim", "surname", "telefon", "phone", "gsm", "cep"],
            "firstName": ["isim", "ad", "name", "first"],
            "lastName": ["soyad", "soyisim", "surname", "last"],
            "phone": ["telefon", "phone", "gsm", "cep", "mobile"],
            
            "search": ["ara", "search", "bul", "ürün ara", "marka ara", "kategori ara"],
            
            # 🆕 EVRENSEL E-TİCARET KEYWORD'LERİ
            "add_to_cart": [
                "sepete ekle", "add to cart", "sepete at", "hemen al", "satın al", "buy now",
                "sepet", "ekle", "add", "buy", "satın", "al",  # Daha kısa varyasyonlar
                "basket", "cart"  # İngilizce varyasyonlar
            ],
            "cart": ["sepetim", "sepet", "cart", "my cart", "basket", "sepetiniz"],
            "checkout": [
                "sepeti onayla", "alışverişi tamamla", "satın al", "ödeme yap", "checkout", 
                "confirm cart", "devam et", "onayla", "tamamla", "siparişi tamamla",
                "öde", "sipariş", "confirm", "complete", "proceed"  # Daha kısa varyasyonlar
            ]
        }

        self.NEGATIVE_KEYWORDS = [
            # Sosyal medya
            "facebook", "google", "apple", "iphone", "twitter", "instagram",
            # Yardım ve şifre kurtarma
            "unuttum", "forgot", "yardım", "help", "sıfırla", "reset",
            # Navigasyon ve layout
            "footer", "menu", "nav", "header", "sidebar",
            # Popup ve modal
            "close", "kapat", "popup", "reklam", "modal", "overlay",
            # Mağaza ve satıcı (sepet yerine mağazaya yönlendirme)
            "magaza", "satıcı", "seller", "store",
            # Favori ve beğeni
            "wishlist", "favourite", "favori", "begen", "like", "heart",
            # Oklar ve yönlendirmeler
            "arrow", "ok", "yon", "chevron", "scroll", "slider",
            # Kampanya ve promosyon
            "kampanya", "campaign", "banner", "promo",
            # 🆕 LOGO VE MARKA ELEMENTLERİ (N11 sorunu)
            "logo", "brand", "marka",
            # 🆕 MOBİL VE DESKTOP SPECİFİK
            "mobile", "desktop", "responsive",
            # 🆕 CONTAINER VE WRAPPER (Yanlış tıklama)
            "container", "wrapper", "holder", "box",
            # 🆕 ITEM VE LİST (Ürün kartları yerine buton)
            "itemcontainer", "item-container", "product-item", "card-item",
            # 🆕 IMAGE VE MEDIA
            "image", "img", "photo", "video", "media",
            # 🆕 CATEGORY VE FİLTRE
            "category", "kategori", "filter", "filtre", "sort", "sırala"
        ]

    @staticmethod
    def normalize_text(text):
        if not text: return ""
        text = text.replace("İ", "i").replace("I", "ı").replace("Ş", "ş").replace("Ğ", "ğ").replace("Ü", "ü").replace("Ö", "ö").replace("Ç", "ç")
        return " ".join(text.split()).lower()

    def get_xpath(self, category):
        """Legacy XPath metodu - geriye uyumluluk için korundu."""
        return self._get_fallback_xpath(category)
    
    def get_smart_xpath(self, category, driver=None):
        """
        🆕 SMART XPATH STRATEJİSİ
        
        Önce dar scope XPath'ler denenir (daha hızlı ve doğru).
        Bulunamazsa geniş scope'a fallback yapılır.
        
        Args:
            category: Element kategorisi
            driver: Selenium WebDriver (opsiyonel, dar scope test için)
        
        Returns:
            tuple: (xpath_string, scope_type)
        """
        # Dar scope XPath'ler - Daha spesifik, daha az element döner
        narrow_xpaths = {
            "email": [
                "//input[@type='email']",
                "//input[contains(@name, 'mail') or contains(@id, 'mail')]",
                "//input[contains(@placeholder, 'mail') or contains(@placeholder, 'posta')]",
                "//input[contains(@autocomplete, 'email')]",
            ],
            "password": [
                "//input[@type='password']",
                "//input[contains(@name, 'pass') or contains(@id, 'pass')]",
                "//input[contains(@name, 'sifre') or contains(@id, 'sifre')]",
            ],
            "search": [
                "//input[@type='search']",
                "//input[contains(@name, 'search') or contains(@id, 'search')]",
                "//input[contains(@name, 'q') or contains(@id, 'q')]",
                "//input[contains(@placeholder, 'ara') or contains(@placeholder, 'search')]",
                "//input[contains(@class, 'search')]",
            ],
            "add_to_cart": [
                # Türkçe butonlar
                "//button[contains(translate(., 'SEPETEKLİ', 'sepetekli'), 'sepete ekle')]",
                "//button[contains(., 'Sepete Ekle')]",
                "//a[contains(., 'Sepete Ekle')]",
                "//button[contains(., 'Hemen Al')]",
                "//button[contains(., 'Satın Al')]",
                # İngilizce butonlar
                "//button[contains(., 'Add to Cart')]",
                "//button[contains(., 'Buy Now')]",
                # Class bazlı
                "//button[contains(@class, 'add-to-cart') or contains(@class, 'addToCart')]",
                "//button[contains(@class, 'add-basket') or contains(@class, 'addBasket')]",
                "//button[contains(@class, 'buy-now') or contains(@class, 'buyNow')]",
                "//button[@data-testid='add-to-cart']",
                "//*[contains(@class, 'add') and contains(@class, 'cart')]//button",
                # Genel buton
                "//button[contains(@class, 'btn') and contains(@class, 'cart')]",
            ],
            "cart": [
                "//a[contains(@href, 'sepet') or contains(@href, 'cart') or contains(@href, 'basket')]",
                "//*[contains(@class, 'cart') or contains(@class, 'basket') or contains(@class, 'sepet')]//a",
                "//*[@id='cart' or @id='basket' or @id='sepet']//a",
                "//a[contains(@class, 'cart')]",
            ],
            "login_btn": [
                "//a[contains(@href, 'login') or contains(@href, 'giris')]",
                "//*[contains(@class, 'login') or contains(@class, 'signin')]//a",
                "//a[contains(., 'Giriş') or contains(., 'Login')]",
            ],
            "checkout": [
                # Türkçe butonlar
                "//button[contains(., 'Tamamla') or contains(., 'Onayla')]",
                "//button[contains(., 'Ödeme')]",
                "//a[contains(., 'Satın Al') or contains(., 'Ödeme')]",
                "//button[contains(., 'Siparişi Tamamla')]",
                "//button[contains(., 'Alışverişi Tamamla')]",
                # İngilizce butonlar
                "//button[contains(., 'Checkout')]",
                "//button[contains(., 'Complete')]",
                "//button[contains(., 'Proceed')]",
                # Class bazlı
                "//button[contains(@class, 'checkout') or contains(@class, 'confirm')]",
                "//button[contains(@class, 'complete') or contains(@class, 'proceed')]",
            ],
        }
        
        # Driver varsa ve dar scope test edilecekse
        if driver and category in narrow_xpaths:
            for xpath in narrow_xpaths[category]:
                try:
                    from selenium.webdriver.common.by import By
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        return xpath, "NARROW"
                except:
                    continue
        
        # Dar scope XPath string'i döndür (driver yoksa)
        if category in narrow_xpaths:
            # Tüm dar scope XPath'leri birleştir
            combined = " | ".join(narrow_xpaths[category])
            return combined, "NARROW_COMBINED"
        
        # Fallback - Geniş scope
        return self._get_fallback_xpath(category), "FALLBACK"
    
    def _get_fallback_xpath(self, category):
        """Geniş scope fallback XPath'ler."""
        if category in ["email", "password", "text_input", "search", "firstName", "lastName", "phone"]:
            return "//input[not(@type='hidden') and not(@type='submit') and not(@type='button')]"
        elif category in ["button", "add_to_cart", "login_btn", "signup"]: 
            return "//button | //a | //input[@type='submit'] | //*[contains(@class, 'btn')] | //*[contains(@id, 'btn')] | //div[@role='button'] | //span[@role='button'] | //span"
        return "//*"

    def score_tag_priority(self, tag_name, attributes, category):
        tag = tag_name.lower()
        role = attributes.get("role", "")
        cls = attributes.get("class", "").lower()
        id_val = attributes.get("id", "").lower()
        
        # --- INPUTLAR ---
        if category in ["email", "password", "search", "text_input", "firstName", "lastName", "phone"]:
            if tag == "input": return 1.0
            return 0.1

        # --- LOGIN NAVİGASYON ---
        if category == "login_btn":
            if "tab" in cls: return 0.1 
            if tag == "a": return 1.0
            if tag == "span" or tag == "div": return 0.9 
            if tag == "button": return 0.3 
            return 0.2

        # --- NORMAL BUTONLAR ---
        if category in ["button", "add_to_cart"]:
            if "tab" in cls: return 0.1 
            if "arrow" in cls or "chevron" in cls: return 0.05 # Okları cezalandır
            is_button_like = "btn" in cls or "button" in cls or "btn" in id_val or "button" in id_val or "add" in cls
            
            if tag == "button" and attributes.get("type") == "submit": return 1.0
            if tag == "button": return 0.95
            if tag == "div" and is_button_like: return 0.95
            if tag == "a": return 0.9 
            if role == "button": return 0.8
            if tag == "span" and is_button_like: return 0.8
            if tag == "div": return 0.4
        
        return 0.2

    def score_location(self, element_y, screen_height, category):
        if element_y > (screen_height * 0.95): return 0.1 
        
        if category == "login_btn":
            if element_y < 120: return 1.0 
            if element_y < 200: return 0.5 
            return 0.0 

        if category == "search":
            if element_y < 200: return 1.0
            return 0.5 
            
        if category in ["email", "password", "text_input", "firstName", "lastName", "phone"]:
            if element_y < 150: return 0.1  # Header'da olmamalı 
            
        # Sepetim butonu genelde Header'dadır (Sağ üst)
        if category == "cart":
            if element_y < 150: return 1.0
            return 0.5

        relative_y = element_y / screen_height
        if 0.2 <= relative_y <= 0.6: return 1.0 
        return 0.7

    def score_semantic(self, element_text, target_keywords_key="login"):
        """
        🆕 GELİŞTİRİLMİŞ SEMANTİK PUANLAMA (EVRENSEL UYUMLULUK)
        
        Birden fazla benzerlik metriği kullanarak daha doğru sonuçlar üretir.
        Negatif keyword kontrolü artık daha zeki çalışıyor.
        """
        if not element_text: return 0.0
        normalized_text = self.normalize_text(element_text)
        
        # 🆕 ÖNCE POZİTİF KEYWORD KONTROLÜ YAP
        # Eğer aranan keyword varsa, negatif kontrolü yapma
        keywords = self.CRITICAL_KEYWORDS.get(target_keywords_key, [])
        
        # Tam eşleşme var mı kontrol et
        has_positive_match = False
        for kw in keywords:
            if kw in normalized_text:
                has_positive_match = True
                break
        
        # Sadece pozitif eşleşme YOKSA negatif kontrolü yap
        # Bu sayede "Sepete Ekle" butonu "ekle" kelimesi yüzünden reddedilmez
        if not has_positive_match:
            for neg in self.NEGATIVE_KEYWORDS:
                if neg in normalized_text: 
                    return -0.3  # -0.5'ten -0.3'e düşürüldü (daha toleranslı)
            
        # --- ÖZEL SEMANTİK FİLTRELER ---
        if target_keywords_key == "cart":
            if "ekle" in normalized_text or "add" in normalized_text: return 0.0

        if target_keywords_key == "add_to_cart":
            if "git" in normalized_text or "go" in normalized_text: return 0.0
        
        best_match = 0.0
        for kw in keywords:
            # Tam eşleşme kontrolü
            if kw in normalized_text: 
                # Sepete Ekle için metin eşleşmesi KRİTİK öneme sahip
                if target_keywords_key == "add_to_cart" and ("sepete ekle" in normalized_text or "add to cart" in normalized_text):
                    return 3.0  # Çok güçlü sinyal
                    
                # Checkout için metin eşleşmesi de güçlü sinyal
                if target_keywords_key == "checkout" and ("alışverişi tamamla" in normalized_text or "ödeme" in normalized_text):
                    return 2.5  # Güçlü sinyal
                    
                return 1.0
            
            # 🆕 BİRLEŞİK BENZERLİK SKORU
            if len(kw) > 3:
                # Tüm similarity metriklerini kullan
                sim_combined = combined_similarity(normalized_text, kw)
                
                # N-gram ile ek kontrol ("sepete" vs "sepet" gibi)
                sim_ngram = ngram_similarity(normalized_text, kw, n=3)
                
                best_match = max(best_match, sim_combined, sim_ngram)
        
        # 🆕 EVRENSEL: Eşik değeri daha da düşürüldü (0.5 -> 0.3)
        # Farklı siteler farklı kelimeler kullanabilir
        return best_match if best_match > 0.3 else 0.0

    def score_proximity(self, element_y, reference_y):
        if reference_y is None: return 0.0
        distance = element_y - reference_y
        if 0 < distance < 250:
            return 0.3 
        elif distance > 250:
            return 0.05 
        return 0.0 

    def calculate_final_score(self, visual_score, semantic_score, location_score, tag_score, category="button"):
        """
        🆕 KATEGORİ BAZLI DİNAMİK PUANLAMA
        
        Her kategori için optimize edilmiş ağırlıklar kullanır.
        Ağırlıklar toplamı her zaman 1.0 olacak şekilde normalize edilmiştir.
        
        Args:
            visual_score: Görsel benzerlik skoru (0-1)
            semantic_score: Semantik eşleşme skoru (0-1, özel durumlarda >1 olabilir)
            location_score: Konum skoru (0-1)
            tag_score: HTML tag öncelik skoru (0-1)
            category: Element kategorisi (email, button, add_to_cart, etc.)
        
        Returns:
            tuple: (final_score, confidence_level)
        """
        # Kategori için ağırlıkları al
        weights = config.get_weights_for_category(category)
        
        # Semantik skor bazen 1'den büyük olabilir (güçlü eşleşme bonusu)
        # Bunu normalize edelim ama bonusu koruyalım
        semantic_normalized = min(semantic_score, 1.0)
        semantic_bonus = max(0, semantic_score - 1.0) * 0.15  # Bonus'un %15'ini ekle
        
        # Ağırlıklı toplam hesapla
        weighted_sum = (
            visual_score * weights["visual"] +
            semantic_normalized * weights["semantic"] +
            location_score * weights["location"] +
            tag_score * weights["tag"]
        )
        
        # Semantic bonus ekle
        weighted_sum += semantic_bonus
        
        # 🆕 EVRENSEL: Tag skoru cezası kaldırıldı
        # Farklı sitelerde farklı tag yapıları olabilir
        # if tag_score < 0.2:
        #     weighted_sum *= 0.5
        
        # 🆕 EVRENSEL: Negatif semantik skor cezası hafifletildi
        # Bazı siteler farklı kelimeler kullanabilir
        if semantic_score < 0:
            weighted_sum *= 0.5  # 0.3'ten 0.5'e yükseltildi (daha toleranslı)
        
        # Final skoru 0-1 arasında tut
        final_score = max(0.0, min(weighted_sum, 1.0))
        
        # Confidence level belirle
        confidence_level = self._get_confidence_level(final_score)
        
        return final_score, confidence_level
    
    def _get_confidence_level(self, score):
        """Skor bazlı güven seviyesi döner."""
        thresholds = config.CONFIDENCE_THRESHOLDS
        
        if score >= thresholds["high"]:
            return "HIGH"
        elif score >= thresholds["medium"]:
            return "MEDIUM"
        elif score >= thresholds["low"]:
            return "LOW"
        else:
            return "REJECT"
    
    # Geriye uyumluluk için eski metod imzası
    def calculate_final_score_legacy(self, visual_score, semantic_score, location_score, tag_score):
        """Eski kod için geriye uyumluluk."""
        score, _ = self.calculate_final_score(visual_score, semantic_score, location_score, tag_score)
        return score

