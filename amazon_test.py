# amazon_test.py
"""
🛒 AMAZON.TR ALIŞVERIŞ TESTİ
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
    print("🛒 AMAZON.TR AI TEST (Pure AI - No IDs)")
    print("="*70)
    
    # Reporter
    reporter = TestReporter("amazon_ai_test")
    
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
        print("\n🌍 1. Amazon.tr Anasayfasına Gidiliyor...")
        driver.get("https://www.amazon.com.tr")
        bot.smart_wait("page_ready", timeout=10)
        
        # Pop-up/Cookie kapat
        try:
            time.sleep(2)
            driver.execute_script("""
                var cookie = document.querySelector('[id*="cookie"], [class*="cookie"]');
                if (cookie) cookie.click();
            """)
        except:
            pass
        
        # 2. Ürün arama (giriş yapmadan)
        print("\n🔍 2. Ürün Aranıyor: mouse...")
        if bot.interact("search", text="mouse", target_text="Ara"):
            print("   ✅ Arama yapıldı")
        
        time.sleep(3)
        
        # 3. Rastgele ürün seç
        print("\n🎲 3. Listeden Rastgele Ürün Seçiliyor...")
        if bot.select_random_product():
            print("   ✅ Ürün seçildi")
        
        time.sleep(3)
        
        # 4. Sepete ekle
        print("\n🛒 4. Sepete Ekleniyor...")
        if bot.interact("add_to_cart", target_text="Sepete Ekle"):
            print("   ✅ Sepete eklendi")
        
        time.sleep(2)
        
        # 5. Sepete git
        print("\n🛍️ 5. Sepete Gidiliyor...")
        if bot.interact("cart", target_text="Sepet"):
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
