# multi_site_test.py
"""
🌐 MULTI-SITE AI TEST RUNNER
N11, Trendyol, Hepsiburada - Tüm sitelerde modeli test et
"""

import subprocess
import time
from datetime import datetime
import json

def run_test(test_file, site_name):
    """Tek bir test çalıştır"""
    print(f"\n{'='*70}")
    print(f"🚀 {site_name} Testi Başlatılıyor...")
    print(f"{'='*70}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["python", test_file],
            capture_output=True,
            text=True,
            encoding='utf-8',  # UTF-8 encoding
            errors='replace',  # Decode hatalarını ignore et
            timeout=300  # 5 dakika timeout
        )
        
        duration = time.time() - start_time
        
        # Başarı kontrolü - çıktıda başarı mesajı var mı?
        output_text = result.stdout if result.stdout else ""
        success = ("✅" in output_text and "TEST TAMAMLANDI" in output_text) or result.returncode == 0
        
        return {
            "site": site_name,
            "success": success,
            "duration": round(duration, 2),
            "output": output_text,
            "error": result.stderr if result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return {
            "site": site_name,
            "success": False,
            "duration": round(duration, 2),
            "error": "TIMEOUT - Test 5 dakikayı aştı"
        }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "site": site_name,
            "success": False,
            "duration": round(duration, 2),
            "error": str(e)
        }

def main():
    print("\n" + "="*70)
    print("🌐 MULTI-SITE AI MODEL PERFORMANCE TEST")
    print("="*70)
    print(f"📅 Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Test senaryoları
    tests = [
        ("full_shopping_scenario.py", "N11"),
        ("trendyol_test.py", "Trendyol"),
        ("hepsiburada_test.py", "Hepsiburada")
    ]
    
    results = []
    
    # Her testi çalıştır
    for test_file, site_name in tests:
        result = run_test(test_file, site_name)
        results.append(result)
        
        # Kısa özet
        status = "✅ BAŞARILI" if result["success"] else "❌ BAŞARISIZ"
        print(f"\n{status} - {site_name}: {result['duration']}s")
        
        if result.get("error"):
            print(f"   ⚠️ Hata: {result['error'][:100]}")
        
        # Testler arası bekleme
        time.sleep(5)
    
    # GENEL ÖZET
    print("\n" + "="*70)
    print("📊 GENEL ÖZET")
    print("="*70)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"\n📈 Toplam Test: {total_tests}")
    print(f"✅ Başarılı: {successful_tests}")
    print(f"❌ Başarısız: {total_tests - successful_tests}")
    print(f"🎯 Başarı Oranı: {success_rate:.1f}%")
    
    print("\n📋 Detaylı Sonuçlar:")
    for r in results:
        status_icon = "✅" if r["success"] else "❌"
        print(f"   {status_icon} {r['site']:15s} - {r['duration']:6.2f}s")
    
    # JSON rapor kaydet
    report_file = f"multi_site_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "successful": successful_tests,
            "success_rate": success_rate,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detaylı rapor kaydedildi: {report_file}")
    print("="*70)
    
    return success_rate

if __name__ == "__main__":
    success_rate = main()
    
    # Exit code
    if success_rate == 100:
        exit(0)  # Tüm testler başarılı
    elif success_rate >= 50:
        exit(1)  # Bazıları başarılı
    else:
        exit(2)  # Çoğu başarısız
