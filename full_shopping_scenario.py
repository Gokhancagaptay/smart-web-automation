# full_shopping_scenario.py
"""
🛒 N11 TAM ALIŞVERİŞ SENARYOSU
Hibrit AI Test - E2E Shopping Flow
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from smart_bot import SmartBot
from test_reporter import TestReporter
import config

# --- KULLANICI BİLGİLERİ ---
EMAIL = "test@example.com"
PASSWORD = "TestPassword123"
PRODUCT_TO_SEARCH = "kalem"
SITE_URL = "https://www.n11.com"  # 🆕 Değiştirilebilir: n11.com, trendyol.com, hepsiburada.com

def main():
    print("\n" + "="*70)
    print("🚀 N11 HİBRİT TEST (İLK TIKLAMA ID, GERİSİ AI)")
    print("="*70)
    
    # Test Reporter başlat
    reporter = TestReporter("n11_full_shopping")
    
    # Tarayıcı ayarları
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    bot = SmartBot(driver, reporter=reporter)
    
    try:
        # 1. Anasayfa
        print("\n🌍 1. N11 Anasayfasına Gidiliyor...")
        driver.get(SITE_URL)
        bot.smart_wait("page_ready", timeout=10)
        bot.close_popups()
        
        # 2. Giriş Yap
        print("\n🔐 2. Giriş Yapılıyor...")
        driver.get("https://www.n11.com/giris-yap")
        bot.smart_wait("page_ready", timeout=10)
        
        # Email
        print("   📧 AI E-posta kutusunu arıyor...")
        if bot.interact("email", text=EMAIL, target_text="E-Posta"):
            print(f"   ✅ Email girildi: {EMAIL}")
        else:
            print("   ❌ Email girilemedi!")
            
        # Giriş butonu (şifre alanını açmak için)
        print("   🔘 AI 'Giriş Yap' butonuna tıklıyor (şifre alanını açmak için)...")
        if bot.interact("button", target_text="Giriş Yap"):
            time.sleep(1)
        
        # Şifre
        print("   🔑 AI Şifre kutusunu arıyor...")
        if bot.interact("password", text=PASSWORD, target_text="Şifre"):
            print("   ✅ Şifre girildi")
        else:
            print("   ❌ Şifre girilemedi!")
            
        # Giriş butonu (giriş yapmak için)
        print("   🔘 AI 'Giriş Yap' butonuna tıklıyor (giriş yapılıyor)...")
        if bot.interact("button", target_text="Giriş Yap"):
            print("   ⏳ Giriş sonrası bekleniyor...")
            time.sleep(3)
            
            # Giriş başarılı mı kontrol et
            current_url = driver.current_url
            if "giris-yap" not in current_url:
                print(f"   ✅ Giriş başarılı! Yönlendirilen sayfa: {current_url}")
                # Cache temizle (yeni sayfa için)
                bot.element_cache = {}
                print("   🧹 Element cache temizlendi (yeni sayfa için)")
            else:
                print("   ⚠️ Giriş yapılamadı, devam ediliyor...")
        
        # 3. Anasayfaya git
        print("\n🏠 Anasayfaya gidiliyor...")
        driver.get(SITE_URL)
        bot.smart_wait("page_ready", timeout=10)
        
        # 4. Ürün Ara
        print(f"\n🔍 3. Ürün Aranıyor: {PRODUCT_TO_SEARCH}...")
        if bot.interact("search", text=PRODUCT_TO_SEARCH, target_text="Ara"):
            print(f"   ✅ '{PRODUCT_TO_SEARCH}' arandı")
            # Enter tuşuna bas
            from selenium.webdriver.common.keys import Keys
            driver.switch_to.active_element.send_keys(Keys.RETURN)
            print("   ↵ Enter tuşuna basıldı.")
            bot.smart_wait("page_ready", timeout=10)
        else:
            print("   ❌ Arama yapılamadı!")
        
        # 5. Rastgele Ürün Seç
        print("\n🎲 4. Listeden Rastgele Ürün Seçiliyor...")
        if bot.select_random_product():
            print("   ✅ Ürün seçildi")
            bot.smart_wait("page_ready", timeout=10)
        else:
            print("   ❌ Ürün seçilemedi!")
        
        # 6. Sepete Ekle
        print("\n🛒 5. Sepete Ekleniyor...")
        if bot.interact("add_to_cart", target_text="Sepete Ekle"):
            print("   ✅ Sepete eklendi")
            time.sleep(2)
        else:
            print("   ❌ Sepete eklenemedi!")
        
        # 7. Sepete Git
        print("\n🛍️ 6. Sepete Gidiliyor...")
        if bot.interact("cart", target_text="Sepetim"):
            print("   ✅ Sepete gidildi")
            bot.smart_wait("page_ready", timeout=10)
        else:
            print("   ❌ Sepete gidilemedi!")
        
        # 8. Checkout
        print("\n💳 7. Ödeme Adımına Geçiliyor (Checkout)...")
        if bot.interact("checkout", target_text="Alışverişi Tamamla"):
            print("   ✅ Checkout sayfasına gidildi")
            bot.smart_wait("page_ready", timeout=5)
        else:
            print("   ❌ Checkout'a gidilemedi!")
        
        # 9. Son Adım - Ödeme Onayı
        print("\n🏁 8. Son Ödeme Onayı...")
        if bot.interact("checkout", target_text="Ödeme Yap"):
            print("   ✅ Ödeme sayfası açıldı")
        else:
            print("   ⚠️ Ödeme butonu bulunamadı (giriş yapılmamış olabilir)")
        
        print("\n✅ SENARYO TAMAMLANDI!")
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🛑 Test bitti.")
        print("\n📊 Rapor oluşturuluyor...")
        reporter.generate_report()
        
        # Learning System özeti
        if hasattr(bot, 'learning'):
            bot.learning.print_session_summary()
        
        driver.quit()
        print("\n✨ Test tamamlandı! Raporları inceleyebilirsin.")

if __name__ == "__main__":
    main()
