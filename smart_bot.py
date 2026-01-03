# smart_bot.py
import time
import os
import datetime
import random 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from ai_model import VisualBrain
from heuristics_engine import Heuristics
from recovery_manager import RecoveryManager  # 🔄 SELF-RECOVERY
from learning_system import LearningSystem  # 🧠 LEARNING
from logger import get_bot_logger, PerformanceLogger  # 📝 LOGGING
from auto_capture import AutoReferenceCapture  # 📸 AUTO-CAPTURE
import config

# Logger instance
log = get_bot_logger()

class SmartBot:
    def __init__(self, driver, reporter=None):
        self.driver = driver
        self.brain = VisualBrain(config.MODEL_PATH) 
        self.rules = Heuristics()
        self.prototypes_dir = config.PROTOTYPES_DIR
        
        self.evidence_dir = "evidence"
        if not os.path.exists(self.evidence_dir):
            os.makedirs(self.evidence_dir)
            
        self.log_file = os.path.join(self.evidence_dir, "action_log.txt")
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"--- TEST BAŞLANGICI: {datetime.datetime.now()} ---\n")
            
        self.interacted_elements = set()
        self.last_interaction = {"id": None, "action": None}
        self.last_input_y = None
        
        # 🆕 CACHE SİSTEMİ (Hafıza)
        self.element_cache = {}  # {"email": {"element": WebElement, "url": "...", "timestamp": ...}}
        
        # 📊 RAPORLAMA SİSTEMİ
        self.reporter = reporter
        
        # 🔄 SELF-RECOVERY SİSTEMİ
        self.recovery = RecoveryManager(max_retries=3, reporter=reporter)
        
        # 🧠 LEARNING SİSTEMİ
        self.learning = LearningSystem(knowledge_file="knowledge/learned_patterns.json") 
        
        # 📸 AUTO-CAPTURE SİSTEMİ (High confidence referansları kaydet)
        self.auto_capture = AutoReferenceCapture(driver, output_dir="prototypes/auto_captured") 

    def log_action(self, action_type, category, details, element):
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        log_msg = f"[{timestamp}] {action_type.upper()} -> {category}: {details}\n"
        print(f"   📝 {log_msg.strip()}")
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg)
        
        try:
            screenshot_name = f"{timestamp}_{category}_{action_type}.png"
            path = os.path.join(self.evidence_dir, screenshot_name)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.driver.execute_script("arguments[0].style.border='5px solid red !important'", element)
            time.sleep(0.5)
            self.driver.save_screenshot(path)
        except Exception as e:
            print(f"   ⚠️ Ekran görüntüsü alınamadı: {e}")

    def _extract_site_name(self, url):
        """URL'den site ismini çıkar"""
        if "n11" in url:
            return "n11"
        elif "hepsiburada" in url:
            return "hepsiburada"
        elif "trendyol" in url:
            return "trendyol"
        else:
            return "unknown"
    
    def get_element_attributes(self, element):
        attrs = {}
        try:
            attrs['tag'] = element.tag_name
            attrs['role'] = element.get_attribute("role") or ""
            attrs['type'] = element.get_attribute("type") or ""
            attrs['class'] = element.get_attribute("class") or ""
            attrs['id'] = element.get_attribute("id") or ""
            attrs['text'] = (element.text or "")[:30]
            attrs['placeholder'] = element.get_attribute("placeholder") or ""
            attrs['value'] = element.get_attribute("value") or "" 
            attrs['title'] = element.get_attribute("title") or "" 
        except:
            pass
        return attrs
    
    def smart_wait(self, condition_type="page_ready", timeout=10, custom_condition=None):
        """
        🆕 DİNAMİK WAIT SİSTEMİ
        Sabit time.sleep() yerine gerçek koşullara göre bekler.
        
        Args:
            condition_type: "page_ready", "url_change", "element_clickable", "custom"
            timeout: Maksimum bekleme süresi
            custom_condition: Özel Selenium EC koşulu
        """
        start_time = time.time()
        
        try:
            if condition_type == "page_ready":
                # Sayfa yüklenmesini bekle
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            elif condition_type == "url_change":
                # URL değişimini bekle
                current_url = self.driver.current_url
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.current_url != current_url
                )
            elif condition_type == "custom" and custom_condition:
                # Özel koşul
                WebDriverWait(self.driver, timeout).until(custom_condition)
            
            elapsed = time.time() - start_time
            print(f"   ⏱️ Bekleme süresi: {elapsed:.2f}s (Koşul: {condition_type})")
            
            # 📊 Reporter'a kaydet
            if self.reporter:
                self.reporter.log_wait(wait_type=condition_type, duration=elapsed, success=True)
            
            return True

        except TimeoutException:
            elapsed = time.time() - start_time
            print(f"   ⚠️ Timeout: {elapsed:.2f}s geçti, devam ediliyor...")
            
            # 📊 Reporter'a kaydet
            if self.reporter:
                self.reporter.log_wait(wait_type=condition_type, duration=elapsed, success=False)
                self.reporter.log_warning(f"Timeout: {condition_type} koşulu {elapsed:.2f}s'de karşılanmadı")
            
            return False
    
    def close_popups(self):
        try:
            popup_keywords = ["kapat", "close", "reddet", "kabul et", "tamam", "anladım", "reject", "accept", "x"]
            candidates = self.driver.find_elements(By.XPATH, "//button | //a | //div[@role='button'] | //span[@role='button']")
            
            for el in candidates:
                if not el.is_displayed(): continue
                text = (el.text or "").lower()
                cls = (el.get_attribute("class") or "").lower()
                id_val = (el.get_attribute("id") or "").lower()
                
                is_popup = any(k in text for k in popup_keywords) or \
                           any(k in cls for k in ["close", "popup", "cookie", "modal", "overlay"]) or \
                           any(k in id_val for k in ["close", "popup", "cookie"])
                           
                if is_popup:
                    if el.size['width'] > 10 and el.size['height'] > 10:
                        print(f"   🧹 Temizlik: Pop-up kapatılıyor... ({text[:10]} | {cls[:15]})")
                        try:
                            el.click()
                            time.sleep(0.5)
                        except:
                            pass
        except:
            pass

    def auto_detect_category(self, target_text):
        """
        🆕 AKILLI KATEGORİ TESPİTİ
        Kullanıcının verdiği metinden otomatik olarak doğru kategoriyi belirler.
        """
        if not target_text:
            return "button"
            
        text = str(target_text).lower()
        
        # Önce en spesifik olanlardan başla
        if "sepete ekle" in text or "add to cart" in text or "hemen al" in text:
            return "add_to_cart"
        elif "sepet" in text or "cart" in text or "basket" in text:
            return "cart"
        elif "ara" in text or "search" in text or "bul" in text:
            return "search"
        elif "e-posta" in text or "email" in text or "mail" in text:
            return "email"
        elif "şifre" in text or "sifre" in text or "password" in text or "parola" in text:
            return "password"
        elif "isim" in text or "name" in text or "ad" in text or "soyad" in text or "surname" in text:
            return "text_input"
        elif "telefon" in text or "phone" in text or "gsm" in text:
            return "text_input"
        elif "üye ol" in text or "kayıt ol" in text or "register" in text or "sign up" in text:
            return "button"  # Kayıt butonu
        elif "giriş yap" in text or "login" in text or "sign in" in text:
            return "button"  # Form submit butonu olarak işle
        elif "onayla" in text or "tamamla" in text or "checkout" in text or "ödeme" in text:
            return "checkout"
        else:
            return "button"  # Default
    
    def check_semantic_match(self, element, target_text):
        try:
            # Element attribute'larını al
            el_text = (element.text or "").lower()
            el_class = (element.get_attribute("class") or "").lower()
            el_id = (element.get_attribute("id") or "").lower()
            
            # 🆕 CLASS VE ID İÇİN AYRI NEGATİF KEYWORD KONTROLÜ
            # Bu çok önemli - text doğru olsa bile class yanlışsa reddet
            
            # Kategoriyi belirle (target_text'ten)
            t = str(target_text).lower() if target_text else ""
            is_input_category = ("mail" in t or "posta" in t or "şifre" in t or 
                                 "sifre" in t or "pass" in t or "ara" in t or "search" in t)
            
            # INPUT KATEGORİLERİ İÇİN KONTROL ATLANIYOR
            # Email, password, search gibi input'lar genelde header içinde olur
            if not is_input_category:
                class_negative_keywords = [
                    # Logo ve marka
                    "logo", "brand", "marka",
                    # Cihaz spesifik
                    "mobile", "desktop", "responsive",
                    # Container ve wrapper
                    "container", "wrapper", "holder", "item",
                    # Medya
                    "image", "img", "banner", "slider", "carousel",
                    # Layout - header hariç (input'lar header'da olabilir)
                    "footer", "nav", "menu", "sidebar",
                    # 🆕 SEO VE CONTENT (N11 sorunu - showSeoContent)
                    "seo", "content", "show", "hide", "toggle",
                    # 🆕 SWIPER VE SLIDER
                    "swiper", "slide", "prev", "next",
                    # 🆕 OVERLAY VE MODAL
                    "overlay", "modal", "popup", "dialog",
                    # 🆕 SOCIAL VE SHARE
                    "social", "share", "facebook", "twitter", "instagram",
                    # 🆕 ADVERTISEMENT - "ad" çıkarıldı çünkü "add-to-cart" class'ını yakalıyordu!
                    "advertisement", "sponsor", "adsense", "ad-banner"
                ]
                
                # 🆕 ADD-TO-CART KORUNUYOR
                # Class'ta "add" varsa bu muhtemelen sepete ekle butonudur, atla
                if "add" in el_class and ("cart" in el_class or "basket" in el_class):
                    pass  # Bu bir sepete ekle butonu, negatif kontrolü atla
                else:
                    for neg in class_negative_keywords:
                        if neg in el_class or neg in el_id:
                            # Eğer class/id negatif keyword içeriyorsa, skoru çok düşür
                            return -1.0
            
            # DAHA KAPSAMLI ÖZELLİK TARAMASI (Class ve ID dahil!)
            own_text = (element.text or "") + " " + \
                       (element.get_attribute("innerText") or "") + " " + \
                       (element.get_attribute("value") or "") + " " + \
                       (element.get_attribute("placeholder") or "") + " " + \
                       (element.get_attribute("title") or "") + " " + \
                       (element.get_attribute("aria-label") or "") + " " + \
                       el_class + " " + el_id
            
            t = str(target_text).lower()
            key = "submit"
            if "posta" in t or "email" in t or "mail" in t: key = "email"
            elif "şifre" in t or "sifre" in t or "pass" in t: key = "password"
            elif "isim" in t or "name" in t or "ad" in t: key = "text_input"
            elif "telefon" in t or "phone" in t or "gsm" in t: key = "phone"
            elif "iriş" in t or "ogin" in t: key = "login"
            elif "ye" in t or "kayıt" in t: key = "signup"
            elif "ara" in t or "search" in t or "bul" in t: key = "search"
            elif "sepet" in t or "cart" in t: key = "cart"
            elif "ekle" in t or "add" in t: key = "add_to_cart"
            elif "onayla" in t or "tamamla" in t or "checkout" in t or "satın" in t: key = "checkout"

            return self.rules.score_semantic(own_text, target_keywords_key=key)
        except:
            return 0.0

    def scan_and_decide(self, category, target_text=None):
        print(f"\n🤖 Analiz Başlıyor: '{category}' aranıyor (Hedef: {target_text})...")
        scan_start_time = time.time()
        
        # 🆕 CACHE KONTROLÜ (Hafızadan Al)
        current_url = self.driver.current_url
        cache_key = f"{category}_{current_url}"
        
        if cache_key in self.element_cache:
            try:
                cached = self.element_cache[cache_key]
                element = cached["element"]
                
                # Hala geçerli mi kontrol et
                if element.is_displayed() and element.is_enabled():
                    print(f"   ⚡ CACHE HIT: '{category}' hafızadan alındı! (Zaman Kazancı: ~2-3s)")
                    
                    # 📊 Reporter'a kaydet
                    if self.reporter:
                        self.reporter.log_scan(
                            category=category,
                            elements_found=1,
                            best_score=cached["score"],
                            duration=time.time() - scan_start_time,
                            cache_hit=True
                        )
                    
                    # Yine de winner formatında dönmeli
                    attrs = self.get_element_attributes(element)
                    winner = {
                        "element": element,
                        "score": cached["score"],
                        "attrs": attrs,
                        "details": "CACHED"
                    }
                    return element, winner
            except:
                # Cache eskimiş, sil ve yeniden ara
                print(f"   🗑️ Cache eskimiş, yeniden taranıyor...")
                del self.element_cache[cache_key]
        
        # 🆕 REFERANS YÜK: Primary + Fallback
        # Primary: prototypes/*.png
        refs = [os.path.join(self.prototypes_dir, f) for f in os.listdir(self.prototypes_dir) if category.lower() in f.lower() and f.endswith(".png")]
        
        # 🆕 FALLBACK HAZIRLA: auto_captured/*.png (henüz kullanılmayacak)
        auto_captured_dir = os.path.join(self.prototypes_dir, "auto_captured")
        auto_refs = []
        if os.path.exists(auto_captured_dir):
            auto_refs = [os.path.join(auto_captured_dir, f) for f in os.listdir(auto_captured_dir) if category.lower() in f.lower() and f.endswith(".png")]
        
        initial_ref_count = len(refs)
        
        # 🆕 SMART XPATH STRATEJİSİ
        # Önce dar scope dene, bulamazsa geniş scope'a geç
        xpath, scope_type = self.rules.get_smart_xpath(category, self.driver)
        
        time.sleep(0.5)  # Reduced from 1s
        elements = self.driver.find_elements(By.XPATH, xpath)
        
        # Dar scope boş döndüyse fallback'e geç
        if not elements and scope_type != "FALLBACK":
            print(f"   ⚠️ Dar scope ({scope_type}) boş, geniş scope deneniyor...")
            xpath = self.rules.get_xpath(category)  # Fallback
            elements = self.driver.find_elements(By.XPATH, xpath)
            scope_type = "FALLBACK"
        
        candidates = []
        screen_height = self.driver.execute_script("return window.innerHeight")

        scope_emoji = {"NARROW": "🎯", "NARROW_COMBINED": "🎯", "FALLBACK": "🔍"}.get(scope_type, "🔍")
        print(f"   {scope_emoji} {len(elements)} element bulundu ({scope_type}). Detaylı analiz başlıyor...")

        for i, el in enumerate(elements):
            try:
                if not el.is_displayed(): 
                    if category == "search":
                        print(f"      🚫 Search Debug: Element {i} görünür değil")
                    continue
                size = el.size
                if size['width'] < 20 or size['height'] < 20: 
                    if category == "search":
                        print(f"      🚫 Search Debug: Element {i} çok küçük ({size['width']}x{size['height']})")
                    continue
                
                attrs = self.get_element_attributes(el)
                el_id = attrs['id']
                
                if el_id and self.last_interaction['id'] == el_id:
                    if category == "button" or category == "add_to_cart":
                         print(f"      🚫 Atlandı (Döngü Koruması): {el_id}")
                         continue

                # Doluluk kontrolü sadece password için (search ve text_input muaf)
                if category == "password" and len(attrs.get('value', '')) > 3:
                    print(f"      🚫 Atlandı (İçi Dolu): {el_id}")
                    continue

                loc_score = self.rules.score_location(el.location['y'], screen_height, category)
                tag_score = self.rules.score_tag_priority(el.tag_name, attrs, category)
                sem_score = self.check_semantic_match(el, target_text)
                
                # 🆕 ADD_TO_CART DEBUG - Neden bulunamadığını görmek için
                if category == "add_to_cart":
                    el_text = (el.text or "")[:50]
                    print(f"      🔍 AddToCart Debug: Element {i}")
                    print(f"          Text: '{el_text}'")
                    print(f"          Tag: {attrs.get('tag')} | Class: {(attrs.get('class') or '')[:30]}")
                    print(f"          Sem:{sem_score:.2f} Loc:{loc_score:.2f} Tag:{tag_score:.2f}")
                
                # 🆕 EARLY STOPPING - Semantik skor çok yüksekse görsel analizi atla
                # Bu "Sepete Ekle" gibi tam eşleşmelerde büyük zaman kazandırır
                skip_visual = False
                if sem_score >= 2.0:  # Güçlü semantik eşleşme (örn: "sepete ekle" tam eşleşme)
                    skip_visual = True
                    vis_score = 0.5  # Varsayılan görsel skor
                
                # 🆕 GÖRSEL ANALİZ OPTİMİZASYONU
                if not skip_visual:
                    vis_score = 0.0
                    
                    # Sadece ilk N elementi görsel analiz et (performans için)
                    MAX_VISUAL_ANALYSIS = 15
                    
                    if refs and self.brain.model and i < MAX_VISUAL_ANALYSIS:
                        try:
                            # Elementi görsel olarak kaydet
                            temp_el_img = f"{config.TEMP_SCAN_IMAGE.replace('.png', '')}_{i}.png"
                            el.screenshot(temp_el_img)
                            
                            # 🆕 İLK PROTOTYPE YETERLİ - Eğer yüksek skor bulursan dur
                            max_similarity = 0.0
                            for ref_path in refs[:2]:  # Sadece ilk 2 prototype (hız için)
                                similarity = self.brain.compare_images(temp_el_img, ref_path)
                                max_similarity = max(max_similarity, similarity)
                                
                                # Early exit - Yeterince yüksek skor bulunduysa dur
                                if max_similarity > 0.85:
                                    break
                            
                            vis_score = max_similarity
                            
                            # Temizlik
                            try:
                                os.remove(temp_el_img)
                            except:
                                pass
                                
                        except Exception as e:
                            # Görsel analiz başarısız, fallback
                            vis_score = 0.25 if refs else 0.0
                    else:
                        # Görsel analiz atlandı veya model yok
                        vis_score = 0.25 if refs else 0.0
                
                proximity_bonus = 0.0
                if category == "button" and self.last_input_y:
                    proximity_bonus = self.rules.score_proximity(el.location['y'], self.last_input_y)

                # 🆕 KATEGORİ BAZLI DİNAMİK PUANLAMA
                final_score, confidence_level = self.rules.calculate_final_score(
                    vis_score, sem_score, loc_score, tag_score, category=category
                )
                final_score += proximity_bonus
                
                # Minimum eşik kontrolü
                min_threshold = config.get_min_threshold_for_category(category)
                
                # 🆕 SEARCH DEBUG
                if category == "search":
                    print(f"      🔍 Search Debug: Element {i}")
                    print(f"          V:{vis_score:.2f} S:{sem_score:.1f} L:{loc_score:.1f} T:{tag_score:.1f}")
                    print(f"          Final:{final_score:.2f} Threshold:{min_threshold:.2f} Conf:{confidence_level}")

                # 🆕 SEARCH İÇİN DAHA TOLERANSLI EŞİK
                # Search input'ları kritik olduğu için düşük skorlu bile kabul et
                if category == "search" and attrs.get('tag', '').lower() == 'input':
                    if final_score > 0.0:  # Herhangi bir pozitif skor varsa kabul et
                        candidates.append({
                            "element": el,
                            "score": final_score,
                            "confidence": confidence_level,
                            "attrs": attrs,
                            "visual_score": vis_score,
                            "details": f"V:{vis_score:.2f} S:{sem_score:.1f} L:{loc_score:.1f} T:{tag_score:.1f} P:{proximity_bonus:.2f} [{confidence_level}]"
                        })
                        continue
                
                # 🆕 EVRENSEL: ADD_TO_CART VE CHECKOUT İÇİN DE TOLERANSLI EŞİK
                # Bu butonlar farklı sitelerde çok farklı yapıda olabilir
                if category in ["add_to_cart", "checkout"] and attrs.get('tag', '').lower() in ['button', 'a', 'div', 'span']:
                    if final_score > 0.05:  # Çok düşük eşik - pozitif skor varsa kabul et
                        candidates.append({
                            "element": el,
                            "score": final_score,
                            "confidence": confidence_level,
                            "attrs": attrs,
                            "visual_score": vis_score,
                            "details": f"V:{vis_score:.2f} S:{sem_score:.1f} L:{loc_score:.1f} T:{tag_score:.1f} P:{proximity_bonus:.2f} [{confidence_level}]"
                        })
                        continue

                if final_score > min_threshold or confidence_level != "REJECT":
                    candidates.append({
                        "element": el,
                        "score": final_score,
                        "confidence": confidence_level,
                        "attrs": attrs,
                        "visual_score": vis_score,  # 📸 Auto-capture için
                        "details": f"V:{vis_score:.2f} S:{sem_score:.1f} L:{loc_score:.1f} T:{tag_score:.1f} P:{proximity_bonus:.2f} [{confidence_level}]"
                    })
            except:
                continue

        if not candidates: return None

        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # --- DEBUG: İLK 3 ADAYI GÖSTER ---
        print("\n   🔍 EN İYİ ADAYLAR:")
        for idx, cand in enumerate(candidates[:3]):
            identifier = f"ID:{cand['attrs']['id']}" if cand['attrs']['id'] else f"CLASS:{cand['attrs']['class']}"
            conf_emoji = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "REJECT": "🔴"}.get(cand.get('confidence', 'LOW'), "⚪")
            print(f"      #{idx+1}: {cand['attrs']['tag']} (Skor: {cand['score']:.4f}) {conf_emoji} {identifier}")
            print(f"          └-> {cand['details']}")
            
        winner = candidates[0]
        
        # 🆕 FALLBACK: Düşük skor ve auto_refs varsa tekrar tara
        FALLBACK_THRESHOLD = 0.7
        if winner['score'] < FALLBACK_THRESHOLD and auto_refs and initial_ref_count > 0:
            print(f"   ⚠️ Düşük skor ({winner['score']:.2f}), auto_captured refs ile tekrar taranıyor...")
            print(f"   📁 Referans sayısı: {initial_ref_count} → {initial_ref_count + len(auto_refs)} (+{len(auto_refs)} auto)")
            
            # Auto-captured ile tüm candidate'ları tekrar değerlendir
            improved_count = 0
            for cand in candidates[:5]:  # İlk 5 candidate
                el = cand['element']
                try:
                    temp_el_img = f"{config.TEMP_SCAN_IMAGE.replace('.png', '')}_fallback.png"
                    el.screenshot(temp_el_img)
                    
                    # Auto refs ile karşılaştır
                    max_auto_sim = 0.0
                    for ref_path in auto_refs[:3]:
                        sim = self.brain.compare_images(temp_el_img, ref_path)
                        max_auto_sim = max(max_auto_sim, sim)
                    
                    # İyileştirme varsa uygula
                    if max_auto_sim > cand.get('visual_score', 0):
                        old_score = cand['score']
                        score_boost = (max_auto_sim - cand.get('visual_score', 0)) * 0.4
                        cand['score'] += score_boost
                        cand['visual_score'] = max_auto_sim
                        improved_count += 1
                        print(f"      ✨ #{candidates.index(cand)+1} iyileşti: {old_score:.2f} → {cand['score']:.2f}")
                    
                    try:
                        os.remove(temp_el_img)
                    except:
                        pass
                except:
                    pass
            
            if improved_count > 0:
                candidates.sort(key=lambda x: x['score'], reverse=True)
                old_winner_score = winner['score']
                winner = candidates[0]
                print(f"   🔄 Fallback sonucu: {old_winner_score:.2f} → {winner['score']:.2f}")
        
        identifier = f"ID:{winner['attrs']['id']}" if winner['attrs']['id'] else f"CLASS:{winner['attrs']['class']}"
        conf_emoji = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "REJECT": "🔴"}.get(winner.get('confidence', 'LOW'), "⚪")
        print(f"\n   🏆 KAZANAN: {winner['attrs']['tag']} (Skor: {winner['score']:.4f}) {conf_emoji} {winner.get('confidence', 'N/A')} {identifier}")
        
        # 📊 Reporter'a kaydet
        scan_duration = time.time() - scan_start_time
        if self.reporter:
            self.reporter.log_scan(
                category=category,
                elements_found=len(elements),
                best_score=winner['score'],
                duration=scan_duration,
                cache_hit=False
            )
        
        # 🆕 CACHE'E KAYDET (Gelecekte kullan)
        self.element_cache[cache_key] = {
            "element": winner['element'],
            "score": winner['score'],
            "url": current_url,
            "timestamp": time.time()
        }
        print(f"   💾 Cache'e kaydedildi: {cache_key}")
        
        return winner['element'], winner

    def interact(self, category, text=None, target_text=None):
        interact_start_time = time.time()
        
        result = self.scan_and_decide(category, target_text)
        if not result:
            print(f"❌ Element bulunamadı: {category}")
            
            # 📊 Reporter'a hata kaydet
            if self.reporter:
                self.reporter.log_error(
                    error_type="ElementNotFound",
                    message=f"Element bulunamadı: {category} (target: {target_text})",
                    element_info={"category": category, "target_text": target_text}
                )
            
            return False
            
        element, winner_data = result
        el_id = winner_data['attrs']['id']
        el_class = winner_data['attrs']['class']
        el_tag = winner_data['attrs']['tag']

        try:
            identifier = f"ID:{el_id}" if el_id else f"CLASS:{el_class}" if el_class else f"TAG:{el_tag}"
            details = f"Skor:{winner_data['score']:.2f} {identifier}"
            
            if text:
                self.log_action("TYPE", category, f"{details} -> Yazılan: {text}", element)
                element.click()
                time.sleep(0.5)  # Focus için bekle
                
                # 🆕 SEARCH İÇİN ACTIONCHAINS İLE YAZMA
                # Vue.js/React bazlı siteler için karakter karakter yazma gerekli
                if category == "search":
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        
                        # Önce element'i temizle
                        element.clear()
                        time.sleep(0.3)
                        
                        # ActionChains ile karakter karakter yaz
                        # Bu Vue/React state'ini düzgün günceller
                        actions = ActionChains(self.driver)
                        actions.click(element)
                        actions.pause(0.3)
                        
                        # Her karakteri tek tek yaz (human-like)
                        for char in text:
                            actions.send_keys(char)
                            actions.pause(0.05)  # Karakterler arası kısa bekleme
                        
                        # Biraz bekle sonra Enter
                        actions.pause(0.5)
                        actions.send_keys(Keys.ENTER)  # 🆕 Enter ActionChains içinde!
                        
                        actions.perform()
                        print(f"   📝 ActionChains ile yazıldı: {text}")
                        print("   ↵ Enter tuşuna basıldı.")
                        
                        # Sayfa yüklenmesini bekle
                        time.sleep(3)
                    except Exception as e:
                        print(f"   ⚠️ ActionChains hatası: {e}")
                        # Fallback: Normal send_keys dene
                        element.clear()
                        element.send_keys(text)
                        element.send_keys(Keys.ENTER)
                        time.sleep(2)
                else:
                    element.clear()
                    element.send_keys(text)
                
                # 🆕 SEARCH SONRASI STALE ELEMENT'DEN KAÇIN
                # Sayfa değiştikten sonra eski element'e erişmeye çalışma
                if category != "search":
                    self.last_interaction = {"id": el_id, "action": "TYPE"}
                    try:
                        self.last_input_y = element.location['y']
                    except:
                        self.last_input_y = 0
                else:
                    self.last_interaction = {"id": el_id, "action": "TYPE"}
                    self.last_input_y = 0  # Sayfa değişti, eski location geçersiz
                action_type = "TYPE"
            else:
                self.log_action("CLICK", category, details, element)
                try:
                    element.click()
                except:
                    self.driver.execute_script("arguments[0].click();", element)
                self.last_interaction = {"id": el_id, "action": "CLICK"}
                action_type = "CLICK"
            
            # 📊 Reporter'a başarıyı kaydet
            interact_duration = time.time() - interact_start_time
            if self.reporter:
                self.reporter.log_interaction(
                    action_type=action_type,
                    category=category,
                    element_info={"id": el_id, "class": el_class, "tag": el_tag},
                    score=winner_data['score'],
                    success=True,
                    duration=interact_duration
                )
            
            # 🧠 Başarılı etkileşimi öğren
            # 🆕 SEARCH SONRASI STALE ELEMENT KORUNUYOR
            try:
                site_name = self._extract_site_name(self.driver.current_url)
                element_text = element.text[:50] if category != "search" else ""
            except:
                site_name = "unknown"
                element_text = ""
            
            self.learning.learn_success(
                site=site_name,
                action_type=action_type,
                category=category,
                element_info={"id": el_id, "class": el_class, "tag": el_tag, "text": element_text},
                score=winner_data['score']
            )
            
            # 📸 AUTO-CAPTURE: %70-95 güvenli elementleri kaydet
            # Visual score (V değeri) kullan - bu model'in katkısı
            try:
                visual_score = winner_data.get('visual_score', 0)
                if self.auto_capture.should_capture(visual_score, category):
                    self.auto_capture.capture_element(
                        element=element,
                        category=category,
                        site_name=site_name,
                        confidence_score=visual_score
                    )
            except Exception as e:
                # Sessizce başarısız ol - ana işlemi bozma
                pass
            
            return True
        except Exception as e:
            print(f"❌ Etkileşim Hatası: {e}")
            
            # 📊 Reporter'a hata kaydet
            interact_duration = time.time() - interact_start_time
            if self.reporter:
                self.reporter.log_interaction(
                    action_type="FAILED",
                    category=category,
                    element_info={"id": el_id, "class": el_class, "tag": el_tag},
                    score=winner_data['score'],
                    success=False,
                    duration=interact_duration
                )
                self.reporter.log_error(
                    error_type="InteractionError",
                    message=str(e),
                    element_info={"id": el_id, "class": el_class, "tag": el_tag}
                )
            
            return False

    def smart_scroll(self, direction="down", distance=500, smooth=True):
        """
        🔍 SMART SCROLL - Akıllı Sayfa Kaydırma
        
        Args:
            direction: "down", "up", "bottom", "top"
            distance: Kaydırma mesafesi (px)
            smooth: Yumuşak scroll (true) veya anlık (false)
        """
        if direction == "down":
            if smooth:
                # Yumuşak scroll (lazy-load için daha iyi)
                self.driver.execute_script(f"window.scrollBy({{top: {distance}, behavior: 'smooth'}});")
            else:
                self.driver.execute_script(f"window.scrollBy(0, {distance});")
        
        elif direction == "up":
            if smooth:
                self.driver.execute_script(f"window.scrollBy({{top: -{distance}, behavior: 'smooth'}});")
            else:
                self.driver.execute_script(f"window.scrollBy(0, -{distance});")
        
        elif direction == "bottom":
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        elif direction == "top":
            self.driver.execute_script("window.scrollTo(0, 0);")
        
        time.sleep(0.5)  # Lazy-load için bekleme
    
    def scroll_until_element_visible(self, element, max_scrolls=10):
        """
        Element görünür hale gelene kadar scroll et
        
        Args:
            element: WebElement
            max_scrolls: Maksimum scroll sayısı
        
        Returns:
            bool: Element görünür hale geldi mi?
        """
        for i in range(max_scrolls):
            try:
                if element.is_displayed():
                    print(f"   ✅ Element {i} scroll sonra görünür hale geldi!")
                    return True
            except:
                pass
            
            self.smart_scroll(direction="down", distance=300, smooth=True)
        
        print(f"   ❌ Element {max_scrolls} scroll sonra hala görünmüyor!")
        return False
    
    def progressive_scroll_and_scan(self, category, target_text=None, scroll_steps=5):
        """
        🔍 PROGRESİF TARAMA - Sayfa scroll ederek element ara
        
        Lazy-load sayfalar için: Her scroll'da yeni elementler yüklenir,
        bu yüzden her scroll'da tekrar tarama yap.
        
        Args:
            category: Element kategorisi
            target_text: Hedef metin
            scroll_steps: Kaç adımda scroll edilecek
        
        Returns:
            WebElement veya None
        """
        print(f"\n🔍 Progresif Tarama Başlıyor: '{category}' için sayfa scroll edilecek...")
        
        # Önce mevcut görünümde ara
        result = self.scan_and_decide(category, target_text)
        if result:
            print("   ✅ Element ilk ekranda bulundu!")
            return result
        
        # Scroll ederek ara
        for step in range(1, scroll_steps + 1):
            print(f"   📜 Scroll adımı {step}/{scroll_steps}...")
            self.smart_scroll(direction="down", distance=500, smooth=True)
            time.sleep(1)  # Lazy-load için bekleme
            
            # Yeniden tara
            result = self.scan_and_decide(category, target_text)
            if result:
                print(f"   ✅ Element {step}. scroll'da bulundu!")
                return result
        
        print(f"   ❌ Element {scroll_steps} scroll sonra da bulunamadı!")
        return None
    
    def select_random_product(self, use_progressive_scan=False):
        print("\\n🤖 Analiz Başlıyor: 'Ürün Listesi' taranıyor...")
        
        # 🆕 SAYFA YÜKLENMESİNİ BEKLE
        time.sleep(2)  # Arama sonuçlarının yüklenmesi için
        
        try:
            # 🆕 GENİŞLETİLMİŞ ÜRÜN XPATH'LERİ
            # N11 arama sonuçları dahil
            product_xpaths = [
                # 🆕 N11 ARAMA SONUÇLARI SAYFASI
                "//div[contains(@class, 'search-result')]//a[contains(@href, '/urun/')]",
                "//ul[contains(@class, 'search-result')]//a[contains(@href, '/urun/')]",
                "//div[contains(@class, 'resultList')]//a[contains(@href, '/urun/')]",
                "//li[contains(@class, 'result')]//a[contains(@href, '/urun/')]",
                # N11 ana sayfa yapısı
                "//div[contains(@class, 'columnContent')]//a[contains(@href, '/urun/')]",
                "//li[contains(@class, 'productItem')]//a",
                "//div[contains(@class, 'productItem')]//a",
                # Genel e-ticaret yapısı
                "//div[contains(@class, 'product')]//a[contains(@href, '/')]",
                "//a[contains(@class, 'plink')]",
                "//a[contains(@class, 'product-link')]",
                "//a[contains(@class, 'card')]//parent::*//a",
                # 🆕 N11 genel - en geniş
                "//a[contains(@href, '/urun/')]",
                # Trendyol yapısı
                "//div[contains(@class, 'p-card')]//a",
                # Hepsiburada yapısı
                "//li[contains(@class, 'productListContent')]//a",
                # Fallback - daha genel
                "//li//a[contains(@href, 'html')]",
                "//div[contains(@class, 'product')]//a"
            ]
            
            combined_xpath = " | ".join(product_xpaths)
            
            if use_progressive_scan:
                # Progresif tarama ile daha fazla ürün bul
                all_products = []
                for i in range(3):  # 3 scroll yap
                    products = self.driver.find_elements(By.XPATH, combined_xpath)
                    all_products.extend(products)
                    self.smart_scroll(direction="down", distance=500, smooth=True)
                    time.sleep(1)
                
                potential_products = list(set(all_products))  # Duplicate'leri kaldır
            else:
                potential_products = self.driver.find_elements(By.XPATH, combined_xpath)
            
            print(f"   ℹ️ {len(potential_products)} potansiyel ürün bulundu.")
            
            # Debug: İlk 3 ürünün href'ini göster
            if potential_products:
                print(f"   🔍 Debug - İlk 3 ürün href'leri:")
                for idx, p in enumerate(potential_products[:3]):
                    try:
                        href = p.get_attribute('href') or "N/A"
                        print(f"      #{idx+1}: {href[:80]}...")
                    except:
                        pass
            
            valid_products = []
            for p in potential_products:
                try:
                    if p.is_displayed() and p.size['height'] > 50 and p.size['width'] > 50:
                        # Ürün linki mi kontrol et - daha gevşek kontrol
                        href = p.get_attribute('href') or ""
                        # N11 ürün linkleri: /urun/, -p-, .html veya herhangi bir / içeren
                        if href and len(href) > 20 and ('/' in href):
                            valid_products.append(p)
                except:
                    continue
            
            if not valid_products:
                print("❌ Hiç ürün bulunamadı.")
                return False
                
            print(f"   ✅ {len(valid_products)} geçerli ürün bulundu.")
            target = random.choice(valid_products[:10])  # İlk 10'dan seç
            
            # Element'i görünür hale getir
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
            time.sleep(0.5)
            
            # 🆕 OVERLAY KAPAT (N11 popup sorunu)
            try:
                overlays = self.driver.find_elements(By.CSS_SELECTOR, ".overlay, .modal, .popup, [class*='overlay']")
                for overlay in overlays:
                    try:
                        if overlay.is_displayed():
                            self.driver.execute_script("arguments[0].style.display='none';", overlay)
                            print("   🧹 Overlay gizlendi.")
                    except:
                        pass
            except:
                pass
            
            print(f"   🎲 Rastgele bir ürün seçildi.")
            self.log_action("CLICK", "product_select", "Rastgele Ürün Seçimi", target)
            
            # 🆕 TARGET=_BLANK VARSA KALDIR (AYNI SEKMEDE AÇ)
            try:
                target_attr = target.get_attribute("target")
                if target_attr == "_blank":
                    self.driver.execute_script("arguments[0].removeAttribute('target');", target)
                    print("   🔧 target=_blank kaldırıldı (aynı sekmede açılacak)")
            except:
                pass
            
            # Mevcut URL'yi kaydet
            old_url = self.driver.current_url
            old_handles = self.driver.window_handles
            
            # 🆕 ÖNCE NORMAL CLICK DENE, BAŞARISIZ OLURSA JS CLICK
            try:
                target.click()
            except Exception as click_err:
                if "intercepted" in str(click_err).lower():
                    print("   ⚠️ Click intercepted, JavaScript click deneniyor...")
                    self.driver.execute_script("arguments[0].click();", target)
                else:
                    raise click_err
            
            time.sleep(2)
            
            # 🆕 YENİ SEKME KONTROLÜ
            new_handles = self.driver.window_handles
            if len(new_handles) > len(old_handles):
                # Yeni sekme açıldı, ona geç
                new_tab = [h for h in new_handles if h not in old_handles][0]
                self.driver.switch_to.window(new_tab)
                print("   🔀 Yeni sekmeye geçildi")
            
            # URL değişti mi kontrol et
            new_url = self.driver.current_url
            if new_url == old_url or "/arama" in new_url:
                # URL değişmedi veya hala arama sayfasındayız
                # Ürün linkini direkt ziyaret et
                href = target.get_attribute("href")
                if href and "/urun/" in href:
                    print(f"   🔗 Direkt URL'ye gidiliyor: {href[:60]}...")
                    self.driver.get(href)
                    time.sleep(2)
            
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Ürün seçimi hatası: {e}")
            return False

    def hybrid_click(self, selectors, target_text="Button", use_recovery=True):
        if selectors:
            print("   ⚡ Legacy Katmanı: Hızlı element arama başladı...")
            for by_method, value in selectors:
                try:
                    element = self.driver.find_element(by_method, value)
                    if element.is_displayed():
                        element.click()
                        print(f"   ✅ Başarılı! (Klasik Yöntem: {value})")
                        return True
                except:
                    continue
        print(f"   ⚠️ Klasik yöntemler başarısız! SmartBot devreye giriyor...")
        
        # 🆕 AKILLI KATEGORİ TESPİTİ
        category = self.auto_detect_category(target_text)
        if category != "button":
            print(f"   🎯 Akıllı Tespit: '{target_text}' → Kategori: '{category}'")
        
        # AI ile dene
        success = self.interact(category, target_text=target_text)
        
        # 🔄 Başarısız olursa ve recovery aktifse alternatif yolları dene
        if not success and use_recovery and category in ["cart", "add_to_cart", "login", "checkout"]:
            print(f"\n🔄 Recovery Manager devreye giriyor...")
            
            context = {
                "driver": self.driver,
                "bot": self,
                "site_url": self.driver.current_url
            }
            
            def primary_action():
                return False  # AI zaten denedi ve başarısız oldu
            
            success = self.recovery.attempt_with_recovery(category, primary_action, context)
        
        return success

    def hybrid_type(self, selectors, text, category="email", use_recovery=True):
        if selectors:
            print("   ⚡ Legacy Katmanı: Input alanı aranıyor...")
            for by_method, value in selectors:
                try:
                    element = self.driver.find_element(by_method, value)
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(text)
                        print(f"   ✅ Başarılı! (Klasik Yöntem: {value})")
                        return True
                except:
                    continue
        
        print(f"   ⚠️ Input bulunamadı! SmartBot devreye giriyor...")
        
        # 🆕 Hint için daha iyi isimlendirme
        hint_map = {
            "email": "E-Posta",
            "password": "Şifre",
            "search": "Ara",
            "text_input": "Metin",
            "firstName": "İsim",
            "lastName": "Soyisim",
            "phone": "Telefon"
        }
        hint = hint_map.get(category, category.capitalize())
        
        # AI ile dene
        success = self.interact(category, text=text, target_text=hint)
        
        # 🔄 Search için özel recovery
        if not success and use_recovery and category == "search":
            print(f"\n🔄 Recovery Manager devreye giriyor (Search)...")
            
            context = {
                "driver": self.driver,
                "bot": self,
                "search_term": text
            }
            
            def primary_action():
                return False  # AI zaten denedi ve başarısız oldu
            
            success = self.recovery.attempt_with_recovery("search", primary_action, context)
        
        return success
