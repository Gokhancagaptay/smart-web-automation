# mega_site_test.py
"""
🌐 MEGA MULTI-SITE AI TEST v2.0
10 E-Ticaret sitesinde AI modelini test et
Sorunlu siteler kaldırıldı, stabil siteler eklendi
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from smart_bot import SmartBot
from test_reporter import TestReporter
from datetime import datetime
import json

# ✅ TEST SİTELERİ (Stabil ve çalışan siteler)
SITES = [
    {
        "name": "N11",
        "url": "https://www.n11.com",
        "search_term": "kulaklık",
        "timeout": 15
    },
    {
        "name": "Hepsiburada",
        "url": "https://www.hepsiburada.com",
        "search_term": "telefon kılıfı",
        "timeout": 20
    },
    {
        "name": "Trendyol", 
        "url": "https://www.trendyol.com",
        "search_term": "çanta",
        "timeout": 20
    },
    {
        "name": "Çiçeksepeti",
        "url": "https://www.ciceksepeti.com",
        "search_term": "gül buketi",
        "timeout": 15
    },
    {
        "name": "Amazon TR",
        "url": "https://www.amazon.com.tr",
        "search_term": "powerbank",
        "timeout": 15
    },
    {
        "name": "Kitapsepeti",
        "url": "https://www.kitapsepeti.com",
        "search_term": "roman",
        "timeout": 15
    },
    {
        "name": "Teknosa",
        "url": "https://www.teknosa.com",
        "search_term": "kulaklık",
        "timeout": 20
    },
    {
        "name": "Vatanbilgisayar",
        "url": "https://www.vatanbilgisayar.com",
        "search_term": "mouse",
        "timeout": 15
    },
    {
        "name": "Gratis",
        "url": "https://www.gratis.com",
        "search_term": "parfüm",
        "timeout": 15
    },
    {
        "name": "Decathlon",
        "url": "https://www.decathlon.com.tr",
        "search_term": "bisiklet",
        "timeout": 20
    },
    {
        "name": "Watsons",
        "url": "https://www.watsons.com.tr",
        "search_term": "şampuan",
        "timeout": 15
    }
]

def close_popups(driver):
    """Tüm pop-up ve modal'ları kapat"""
    try:
        driver.execute_script("""
            // Modal ve popup kapatma
            var closeSelectors = [
                '[class*="close"]', '[class*="Close"]', '[id*="close"]', '[id*="Close"]',
                '[class*="modal"] button', '[class*="popup"] button',
                '[aria-label*="kapat"]', '[aria-label*="close"]',
                '[class*="cookie"] button', '[class*="consent"] button',
                '[class*="notification"] [class*="close"]',
                '.modal-close', '.popup-close', '.btn-close',
                '[data-dismiss="modal"]', '[data-testid*="close"]'
            ];
            
            closeSelectors.forEach(function(selector) {
                try {
                    var elements = document.querySelectorAll(selector);
                    elements.forEach(function(el) {
                        if (el.offsetParent !== null) {
                            el.click();
                        }
                    });
                } catch(e) {}
            });
            
            // Overlay gizle
            var overlays = document.querySelectorAll('[class*="overlay"], [class*="modal-backdrop"]');
            overlays.forEach(function(el) {
                el.style.display = 'none';
            });
        """)
    except:
        pass

