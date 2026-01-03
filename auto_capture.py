"""
🧠 AUTO REFERENCE CAPTURE SYSTEM
Model %70+ güvenle bulduğu elementleri otomatik kayıt eder.
Bu referanslar gelecekte model eğitimi için kullanılabilir.
"""

import os
import time
from PIL import Image
from io import BytesIO
from datetime import datetime

class AutoReferenceCapture:
    def __init__(self, driver, output_dir="prototypes/auto_captured"):
        """
        Args:
            driver: Selenium WebDriver instance
            output_dir: Kayıt klasörü
        """
        self.driver = driver
        self.output_dir = output_dir
        self.min_confidence = 0.70  # %70 üzeri güven
        self.max_confidence = 0.95  # %95 altı (çok yüksekler zaten iyi)
        self.target_size = (64, 64)  # Model input boyutu
        self.captured_count = 0
        self.session_captures = []
        
        # Klasör oluştur
        os.makedirs(output_dir, exist_ok=True)
        print(f"📸 AutoReferenceCapture aktif: {output_dir}")
    
    def should_capture(self, confidence_score, category):
        """
        Capture edilmeli mi kontrol et
        
        Args:
            confidence_score: Model güven skoru (0-1)
            category: Element kategorisi (email, button, vb.)
        
        Returns:
            bool: Capture edilmeli mi
        """
        # Güven aralığı kontrolü
        if confidence_score < self.min_confidence:
            return False
        if confidence_score > self.max_confidence:
            return False  # Zaten çok iyi, eğitime gerek yok
        
        # Bazı kategorileri daha çok yakala
        priority_categories = ["email", "password", "button", "search", "add_to_cart", "checkout"]
        if category.lower() in priority_categories:
            return True
        
        return False
    
    def capture_element(self, element, category, site_name, confidence_score):
        """
        Element screenshot'ını kaydet
        
        Args:
            element: Selenium WebElement
            category: Element kategorisi
            site_name: Site adı (n11, trendyol, vb.)
            confidence_score: Model güven skoru
        
        Returns:
            str: Kaydedilen dosya yolu veya None
        """
        try:
            # Screenshot al
            screenshot = element.screenshot_as_png
            
            # PIL ile aç
            img = Image.open(BytesIO(screenshot))
            
            # Boyutlandır (model input boyutuna)
            img_resized = img.resize(self.target_size, Image.Resampling.LANCZOS)
            
            # RGB'ye çevir (RGBA olabilir)
            if img_resized.mode == 'RGBA':
                # Beyaz arka plan ile birleştir
                background = Image.new('RGB', self.target_size, (255, 255, 255))
                background.paste(img_resized, mask=img_resized.split()[3])
                img_resized = background
            elif img_resized.mode != 'RGB':
                img_resized = img_resized.convert('RGB')
            
            # 🆕 DUPLICATE CHECK: Benzer referans var mı kontrol et
            if self._is_duplicate(img_resized, category, site_name):
                return None  # Duplicate, kaydetme
            
            # Dosya adı oluştur
            timestamp = int(time.time())
            confidence_pct = int(confidence_score * 100)
            filename = f"{category}_auto_{site_name}_{confidence_pct}pct_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Kaydet
            img_resized.save(filepath, "PNG")
            
            self.captured_count += 1
            self.session_captures.append({
                "file": filename,
                "category": category,
                "site": site_name,
                "confidence": confidence_score,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"   📸 Referans yakalandı: {filename} (Güven: {confidence_pct}%)")
            return filepath
            
        except Exception as e:
            # Sessizce başarısız ol - ana işlemi bozma
            return None
    
    def _is_duplicate(self, new_img, category, site_name):
        """
        Yeni image duplicate mi kontrol et
        
        Args:
            new_img: PIL Image (zaten 64x64 RGB)
            category: Element kategorisi
            site_name: Site adı
        
        Returns:
            bool: Duplicate ise True
        """
        try:
            # Mevcut referansları kontrol et
            if not os.path.exists(self.output_dir):
                return False
            
            # 🆕 EVRENSEL: Aynı kategori için TÜM referansları bul (site fark etmez)
            # Email N11'de de Hepsiburada'da da benzer olabilir
            existing_refs = [
                f for f in os.listdir(self.output_dir)
                if f.startswith(f"{category}_auto_") and f.endswith(".png")
            ]
            
            # Hiç referans yoksa duplicate değil
            if not existing_refs:
                return False
            
            # Yeni image'i geçici kaydet (karşılaştırma için)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                new_img.save(tmp_path, "PNG")
            
            try:
                # AI model ile karşılaştır
                from ai_model import VisualBrain
                import config
                
                # Brain instance (cache varsa kullan)
                if not hasattr(self, '_brain'):
                    self._brain = VisualBrain(config.MODEL_PATH)
                
                # Mevcut referanslarla karşılaştır
                DUPLICATE_THRESHOLD = 0.95  # %95+ benzerlik = duplicate
                
                for ref_file in existing_refs[:5]:  # Son 5 referansı kontrol et (performans)
                    ref_path = os.path.join(self.output_dir, ref_file)
                    similarity = self._brain.compare_images(tmp_path, ref_path)
                    
                    if similarity > DUPLICATE_THRESHOLD:
                        print(f"   🔄 Duplicate atlandı: {ref_file} ile %{int(similarity*100)} benzer")
                        return True
                
                return False
                
            finally:
                # Geçici dosyayı temizle
                try:
                    os.remove(tmp_path)
                except:
                    pass
                
        except Exception as e:
            # Hata durumunda duplicate değil say (kaydetmeye devam et)
            return False
    
    def capture_if_worthy(self, element, category, site_name, confidence_score):
        """
        Uygunsa yakala - ana fonksiyon
        
        Returns:
            str: Dosya yolu veya None
        """
        if self.should_capture(confidence_score, category):
            return self.capture_element(element, category, site_name, confidence_score)
        return None
    
    def get_session_summary(self):
        """Oturum özeti döndür"""
        return {
            "total_captured": self.captured_count,
            "captures": self.session_captures,
            "output_dir": self.output_dir
        }
    
    def print_summary(self):
        """Özeti yazdır"""
        if self.captured_count > 0:
            print(f"\n📸 AUTO-CAPTURE ÖZET:")
            print(f"   Toplam Yakalanan: {self.captured_count}")
            print(f"   Klasör: {self.output_dir}")
            
            # Kategorilere göre dağılım
            category_counts = {}
            for cap in self.session_captures:
                cat = cap["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            for cat, count in category_counts.items():
                print(f"   - {cat}: {count} adet")


# === STANDALONE KULLANIM ===
if __name__ == "__main__":
    print("🧠 AutoReferenceCapture Module")
    print("Kullanım: SmartBot içinde otomatik çağrılır")
    print("Min Güven: 70%, Max Güven: 95%")
    print("Hedef Boyut: 64x64 px")
