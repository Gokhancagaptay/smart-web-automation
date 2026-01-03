import os
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ai_model import VisualBrain
from logger import get_healer_logger, PerformanceLogger  # 📝 LOGGING

# Logger instance
log = get_healer_logger()

class Healer:
    def __init__(self, driver):
        self.driver = driver
        self.brain = VisualBrain() 
        # Eşik değeri: Kendi eğittiğimiz model için biraz daha esnek olabilir (0.50 - 0.70 arası)
        self.threshold = 0.50 
        
        # Klasörler
        self.reference_folder = "reference_images" 
        self.dataset_pool = "universal_dataset_pool"
        
        # Klasörleri oluştur
        for folder in [self.reference_folder, f"{self.dataset_pool}/buttons", f"{self.dataset_pool}/inputs", f"{self.dataset_pool}/others"]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def find_element(self, by, value, element_key_name):
        """
        Elementi bulur, bulamazsa AI ile onarır, başarılıysa veri toplar.
        """
        found_element = None
        method_used = "MECHANICAL"

        try:
            # --- YOL 1: MEKANİK ARAMA ---
            # 10 saniye bekle
            found_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((by, value))
            )
            # Referans görseli (Golden Image) yedekle
            self._save_reference_image(found_element, element_key_name)

        except Exception as e:
            # --- YOL 2: SELF-HEALING (AI) ---
            log.warning(f"'{element_key_name}' normal yolla bulunamadı!")
            log.info("SELF-HEALING (AI) Modülü devreye giriyor...")
            
            found_element = self._heal_with_ai(element_key_name)
            method_used = "AI_REPAIR"
            
            if not found_element:
                # AI da bulamazsa hatayı fırlat
                raise e 

        # --- VERİ MADENCİLİĞİ (Gelecek Vizyonu) ---
        if found_element:
            self._collect_training_data(found_element, element_key_name, method_used)
            
        return found_element

    def _highlight_element(self, element):
        """Elementin etrafına kırmızı çerçeve çizer."""
        try:
            self.driver.execute_script("arguments[0].style.border='3px solid red'", element)
            time.sleep(0.5) # Şov için biraz bekle
        except: pass

    def _is_good_element(self, element):
        """Elementin fotoğraf çekmeye değer olup olmadığını kontrol eder."""
        try:
            if not element.is_displayed(): return False
            size = element.size
            if size['width'] < 20 or size['height'] < 10: return False
            return True
        except:
            return False

    def _collect_training_data(self, element, name, method):
        """Başarılı elementi havuza atar."""
        if not self._is_good_element(element): return

        try:
            category = "others"
            if any(x in name for x in ["btn", "button", "buton", "link"]):
                category = "buttons"
            elif any(x in name for x in ["input", "field", "kutu"]):
                category = "inputs"
            
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{name}_{method}_{unique_id}.png"
            save_path = os.path.join(self.dataset_pool, category, filename)
            
            # Kaydetmeden önce elemente odaklan
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            
            element.screenshot(save_path)
        except:
            pass 

    def _save_reference_image(self, element, name):
        """Self-Healing için referans kaydeder."""
        ref_path = os.path.join(self.reference_folder, f"{name}.png")
        
        if os.path.exists(ref_path): return

        if self._is_good_element(element):
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.2)
                element.screenshot(ref_path)
                log.debug(f"Referans kaydedildi: {name}")
            except:
                pass

    def _heal_with_ai(self, name):
        """Görsel onarım yapar."""
        ref_path = os.path.join(self.reference_folder, f"{name}.png")
        
        if not os.path.exists(ref_path):
            log.error(f"Onarım başarısız: '{name}' için referans görseli yok.")
            return None

        log.info("Görsel analiz yapılıyor...")
        # Sayfadaki potansiyel adayları topla
        candidates = self.driver.find_elements(By.XPATH, "//button | //input | //a | //div[@role='button']")
        
        best_score = 0
        best_element = None
        temp_path = "temp_candidate_snapshot.png"

        for element in candidates:
            try:
                if not self._is_good_element(element): continue
                
                element.screenshot(temp_path)
                score = self.brain.compare_images(ref_path, temp_path)
                
                if score > best_score:
                    best_score = score
                    best_element = element
            except: continue

        if os.path.exists(temp_path): os.remove(temp_path)

        log.info(f"AI analiz bitti. En yüksek skor: {best_score:.4f}")
        
        if best_score >= self.threshold:
            log.info("Onarım BAŞARILI!")
            self._highlight_element(best_element) 
            
            # --- STALE ELEMENT FIX (YENİDEN BULMA) ---
            # Bulunan element bayatlamış olabilir, taze kopyasını bulalım.
            try:
                # Elementin mutlak XPath'ini çıkaran JavaScript
                xpath = self.driver.execute_script(
                    "function absoluteXPath(element) {"
                    "var comp, comps = [];"
                    "var parent = null;"
                    "var xpath = '';"
                    "var getPos = function(element) {"
                    "var position = 1, curNode;"
                    "if (element.nodeType == Node.ATTRIBUTE_NODE) { return null; }"
                    "for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {"
                    "if (curNode.nodeName == element.nodeName) { ++position; }"
                    "}"
                    "return position;"
                    "};"
                    "if (element instanceof Document) { return '/'; }"
                    "for (; element && !(element instanceof Document); element = element.parentNode) {"
                    "comp = comps[comps.length] = {};"
                    "comp.name = element.nodeName;"
                    "comp.position = getPos(element);"
                    "}"
                    "for (var i = comps.length - 1; i >= 0; i--) {"
                    "comp = comps[i];"
                    "xpath += '/' + comp.name.toLowerCase();"
                    "if (comp.position !== null) { xpath += '[' + comp.position + ']'; }"
                    "}"
                    "return xpath;"
                    "} return absoluteXPath(arguments[0]);", best_element
                )
                
                # O XPath ile taze elementi bulup döndür
                fresh_element = self.driver.find_element(By.XPATH, xpath)
                return fresh_element
                
            except Exception as e:
                # XPath üretemezse veya bulamazsa, mecburen eskiyi döndür
                log.warning(f"Element tazelenirken hata oluştu (Eski element kullanılacak): {e}")
                return best_element
            # -------------------------------------------
            
        else:
            log.error("Onarım başarısız: Yeterince benzeyen bir eleman bulunamadı.")
            return None