def test_site(site_config, site_index, total_sites):
    """Tek bir siteyi test et"""
    name = site_config["name"]
    url = site_config["url"]
    search_term = site_config["search_term"]
    timeout = site_config.get("timeout", 15)
    
    print(f"\n{'='*70}")
    print(f"🛒 [{site_index}/{total_sites}] {name.upper()} AI TEST")
    print(f"{'='*70}")
    
    reporter = TestReporter(f"{name.lower().replace(' ', '_')}_ai_test")
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    results = {
        "site": name,
        "url": url,
        "search": False,
        "product_select": False,
        "add_to_cart": False,
        "cart": False,
        "duration": 0,
        "error": None
    }
    
    start_time = time.time()
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(30)
        
        bot = SmartBot(driver, reporter=reporter)
        
        # 1. Anasayfa
        print(f"\n🌍 1. {name} Anasayfasına Gidiliyor...")
        try:
            driver.get(url)
            bot.smart_wait("page_ready", timeout=timeout)
        except Exception as e:
            print(f"   ⚠️ Sayfa yükleme sorunu: {str(e)[:50]}")
            # Yine de devam et
        
        # Pop-up kapat
        time.sleep(2)
        close_popups(driver)
        time.sleep(1)
        
        # 2. Arama
        print(f"\n🔍 2. Ürün Aranıyor: {search_term}...")
        try:
            if bot.interact("search", text=search_term, target_text="Ara"):
                print("   ✅ Arama yapıldı")
                results["search"] = True
            else:
                print("   ❌ Arama başarısız")
        except Exception as e:
            print(f"   ❌ Arama hatası: {str(e)[:50]}")
        
        time.sleep(3)
        close_popups(driver)
        
        # 3. Ürün seç
        print("\n🎲 3. Rastgele Ürün Seçiliyor...")
        try:
            if bot.select_random_product():
                print("   ✅ Ürün seçildi")
                results["product_select"] = True
            else:
                print("   ❌ Ürün seçilemedi")
        except Exception as e:
            print(f"   ❌ Ürün seçme hatası: {str(e)[:50]}")
        
        time.sleep(3)
        close_popups(driver)
        
        # 4. Sepete ekle
        print("\n🛒 4. Sepete Ekleniyor...")
        try:
            if bot.interact("add_to_cart", target_text="Sepete Ekle"):
                print("   ✅ Sepete eklendi")
                results["add_to_cart"] = True
            else:
                # Alternatif hedefler dene
                alt_targets = ["Sepete At", "Add to Cart", "Satın Al", "Ekle"]
                for alt in alt_targets:
                    if bot.interact("add_to_cart", target_text=alt):
                        print(f"   ✅ Sepete eklendi ('{alt}' ile)")
                        results["add_to_cart"] = True
                        break
                if not results["add_to_cart"]:
                    print("   ❌ Sepete eklenemedi")
        except Exception as e:
            print(f"   ❌ Sepete ekleme hatası: {str(e)[:50]}")
        
        time.sleep(2)
        
        # 5. Sepete git
        print("\n🛍️ 5. Sepete Gidiliyor...")
        try:
            if bot.interact("cart", target_text="Sepetim"):
                print("   ✅ Sepete gidildi")
                results["cart"] = True
            else:
                # Alternatif hedefler
                alt_targets = ["Sepet", "Sepetim", "Cart", "Basket"]
                for alt in alt_targets:
                    if bot.interact("cart", target_text=alt):
                        print(f"   ✅ Sepete gidildi ('{alt}' ile)")
                        results["cart"] = True
                        break
                if not results["cart"]:
                    print("   ❌ Sepete gidilemedi")
        except Exception as e:
            print(f"   ❌ Sepet hatası: {str(e)[:50]}")
        
        print(f"\n✅ {name} TESTİ TAMAMLANDI!")
        
    except Exception as e:
        error_msg = str(e)[:200]
        print(f"\n❌ Test Hatası: {error_msg[:100]}")
        results["error"] = error_msg
    
    finally:
        results["duration"] = round(time.time() - start_time, 2)
        
        # Driver kapat
        if driver:
            try:
                driver.quit()
            except:
                pass
        
        # Rapor
        try:
            reporter.generate_report()
        except:
            pass
    
    return results

