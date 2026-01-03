# hepsiburada_test.py
"""
🛒 HEPSİBURADA ALIŞVERIŞ TESTİ
Model performansını test et - kırılgan (ID/Class kullanmadan)
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from smart_bot import SmartBot
from test_reporter import TestReporter
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("\n" + "="*70)
    print("🛒 HEPSİBURADA AI TEST (Pure AI - No IDs)")
    print("="*70)
    
    # Reporter
    reporter = TestReporter("hepsiburada_ai_test")
    
    # Chrome ayarları
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
        print("\n🌍 1. Hepsiburada Anasayfasına Gidiliyor...")
        driver.get("https://www.hepsiburada.com")
        bot.smart_wait("page_ready", timeout=10)
        
        # 2. Giriş
        print("\n🔐 2. Giriş Yapılıyor...")
        
        # Pop-up kapat
        try:
            time.sleep(2)
            driver.execute_script("""
                var close = document.querySelector('[id*="close"], [class*="modal-close"]');
                if (close) close.click();
            """)
        except:
            pass
        
        # Giriş sayfasına git
        driver.get("https://www.hepsiburada.com/uye-girisi")  # Doğru URL
        bot.smart_wait("page_ready", timeout=10)
        
        # Email
        email = os.getenv("HEPSIBURADA_EMAIL", "test@example.com")
        if bot.interact("email", text=email, target_text="E-Posta"):
            print("   ✅ Email girildi")
        
        time.sleep(1)
        
        # Password
        password = os.getenv("HEPSIBURADA_PASSWORD", "testpass123")
        if bot.interact("password", text=password, target_text="Şifre"):
            print("   ✅ Şifre girildi")
        
        time.sleep(1)
        
        # Giriş yap butonu
        if bot.interact("button", target_text="Giriş Yap"):
            print("   ✅ Giriş yapıldı")
        
        time.sleep(3)
        
        # 3. Ürün arama
        print("\n🔍 3. Ürün Aranıyor: telefon...")
        driver.get("https://www.hepsiburada.com")
        bot.smart_wait("page_ready", timeout=10)
        
        if bot.interact("search", text="telefon", target_text="Ara"):
            print("   ✅ Arama yapıldı")
        
        time.sleep(3)
        
        # 4. Rastgele ürün seç
        print("\n🎲 4. Listeden Rastgele Ürün Seçiliyor...")
        if bot.select_random_product():
            print("   ✅ Ürün seçildi")
        
        time.sleep(3)
        
        # 5. Sepete ekle
        print("\n🛒 5. Sepete Ekleniyor...")
        if bot.interact("add_to_cart", target_text="Sepete Ekle"):
            print("   ✅ Sepete eklendi")
        
        time.sleep(2)
        
        # 6. Sepete git
        print("\n🛍️ 6. Sepete Gidiliyor...")
        if bot.interact("cart", target_text="Sepetim"):
            print("   ✅ Sepete gidildi")
        
        time.sleep(2)
        
        print("\n✅ TEST TAMAMLANDI!")
        
    except Exception as e:
        print(f"\n❌ Test Hatası: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🛑 Test bitti.")
        driver.quit()
        
        # Rapor
        reporter.generate_report()
        
        # Learning özet
        bot.learning.save_and_report()

if __name__ == "__main__":
    main()
