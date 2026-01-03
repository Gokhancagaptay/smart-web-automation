# mega_site_test.py
"""
🌐 MEGA MULTI-SITE AI TEST
10+ E-Ticaret sitesinde AI modelini test et
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from smart_bot import SmartBot
from test_reporter import TestReporter
from datetime import datetime
import json

# TEST SİTELERİ
SITES = [
    {
        "name": "N11",
        "url": "https://www.n11.com",
        "search_term": "kulaklık"
    },
    {
        "name": "Trendyol", 
        "url": "https://www.trendyol.com",
        "search_term": "telefon kılıfı"
    },
    {
        "name": "Çiçeksepeti",
        "url": "https://www.ciceksepeti.com",
        "search_term": "gül"
    },
    {
        "name": "GittiGidiyor",
        "url": "https://www.gittigidiyor.com",
        "search_term": "laptop"
    },
    {
        "name": "Morhipo",
        "url": "https://www.morhipo.com",
        "search_term": "elbise"
    },
    {
        "name": "Boyner",
        "url": "https://www.boyner.com.tr",
        "search_term": "ayakkabı"
    },
    {
        "name": "Koton",
        "url": "https://www.koton.com",
        "search_term": "tişört"
    },
    {
        "name": "LC Waikiki",
        "url": "https://www.lcwaikiki.com/tr-TR",
        "search_term": "pantolon"
    },
    {
        "name": "Decathlon",
        "url": "https://www.decathlon.com.tr",
        "search_term": "bisiklet"
    },
    {
        "name": "MediaMarkt",
        "url": "https://www.mediamarkt.com.tr",
        "search_term": "tablet"
    }
]

def test_site(site_config):
    """Tek bir siteyi test et"""
    name = site_config["name"]
    url = site_config["url"]
    search_term = site_config["search_term"]
    
    print(f"\n{'='*70}")
    print(f"🛒 {name.upper()} AI TEST")
    print(f"{'='*70}")
    
    reporter = TestReporter(f"{name.lower()}_ai_test")
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    bot = SmartBot(driver, reporter=reporter)
    
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
        # 1. Anasayfa
        print(f"\n🌍 1. {name} Anasayfasına Gidiliyor...")
        driver.get(url)
        bot.smart_wait("page_ready", timeout=15)
        
        # Pop-up kapat
        try:
            time.sleep(2)
            driver.execute_script("""
                var modals = document.querySelectorAll('[class*="modal"], [class*="popup"], [class*="close"], [id*="close"]');
                modals.forEach(m => { try { m.click(); } catch(e) {} });
            """)
        except:
            pass
        
        # 2. Arama
        print(f"\n🔍 2. Ürün Aranıyor: {search_term}...")
        if bot.interact("search", text=search_term, target_text="Ara"):
            print("   ✅ Arama yapıldı")
            results["search"] = True
        else:
            print("   ❌ Arama başarısız")
        
        time.sleep(3)
        
        # 3. Ürün seç
        print("\n🎲 3. Rastgele Ürün Seçiliyor...")
        if bot.select_random_product():
            print("   ✅ Ürün seçildi")
            results["product_select"] = True
        else:
            print("   ❌ Ürün seçilemedi")
        
        time.sleep(3)
        
        # 4. Sepete ekle
        print("\n🛒 4. Sepete Ekleniyor...")
        if bot.interact("add_to_cart", target_text="Sepete Ekle"):
            print("   ✅ Sepete eklendi")
            results["add_to_cart"] = True
        else:
            print("   ❌ Sepete eklenemedi")
        
        time.sleep(2)
        
        # 5. Sepete git
        print("\n🛍️ 5. Sepete Gidiliyor...")
        if bot.interact("cart", target_text="Sepet"):
            print("   ✅ Sepete gidildi")
            results["cart"] = True
        else:
            print("   ❌ Sepete gidilemedi")
        
        print(f"\n✅ {name} TESTİ TAMAMLANDI!")
        
    except Exception as e:
        print(f"\n❌ Test Hatası: {str(e)[:100]}")
        results["error"] = str(e)[:200]
    
    finally:
        results["duration"] = round(time.time() - start_time, 2)
        driver.quit()
        
        # Rapor
        try:
            reporter.generate_report()
        except:
            pass
    
    return results

def main():
    print("\n" + "="*70)
    print("🌐 MEGA MULTI-SITE AI MODEL PERFORMANCE TEST")
    print("="*70)
    print(f"📅 Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Test Edilecek Site Sayısı: {len(SITES)}")
    print("="*70)
    
    all_results = []
    
    for i, site in enumerate(SITES, 1):
        print(f"\n\n{'#'*70}")
        print(f"# TEST {i}/{len(SITES)}: {site['name']}")
        print(f"{'#'*70}")
        
        result = test_site(site)
        all_results.append(result)
        
        # Kısa özet
        success_count = sum([result["search"], result["product_select"], result["add_to_cart"], result["cart"]])
        success_rate = (success_count / 4) * 100
        status = "✅" if success_rate >= 50 else "❌"
        print(f"\n{status} {site['name']}: {success_rate:.0f}% ({success_count}/4 adım)")
        
        # Testler arası bekleme
        if i < len(SITES):
            print("\n⏳ Bir sonraki test için 5 saniye bekleniyor...")
            time.sleep(5)
    
    # GENEL ÖZET
    print("\n\n" + "="*70)
    print("📊 MEGA TEST GENEL ÖZETİ")
    print("="*70)
    
    total_sites = len(all_results)
    
    # İstatistikler
    search_success = sum(1 for r in all_results if r["search"])
    product_success = sum(1 for r in all_results if r["product_select"])
    cart_add_success = sum(1 for r in all_results if r["add_to_cart"])
    cart_success = sum(1 for r in all_results if r["cart"])
    
    total_steps = total_sites * 4
    successful_steps = search_success + product_success + cart_add_success + cart_success
    overall_success = (successful_steps / total_steps) * 100
    
    print(f"\n📈 GENEL BAŞARI: {overall_success:.1f}%")
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
    
    # JSON rapor
    report_file = f"mega_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_sites": total_sites,
            "overall_success_rate": overall_success,
            "step_success": {
                "search": search_success,
                "product_select": product_success,
                "add_to_cart": cart_add_success,
                "cart": cart_success
            },
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detaylı rapor: {report_file}")
    print("="*70)
    
    return overall_success

if __name__ == "__main__":
    success_rate = main()
    print(f"\n🎯 Test tamamlandı! Genel başarı: {success_rate:.1f}%")