def print_summary(all_results):
    """Sonuç özeti yazdır"""
    total_sites = len(all_results)
    
    # İstatistikler
    search_success = sum(1 for r in all_results if r["search"])
    product_success = sum(1 for r in all_results if r["product_select"])
    cart_add_success = sum(1 for r in all_results if r["add_to_cart"])
    cart_success = sum(1 for r in all_results if r["cart"])
    
    total_steps = total_sites * 4
    successful_steps = search_success + product_success + cart_add_success + cart_success
    overall_success = (successful_steps / total_steps) * 100 if total_steps > 0 else 0
    
    print(f"\n\n{'='*70}")
    print("� MEGA TEST GENEL ÖZETİ")
    print("="*70)
    
    print(f"\n�📈 GENEL BAŞARI: {overall_success:.1f}%")
    print(f"   ├─ Search: {search_success}/{total_sites} ({search_success/total_sites*100:.0f}%)")
    print(f"   ├─ Product Select: {product_success}/{total_sites} ({product_success/total_sites*100:.0f}%)")
    print(f"   ├─ Add to Cart: {cart_add_success}/{total_sites} ({cart_add_success/total_sites*100:.0f}%)")
    print(f"   └─ Cart: {cart_success}/{total_sites} ({cart_success/total_sites*100:.0f}%)")
    
    print(f"\n📋 SİTE BAZLI SONUÇLAR:")
    print(f"{'Site':<20} {'Search':^8} {'Product':^8} {'AddCart':^8} {'Cart':^8} {'Süre':^8} {'Başarı':^8}")
    print("-" * 76)
    
    for r in all_results:
        s = "✅" if r["search"] else "❌"
        p = "✅" if r["product_select"] else "❌"
        a = "✅" if r["add_to_cart"] else "❌"
        c = "✅" if r["cart"] else "❌"
        success = sum([r["search"], r["product_select"], r["add_to_cart"], r["cart"]]) / 4 * 100
        print(f"{r['site']:<20} {s:^8} {p:^8} {a:^8} {c:^8} {r['duration']:>6.1f}s {success:>6.0f}%")
    
    # Başarılı/Başarısız site sayısı
    good_sites = sum(1 for r in all_results if sum([r["search"], r["product_select"], r["add_to_cart"], r["cart"]]) >= 2)
    print(f"\n✅ Başarılı Siteler (≥%50): {good_sites}/{total_sites}")
    print(f"❌ Başarısız Siteler (<50%): {total_sites - good_sites}/{total_sites}")
    
    return overall_success

def main():
    print("\n" + "="*70)
    print("🌐 MEGA MULTI-SITE AI MODEL PERFORMANCE TEST v2.0")
    print("="*70)
    print(f"📅 Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Test Edilecek Site Sayısı: {len(SITES)}")
    print("="*70)
    
    print("\n📋 Test Edilecek Siteler:")
    for i, site in enumerate(SITES, 1):
        print(f"   {i}. {site['name']} ({site['url']})")
    
    all_results = []
    total_sites = len(SITES)
    
    for i, site in enumerate(SITES, 1):
        print(f"\n\n{'#'*70}")
        print(f"# TEST {i}/{total_sites}: {site['name']}")
        print(f"{'#'*70}")
        
        result = test_site(site, i, total_sites)
        all_results.append(result)
        
        # Kısa özet
        success_count = sum([result["search"], result["product_select"], result["add_to_cart"], result["cart"]])
        success_rate = (success_count / 4) * 100
        status = "✅" if success_rate >= 50 else "❌"
        print(f"\n{status} {site['name']}: {success_rate:.0f}% ({success_count}/4 adım)")
        
        # Testler arası bekleme
        if i < total_sites:
            print("\n⏳ Bir sonraki test için 3 saniye bekleniyor...")
            time.sleep(3)
    
    # GENEL ÖZET
    overall_success = print_summary(all_results)
    
    # JSON rapor
    report_file = f"mega_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "version": "2.0",
            "total_sites": total_sites,
            "overall_success_rate": overall_success,
            "step_success": {
                "search": sum(1 for r in all_results if r["search"]),
                "product_select": sum(1 for r in all_results if r["product_select"]),
                "add_to_cart": sum(1 for r in all_results if r["add_to_cart"]),
                "cart": sum(1 for r in all_results if r["cart"])
            },
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detaylı rapor: {report_file}")
    print("="*70)
    
    return overall_success

if __name__ == "__main__":
    success_rate = main()
    print(f"\n🎯 Test tamamlandı! Genel başarı: {success_rate:.1f}%")
